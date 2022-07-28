import time
import telebot
import strings
import logging
import threading
import requests
import os
import yaml
from databaseHandling.prototype import DatabaseHandler, dbEntryUpdate
from databaseHandling.mysql import MySQLHandler
from databaseHandling.pickledb import PickleDBHandler
from databaseHandling.dynamodb import DynamoDBHandler
from telebot import types
from telebot.apihelper import answer_callback_query
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if not os.path.exists(os.getcwd() + "/logs"):
    os.mkdir(os.getcwd() + "/logs")

if not os.path.isfile(os.getcwd() + "/logs" + "/bot.log"):
    file = open("logs/bot.log", "w")
    file.close()
    
if not os.path.isfile(os.getcwd() + "/logs" + "/databaseHandling.log"):
    file = open("logs/databaseHandling.log", "w")
    file.close()

logging.basicConfig(format="%(levelname)s @ %(asctime)s -> %(message)s", level=logging.WARNING, handlers=[logging.FileHandler("./logs/bot.log"), logging.StreamHandler()])

# Initialization

token = ""
databaseType = ""
sleepTime = 3600
databaseHandler = DatabaseHandler()

try:
    with open("config.yaml") as configFile:
        configData = yaml.load(configFile, Loader=yaml.FullLoader)
        token = configData["token"]
        sleepTime = configData["sleepTime"]
        databaseType = configData["databaseType"]
        match databaseType:
            case "mysql":
                databaseHandler = MySQLHandler()
            case "pickledb":
                databaseHandler = PickleDBHandler(configData["databaseFile"])
            case "dynamodb":
                databaseHandler = DynamoDBHandler(configData["tableName"])
except Exception as exc:
    logging.error("Failed to open config file. Loading config from env vars")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token == None:
        raise "No TELEGRAM_BOT_TOKEN set!"
    sleepTime = os.getenv("TELEGRAM_BOT_SLEEP_TIME")
    if sleepTime == None:
        raise "No TELEGRAM_BOT_SLEEP_TIME set!"
    databaseType = os.getenv("TELEGRAM_BOT_DATABASE_TYPE")
    if databaseType == None:
        raise "No TELEGRAM_BOT_DATABASE_TYPE set!"
    match databaseType:
        case "mysql":
            databaseHandler = MySQLHandler()
        case "pickledb":
            dbFileName = os.getenv("TELEGRAM_BOT_DATABASE_FILE")
            if dbFileName == None:
                raise "No TELEGRAM_BOT_DATABASE_FILE set!"
            databaseHandler = PickleDBHandler(dbFileName)
        case "dynamodb":
            tableName = os.getenv("TELEGRAM_BOT_DATABASE_TABLE_NAME")
            if tableName == None:
                raise "No TELEGRAM_BOT_DATABASE_TABLE_NAME set!"
            databaseHandler = DynamoDBHandler(tableName)
            if os.getenv("AWS_ACCESS_KEY_ID") == None:
                raise "No AWS_ACCESS_KEY_ID set!"
            if os.getenv("AWS_SECRET_ACCESS_KEY") == None:
                raise "No AWS_SECRET_ACCESS_KEY set!"
            if os.getenv("AWS_DEFAULT_REGION") == None:
                raise "No AWS_DEFAULT_REGION set!"

bot = telebot.TeleBot(token, parse_mode=None)

awaitingAdd = []

entryMarkup = types.InlineKeyboardMarkup(row_width = 1)
bt1 = types.InlineKeyboardButton(strings.seeAllReposMessage, callback_data = 1)
bt2 = types.InlineKeyboardButton(strings.addRepoMessage, callback_data = 2)
entryMarkup.add(bt1, bt2)

# Message handler functions

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, strings.welcomeMessage, reply_markup = entryMarkup)

