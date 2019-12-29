# -*- coding: utf-8 -*-
# !/usr/bin/env python
import telebot
from telebot import apihelper, types, util
import re
import time
import requestsss
import warnings
import datetime

datte = [-373309006, 634060742, 656065530]
warnings.filterwarnings(action='ignore', module='.*paramiko.*')
bot = telebot.TeleBot('*************************************')
running_bs = []


@bot.message_handler(content_types=['text'])
def authentification(message):
    name = message.from_user.first_name
    now = datetime.datetime.now()
    user = message.from_user.username

    def bs_key(bs):
        keyboard = types.InlineKeyboardMarkup()
        index = 1

        if bs == "ast":
            for i in ["edem", "sairan", "grand-alatau", "kmg", "severnoe-siyanie", "evrocentr", "bajkonur", "burlin",
                      "zhenis", "maria", "munar", "samal10", "Сейфулина", "Жагалау"]:
                keyboard.add(types.InlineKeyboardButton(text=i, callback_data=f"ast_{i}_{index}"))
                index += 1

        elif bs == "alm":
            for i in ["edem", "esentai", "brt"]:
                keyboard.add(types.InlineKeyboardButton(text=i, callback_data=f"alm_{i}_{index}"))
                index += 1

        elif bs == "shym":
            for i in ["Европейский", "KazTransKom"]:
                keyboard.add(types.InlineKeyboardButton(text=i, callback_data=f"shym_{i}_{index}"))
                index += 1

        elif bs == "ukk":
            for i in ["Kaztel-kolokeyshin", "Абая 1", "Adicom"]:
                keyboard.add(types.InlineKeyboardButton(text=i, callback_data=f"ukk_{i}_{index}"))
                index += 1

        return keyboard

    def keyboard():
        markup = types.ReplyKeyboardRemove(selective=True)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for i in ['/help ast', '/help alm', '/help ukk', '/help shym']:
            btn1 = types.KeyboardButton(i)
            markup.add(btn1)
        return markup

    def get_text_messages(message):
        regex = re.compile("\\d{1,3}\\W\\d{1,3}\\W\\d{1,3}\\W\\d{1,3}")
        Ip = ''.join(regex.findall(message.text))
        regex = re.compile('\"\D{1,3}\d{1,3}\"')
        apk = ''.join(regex.findall(message.text))
        name = message.from_user.first_name
        chat_id = message.chat.id

        if message.text == "123":
            bot.reply_to(message, "Test")

        elif message.text == "/help" or message.text == "/start":
            bot.reply_to(message, "/keyboard or ip")


        elif message.text == "/keyboard":
            text = "Нажмите на кнопку для выбора города"
            bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=keyboard())

        elif apk:
            bot.reply_to(message, requestsss.find_node_in_apk(''.join([i.lstrip('"') for i in apk])))

        elif message.text == "/help ukk":
            bot.send_message(chat_id, "Выберите БС:", parse_mode='HTML', reply_markup=bs_key("ukk"))
        elif message.text == "/help ast":
            bot.send_message(chat_id, "Выберите БС:", parse_mode='HTML', reply_markup=bs_key("ast"))
        elif message.text == "/help alm":
            bot.send_message(chat_id, "Выберите БС:", parse_mode='HTML', reply_markup=bs_key("alm"))
        elif message.text == "/help shym":
            bot.send_message(chat_id, "Выберите БС:", parse_mode='HTML', reply_markup=bs_key("shym"))

        elif message.text == "/exit()":
            print(2 + "2")

        elif requestsss.check_bs(message.text):
            bot.reply_to(message, "В процессе")
            info = requestsss.vot_bi_zarabotalo(message.text)
            if len(info) > 4096:
                for x in range(0, len(info), 4096):
                    bot.send_message(message.chat.id, info[x:x + 4096])
            else:
                bot.reply_to(message, info)

        elif Ip:
            bot.reply_to(message, f"В процессе, @{user}")
            n = requestsss.restart_node(Ip, '')
            if n:
                bot.reply_to(message, n)
            else:
                bot.reply_to(message, f"Выполнено, @{user}")

    global datte

    print(f"{message.from_user.username}:[{message.text}], {message.chat.id}, {message.from_user.id}, ({str(now)})")
    if message.chat.id in datte:
        get_text_messages(message)


@bot.callback_query_handler(func=lambda message: True)
def ans(message):
    global running_bs
    bs_name = message.data.split("_", 2)[1]
    i = message.data.split("_", 2)[2]
    city = message.data.split("_", 2)[0]
    chat_id = message.message.chat.id
    user = message.from_user.username
    if not [i for i in running_bs if f'{bs_name}:{city}' in i]:
        running_bs.append(f'{bs_name}:{city}')
        bot.send_message(chat_id, f"В процессе, @{user}", parse_mode='HTML')
        bot.send_message(chat_id, requestsss.vot_bi_zarabotalo(f"{city}: {i}") + ': ' + bs_name + ', ' + f'@{user}',
                         parse_mode='HTML')
        running_bs.remove(f'{bs_name}:{city}')
    else:
        return bot.send_message(chat_id, f"Бс уже запущенна, @{user} подождите", parse_mode='HTML')


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        time.sleep(90)
