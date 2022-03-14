# Basic Github Releases - Telegram Bot
This is a Telegram bot that monitors the releases of given repos, sending messages upon a new release. It uses Docker for virtualization, and is based on [eternnoir's Telegram bot API](https://github.com/eternnoir/pyTelegramBotAPI).

Interact with the bot [here](https://t.me/prgitrelbot) (If it is online. Hosting is expensive.)

## Running it on your machine
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
- It will give you an API token. Put it in a text file called **_token.txt_**. Create it in the **_botCode_** directory.

### Deploying
In the parent folder, run 
```
docker-compose up
```
To interact with the bot, BotFather should have given you a link to it.
