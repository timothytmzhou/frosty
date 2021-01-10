from src.config import PROFILE
from src.commands import client


def main():
    client.run(PROFILE["bot_token"])


if __name__ == "__main__":
    main()