@bot.message_handler()
def process_message(message):
    if message.chat.id in awaitingAdd:
        result = databaseHandler.addRepo(message.chat.id, message.text)
        match result:
            case "Exists":
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
                markup.add(button)
                bot.send_message(message.chat.id, strings.repoExistsMessage, reply_markup = markup)
            case "Invalid":
                bot.send_message(message.chat.id, strings.repoInvalidFormatMessage)
            case "Error":
                bot.send_message(message.chat.id, strings.repoAddError)
            case _:
                markup = types.InlineKeyboardMarkup()
                yes = types.InlineKeyboardButton(strings.repoAddedYes, callback_data = 2)
                no = types.InlineKeyboardButton(strings.repoAddedNo, callback_data = 101)
                markup.add(yes, no)
                bot.send_message(message.chat.id, strings.repoAdded, reply_markup = markup)
    else:
        bot.send_message(message.chat.id, strings.noSenseMessage, reply_markup = entryMarkup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    match call.data:
        case "1": # see all repos
            repoList = databaseHandler.getRepos(call.message.chat.id)
            if len(repoList) != 0:
                markup = types.InlineKeyboardMarkup(row_width=3)
                for entry in repoList:
                    btn1 = types.InlineKeyboardButton(entry.repoName, url=entry.repoLink)
                    btn2 = types.InlineKeyboardButton(entry.currentReleaseTagName, url=entry.repoLink + "/releases/" + entry.currentReleaseTagName)
                    btn3 = types.InlineKeyboardButton(strings.delteRepoEmoji, callback_data=entry.nameHash)
                    markup.add(btn1, btn2, btn3)
                button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
                markup.add(button)
                bot.edit_message_text(strings.showingReposMessage, call.message.chat.id, call.message.id, reply_markup = markup)
            else:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
                markup.add(button)
                bot.edit_message_text(strings.noReposFoundMessage, call.message.chat.id, call.message.message_id, reply_markup = markup)
            # show all
        case "2": # add repo
        # get link
        # insert into database
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
            markup.add(button)
            bot.edit_message_text(strings.sendLinkToRepoMessage, call.message.chat.id, call.message.message_id, reply_markup = markup)
            awaitingAdd.append(call.message.chat.id)
        case "101": # nevermind
            bot.edit_message_text(strings.welcomeMessage, call.message.chat.id, call.message.message_id, reply_markup = entryMarkup)

            if call.message.chat.id in awaitingAdd:
                awaitingAdd.remove(call.message.chat.id)
        case _: # called back with md5 hash, delete from dbase
            databaseHandler.removeRepo(call.message.chat.id, call.data)
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(strings.refreshListMessage, callback_data = 1)
            markup.add(button)
            bot.edit_message_text(strings.deletedRepoMessage, call.message.chat.id, call.message.message_id, reply_markup = markup)

    answer_callback_query(token, callback_query_id = call.id)

def notifier():
    while True:
        allEntries = databaseHandler.dbDump()
        logging.debug(allEntries)
        updateCommands = []
        for entry in allEntries:
            response = requests.get(f"https://api.github.com/repos/{entry.repoOwner}/{entry.repoName}/releases")
            assert response.status_code == 200
            releaseTag = response.json()[0]["tag_name"]
            if releaseTag != entry.currentReleaseTagName:
                markup = types.InlineKeyboardMarkup(row_width = 2)
                button1 = types.InlineKeyboardButton(entry.repoName, url = entry.repoLink)
                button2 = types.InlineKeyboardButton(releaseTag, url = entry.repoLink + "/releases/" + releaseTag)
                markup.add(button1, button2)
                bot.send_message(entry.chatID, strings.newReleaseFoundMessage, reply_markup = markup)
                updateEntry = dbEntryUpdate(
                    chatID = entry.chatID,
                    nameHash = entry.nameHash,
                    newTag = releaseTag
                )
                updateCommands.append(updateEntry)
        databaseHandler.updateEntries(updateCommands)
        time.sleep(int(sleepTime))

# Starting the bot
th = threading.Thread(target=notifier)
logging.debug("Starting notifier")
th.start()

bot.infinity_polling(timeout=60)
