from src.config import PROFILE
from src.commands import client
import src.info


def main():
    client.run(PROFILE["bot_token"])


if __name__ == "__main__":
    main()
