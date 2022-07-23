# Basic Github Releases - Telegram Bot
This is a Telegram bot that monitors the releases of given repos, sending messages upon a new release. It uses Docker for virtualization, and is based on [eternnoir's Telegram bot API](https://github.com/eternnoir/pyTelegramBotAPI).

Interact with the bot [here](https://t.me/prgitrelbot) (If it is online. Hosting is expensive.)

## Running it yourself
So the bot is offline but you still want to try it? I admire you. Here's how to do it:

### Prerequisites

Have Docker installed, docker-compose is also necessary.

### Getting the files
Either download the code as zip from Github (make sure to unzip it), or clone the repo locally:
```
git clone https://github.com/chofnar/BasicGithubReleasesTelegramBot
```
### Getting an API Token from Telegram
- Talk to the [BotFather](https://t.me/botfather) to create a bot. It's one of the [official bots of Telegram](https://core.telegram.org/bots#6-botfather)
- It will give you an API token. Put it in a text file called **_config.txt_**. Create it in the main directory.
- On the 2nd line of the **_config.txt_** file, put one of the supported database types. They (might) need additional config.

## Supported database types
The bot can use the following database types to store the relevant info. Click on the links attached to see whether or not they need additional config.
- **MySQL**
- **PickleDB** - on the 3rd line of the config file, specify the database file name

### Deploying
In the parent folder, run 
```
docker-compose up
```
To interact with the bot, BotFather should have given you a link to it.
