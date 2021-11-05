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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton(strings.seeAllReposMessage, callback_data = 1)
    itembtn2 = types.InlineKeyboardButton(strings.addRepoMessage, callback_data = 2)
    itembtn3 = types.InlineKeyboardButton(strings.removeRepoMessage, callback_data = 3)
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, strings.welcomeMessage , reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    if(call.data == "1"): # see all repos
        repoList = database.getRepos(call.message.chat.id)
        if repoList:
            pass
        else:
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(strings.noReposFoundMessage, callback_data = 101)
            markup.add(button)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        # show all
        pass
    elif(call.data == "2"): # add repo
        # get link
        # insert into database
        pass
    elif(call.data == "3"): # remove a repo
        # query database
        # show all
        # select which
        # remove from database
        pass
    elif(call.data == "101"): # nevermind
        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtn1 = types.InlineKeyboardButton(strings.seeAllReposMessage, callback_data = 1)
        itembtn2 = types.InlineKeyboardButton(strings.addRepoMessage, callback_data = 2)
        itembtn3 = types.InlineKeyboardButton(strings.removeRepoMessage, callback_data = 3)
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    answer_callback_query(token, callback_query_id=call.id)

bot.infinity_polling()
