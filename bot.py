import telebot
from telebot import types
import sqlite3
from random import randint
import markovify
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()

bot = telebot.TeleBot('мой токен')



# Сразу обучим мини модельку для генерирования----------------------------------------

con = sqlite3.connect('le_petit_db_save_me.db') # пока на другой (не тот и не та)
cur = con.cursor()
comedy_query = """
SELECT anecs.id, anecs.text FROM anecs
"""
cur.execute(comedy_query, )
longlist = cur.fetchall()
longlist[0]
all_anecs = ""
for i in longlist:
    all_anecs += i[1]
    all_anecs += " "

pop_rikolu_model = markovify.Text(all_anecs)

# Сразу же соберём названия тегов -------------------------------------
# (не придумала причины хранить их отдельно в джэйсоне)

con = sqlite3.connect('le_petit_db_save_me.db') # пока на другой (не тот и не та)
cur = con.cursor()
tag_query = """
SELECT tag, id_tag FROM tags
"""
cur.execute(tag_query, )
we_have_tags = dict(cur.fetchall())


# Тут функция обработки ----------------------------------------

def take_tag(word):
    word = word.strip(' ')
    normal_word = morph.parse(word)[0].normal_form
    if normal_word in we_have_tags:
        division = normal_word
    else:
        division = "Ой, у нас нет такого тэга ;( \n Попробуйте другой!"
    return division


# команды бота-----------------------------------------------------------------

@bot.message_handler(commands=['start'])
def starter(message):
    bot.send_message(message.from_user.id, "Тут очень длинное и красивое описание\
                                           но я явно его еще поменяю..",
                     parse_mode='Markdown')
    chat_id = message.chat.id


@bot.message_handler(commands=['help'])
def starter(message):
    bot.send_message(message.from_user.id, "Тут очень длинное и красивое описание\
                                           но я явно его еще поменяю..",
                     parse_mode='Markdown')
    chat_id = message.chat.id


@bot.message_handler(commands=['menu'])
def menu(message):
    start_menu = types.ReplyKeyboardMarkup(True, True)
    start_menu.row('Random 🐇')
    start_menu.row('Чудо технологий 🐓')
    start_menu.row('Анекдот с персонажем🚶‍♂')
    start_menu.row('Свой анекдот (в разработке)')
    bot.send_message(message.chat.id, 'Вы попали в Стартовое меню', \
                     reply_markup=start_menu)

#  наконец текстовое взаимодействие с ботом

@bot.message_handler(content_types=['text'])
def after_first_message(message):
    if message.text == 'Анекдот с персонажем🚶‍♂' or message.text == "Попробовать ещё.." or message.text == "Анекдот с другим персонажем":
#        msg = bot.send_message(message.from_user.id, 'Введите номер телефона: ', reply_markup = start_menu)
        msg = bot.send_message(message.from_user.id, 'Введите персонажа или топик, про которого хитите анекдот')
        bot.register_next_step_handler(msg, after_second_message)

    elif "Random" in message.text:
        string_of = "🐓🦢🕊🐇🐁🐑☁️🍚💭🕸😍🎢💅🏻❤️‍🔥🤤👙🪡🥼🦋🦟🍘" # Ой, как прикольно, они меняются
        a = randint(0, len(string_of)-1)
        b = randint(0, len(string_of)-1)
        c = randint(0, len(string_of)-1)
        text_random = "Ещё Random " + string_of[a] + string_of[b] + string_of[c]
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row(text_random)
        start_menu.row('✨чудо✨ технологий ')
        start_menu.row('Анекдот с персонажем🚶‍♂')
        start_menu.row('Свой анекдот (в разработке)')
        conn = sqlite3.connect('le_petit_db_save_me.db', check_same_thread=False)
        cur = conn.cursor()
        comedy_query = """
        	SELECT *
        	FROM anecs
        	"""
        cur.execute(comedy_query)
        b = cur.fetchall()

        def solve():
            a = randint(0, 5960)
            if len(b[a]) > 1:
                text = str(b[a][1])
                bot.send_message(message.chat.id, text, reply_markup=start_menu)
            else:
                solve()
        solve()

    elif message.text == "✨чудо✨ технологий" or message.text == "Ещё ✨чудо✨ технологий":
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row('Random 🐇')
        start_menu.row('Ещё ✨чудо✨ технологий')
        start_menu.row('Анекдот с персонажем🚶‍♂')
        start_menu.row('Свой анекдот (в разработке)')
        text_for_sending = pop_rikolu_model.make_sentence()
        bot.send_message(message.chat.id, text_for_sending, reply_markup=start_menu)

    elif message.text == "Назад в меню":
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row('Random 🐇')
        start_menu.row('✨чудо✨ технологий')
        start_menu.row('Анекдот с персонажем🚶‍♂')
        start_menu.row('Свой анекдот (в разработке)')
        bot.send_message(message.chat.id, 'Вы вурнулись в Стартовое меню', \
                         reply_markup=start_menu)

def after_second_message(message):
    textc = take_tag(message.text)
    if textc == "Ой, у нас нет такого тэга ;( \n Попробуйте другой!":
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row('Попробовать ещё..')
        start_menu.row('Назад в меню')
        bot.send_message(message.chat.id, textc, reply_markup=start_menu)
    else:
        number_of_tag = str(we_have_tags[textc])
        final_query = """
        SELECT text FROM anecs
        JOIN text_to_tag ON anecs.id = text_to_tag.id_anec
        JOIN tags ON text_to_tag.id_tag = tags.id_tag
        WHERE tags.id_tag == """ + number_of_tag
        con = sqlite3.connect('le_petit_db_save_me.db')  # (не тот и не та)
        cur = con.cursor()
        cur.execute(final_query)
        longlist = cur.fetchall()
        a = randint(0, len(longlist) - 1)
        anec = longlist[a][0]
        start_menu = types.ReplyKeyboardMarkup(True, True)
#        start_menu.row('Анекдот с этим же персонажем🚶‍♂')
        start_menu.row('Анекдот с другим персонажем')
        start_menu.row('Назад в меню')
        bot.send_message(message.from_user.id, anec, reply_markup=start_menu)




# чтобы бот реагировал на сообщения--------------------------------------------
bot.polling(none_stop=True, interval=0) 
