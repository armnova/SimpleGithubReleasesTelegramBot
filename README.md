# Basic Github Releases - Telegram Bot
This is a Telegram bot that monitors the releases of given repos, sending messages upon a new release. It uses Docker for virtualization, and is based on [eternnoir's Telegram bot API](https://github.com/eternnoir/pyTelegramBotAPI).

Interact with the bot [here](https://t.me/prgitrelbot).
It currently checks for new releases every 3 hours.

## Running it yourself
So the bot is offline but you still want to try it? I admire you. Here's how to do it:

### Prerequisites

Have Docker installed. Or not. You can run it directly from the main.py file.

### Getting the files
Either download the code as zip from Github (make sure to unzip it), or clone the repo locally:
```
git clone https://github.com/chofnar/BasicGithubReleasesTelegramBot
```
### Getting an API Token from Telegram
- Talk to the [BotFather](https://t.me/botfather) to create a bot. It's one of the [official bots of Telegram](https://core.telegram.org/bots#6-botfather)
- It will give you an API token. Put it in a text file called **_config.yaml_**, with the field name "**_token_**". Create it in the main directory.
- In the **_config.yaml_** file, put one of the supported database types with the field name "**_databaseType_**". They (might) need additional config.
Check the example config file if you didn't work with yamls yet.

## Supported database types
The bot can use the following database types to store the relevant info. Click on the links attached to see whether or not they need additional config.
- **MySQL**
- **PickleDB** - add databaseFile
- **DynamoDB** - add tableName - **_CURRENTLY THE ONLY ONE WORKING_** - also needs AWS env vars

### Deploying
In the parent folder, run 
```
docker-compose up
```
OR

```
python3 main.py
```
To interact with the bot, BotFather should have given you a link to it.
