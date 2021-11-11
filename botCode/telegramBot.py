import telebot
from telebot import types
from telebot.apihelper import answer_callback_query
from databaseHandling import DatabaseHandler
import strings
import logging

logging.basicConfig(format="%(levelname)s @ %(asctime)s -> %(message)s", level=logging.DEBUG, handlers=[logging.FileHandler("./logs/bot.log"), logging.StreamHandler()])

token = open("token.txt").read()

bot = telebot.TeleBot(token, parse_mode=None)

database = DatabaseHandler()

awaitingAdd = []
awaitingRemove = []

entryMarkup = types.InlineKeyboardMarkup(row_width = 1)
bt1 = types.InlineKeyboardButton(strings.seeAllReposMessage, callback_data = 1)
bt2 = types.InlineKeyboardButton(strings.addRepoMessage, callback_data = 2)
bt3 = types.InlineKeyboardButton(strings.removeRepoMessage, callback_data = 3)
entryMarkup.add(bt1, bt2, bt3)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, strings.welcomeMessage, reply_markup = entryMarkup)

@bot.message_handler()
def process_message(message):
    if message.chat.id in awaitingAdd:
        result = database.addRepo(message.chat.id, message.text)
        if result == "Exists":
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
            markup.add(button)
            bot.send_message(message.chat.id, strings.repoExistsMessage, reply_markup = markup)
        elif result == "Invalid":
            bot.send_message(message.chat.id, strings.repoInvalidFormatMessage)
        else:
            markup = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton(strings.repoAddedYes, callback_data = 2)
            no = types.InlineKeyboardButton(strings.repoAddedNo, callback_data = 101)
            markup.add(yes, no)
            bot.send_message(message.chat.id, strings.repoAdded, reply_markup = markup)
    elif message.chat.id in awaitingRemove:
        pass
    else:
        bot.send_message(message.chat.id, strings.noSenseMessage, reply_markup = entryMarkup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    if(call.data == "1"): # see all repos
        repoList = database.getRepos(call.message.chat.id)
        if len(repoList) != 0:
            logging.debug(f"Not empty! {repoList}")
            markup = types.InlineKeyboardMarkup(row_width=2)
            for entry in repoList:
                # TODO: use the damn dataclass!
                btn1 = types.InlineKeyboardButton(entry[0], url=entry[2])
                btn2 = types.InlineKeyboardButton(entry[1], url=entry[2] + "/releases/" + entry[1])
                markup.add(btn1,btn2)
            button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
            markup.add(button)
            bot.edit_message_text(strings.showingReposMessage, call.message.chat.id, call.message.id, reply_markup = markup)
        else:
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
            markup.add(button)
            bot.edit_message_text(strings.noReposFoundMessage, call.message.chat.id, call.message.message_id, reply_markup = markup)
        # show all
    elif(call.data == "2"): # add repo
        # get link
        # insert into database
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(strings.returnMessage, callback_data = 101)
        markup.add(button)
        bot.edit_message_text(strings.sendLinkToRepoMessage, call.message.chat.id, call.message.message_id, reply_markup = markup)
        awaitingAdd.append(call.message.chat.id)
    elif(call.data == "3"): # remove a repo
        # query database
        # show all
        # select which
        # remove from database
        pass
    elif(call.data == "101"): # nevermind
        bot.edit_message_text(strings.welcomeMessage, call.message.chat.id, call.message.message_id, reply_markup = entryMarkup)

        if call.message.chat.id in awaitingAdd:
            awaitingAdd.remove(call.message.chat.id)
        if call.message.chat.id in awaitingRemove:
            awaitingRemove.remove(call.message.chat.id)

    answer_callback_query(token, callback_query_id = call.id)

bot.infinity_polling()
