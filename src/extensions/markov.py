import random
from src.commands import *
from src.commands import client

channel_history = []


@subcommand()
async def markov_refresh(ctx, channel, number):
    """
    Reads a channel's message history for generating markov messages.

    :param channel channel: which channel to read from
    :param integer number: how many messages to load (max 10000)
    """

    global channel_history

    refresh_max = 10000
    number = min(number, refresh_max)

    await ctx.channel.send(f"Refreshing {number} most recent messages from {channel}...")
    channel_history = await channel.history(limit=number).flatten()
    await ctx.channel.send(f"Finished refreshing {number} most recent messages from {channel}.")


@subcommand()
async def markov_generate(ctx, user, length, prefix=None):
    """
    Generates an n length message based on a user's message history.

    :param user user: which user
    :param integer length: length of generated message, max 1000
    :param string prefix: optional, prefix for the generated message
    """

    global channel_history
    if len(channel_history) == 0:
        await ctx.channel.send("There is no loaded message history. Try refreshing with ``/markov refresh``.")
        return

    length = min(length, 1000)

    history = get_user_message_history(user)
    if history == '' or history is None:
        await ctx.channel.send('No history found for this user.')
        return

    chain = Chain(history)
    chain.train()
    chain_output = chain.generate(length, prefix)

    msg_send = split_message_text(await filter_text_for_mentions(ctx, chain_output))

    await ctx.channel.send(f'{user} says:\n')
    for part in msg_send:
        await ctx.channel.send(f'{part}')


def split_message_text(text, char_limit=2000):
    return [text[i:i + char_limit] for i in range(0, len(text), char_limit)]


def get_user_message_history(user):
    user_message_history = ''
    for m in channel_history:
        if m.author.id == user.id:
            user_message_history += m.content + ' '
    return user_message_history


async def filter_text_for_mentions(context, text):

    cached_ids = {}

    matches = re.findall('<@.*?>', text)
    for match in matches:
        if match == '@everyone' or match == '@here':
            text = text.replace(match, '``'+match+'``')
        safe_ping = match.replace('@', '@!')
        user_id = match.replace('@', '').replace('<', '').replace('>', '').replace('!', '').replace('&', '')

        if user_id in cached_ids.keys():
            mention_name = cached_ids[user_id]
        else:
            try:
                user = await client.fetch_user(user_id)
                mention_name = user.display_name
            except discord.errors.NotFound:
                mention_name = 'unknown_user'
            cached_ids.update({user_id: mention_name})

        safe_ping = safe_ping.replace(user_id, mention_name)
        text = text.replace(match, safe_ping)
    return text


class Chain:

    def __init__(self, training_data):
        self.training_data = training_data
        self.chain_dict = {}

    def train(self):
        self.create_markov_structure()
        self.calculate_transitions()

    def generate(self, length, prefix):

        generated_text = ''
        words_so_far = 0

        # If there is a prefix, check that the last word in the prefix exists
        if prefix is not None:
            prefix_words = prefix.split()
            starting_word = prefix_words[-1]
            if starting_word not in self.chain_dict:
                return f'User has not said the word {starting_word}, so the Markov chain could not be traversed.'
            else:
                starting_state = self.chain_dict[starting_word]
                generated_text = '**' + prefix[:-len(starting_word)] + '**'
        else:
            starting_state = list(self.chain_dict.values())[random.randrange(0, len(self.chain_dict.keys()))]

        current_state = starting_state

        while words_so_far < length:

            generated_text += current_state.word + ' '
            words_so_far += 1

            dice_roll = random.uniform(0, 1)
            p_sum = 0

            # If we have reached a word in the chain that does not have any transitions, we must break, there is not
            # valid word to jump to. Note: Only happens if this state is the last word in the training_text and has not
            # appeared anywhere else in the text.
            # TODO: jump to random word?
            if len(current_state.transitions) == 0:
                break

            for t in current_state.transitions:
                if dice_roll <= t.probability + p_sum:
                    current_state = t.state
                    break
                else:
                    p_sum += t.probability

        return generated_text

    # Creates Markov Chain Structure but does not calculate state transition probabilities
    def create_markov_structure(self):
        if self.training_data is None:
            print("No training data.")
            return

        words = self.training_data.split()
        if len(words) == 0:
            print("Training data contained no words.")
            return

        for i in range(len(words)):
            w = words[i]
            w_state = self.find_or_create_state(w)  # If w does not exist, create new state w

            # If w is not the last word in the training data
            if i != len(words) - 1:
                n = words[i + 1]
                n_state = self.find_or_create_state(n)

                w_to_n = w_state.get_transition(n)
                if w_to_n is None:
                    w_state.add_new_transition(n_state)
                else:
                    w_to_n.count += 1

    # Calculates the probabilities between state transitions
    def calculate_transitions(self):
        for state in self.chain_dict.values():
            total = 0
            for t in state.transitions:
                total += t.count
            for t in state.transitions:
                t.probability = t.count / total

    # Helper method will return the state object for the word, if it doesn't exist it will create one.
    def find_or_create_state(self, word):
        if word in self.chain_dict:
            w_state = self.chain_dict[word]
        else:
            w_state = ChainState(word)
            self.chain_dict[word] = w_state

        return w_state


class ChainStateTransition:

    def __init__(self, state):
        self.state = state
        self.probability = 0.0
        self.count = 1


class ChainState:

    def __init__(self, word):
        self.word = word
        self.transitions = []

    def add_new_transition(self, state):
        self.transitions.append(ChainStateTransition(state))

    def get_transition(self, word):
        for t in self.transitions:
            if t.state.word == word:
                return t
        return None
