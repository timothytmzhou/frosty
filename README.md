frosty - containerized code execution
====================================
# About
Frosty implements arbitrary code execution for a variety of languages. Type /list or /help for more info.
# Deploying
Clone the repository:
```
git clone https://gitlab.com/TimothyZhou/Frosty/-/tree/ohm/src
```
Install python dependencies:
```
pip install -r requirements.txt
```
Frosty uses per-language docker containers to run code. The docker files in `languages/` can be built using `build.sh`.
```
chmod +x build.sh
./build.sh
```
Run frosty from the root directory of the repo.
`python src/main.py`
On startup, if the needed `config.json` file is not present, frosty will automatically generate one. You will need to provide the following inputs:
- bot_token - discord api bot token

You can also generate this file by running `src/config.py` directly.