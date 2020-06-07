# ihscy's over-engineered Discord bot
import discord
from src.util import wrap_sync
from src.commands import *

client = discord.Client()


async def process_message(message):
    msg_info = Message_Info(message)
    # Iterates through the commands dict of the form {Trigger: func -> Call}:
    for trigger, func in commands.copy().items():
        if trigger.match(msg_info.content):
            if msg_info.user_level >= trigger.access_level:
                async with message.channel.typing():
                    args = trigger.slice(msg_info.content)
                    # If so, passes the slice into the corresponding function,
                    #     and adds the returned Call object's invoke() method
                    #     to the client loop.
                    task = await wrap_sync(client.loop, func, msg_info, *args)
                    if isinstance(task, Call):
                        client.loop.create_task(task.invoke())
                break


@client.event
async def on_message(message):
    if not message.author.bot:
        try:
            await process_message(message)
        except Exception as e:
            raise e


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("token", help="discord API token")
    args = parser.parse_args()

    # snow_alert = SnowAlertSystem(client)
    # client.loop.create_task(snow_alert.check_bsd())

    client.run(args.token)


if __name__ == "__main__":
    main()
