import telebot
import random
import time
import os
from dotenv import load_dotenv

# Токен вашего бота
TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)


romaji_katakana = {
    'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o', 'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
    'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so', 'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
    'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no', 'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
    'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo', 'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo', 'ラ': 'ra', 'リ': 'ri',
    'ル': 'ru', 'レ': 're', 'ロ': 'ro', 'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n'
}

romaji_hiragana = {
    'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o', 'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
    'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so', 'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
    'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no', 'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
    'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo', 'や': 'ya', 'ゆ': 'yu', 'よ': 'yo', 'ら': 'ra', 'り': 'ri',
    'る': 'ru', 'れ': 're', 'ろ': 'ro', 'わ': 'wa', 'を': 'wo', 'ん': 'n'
}


user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'katakana': {'questions': list(romaji_katakana.keys()), 'current': None},
                                  'hiragana': {'questions': list(romaji_hiragana.keys()), 'current': None}}
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.add(telebot.types.KeyboardButton('Хирагана'))
    keyboard.add(telebot.types.KeyboardButton('Катакана'))
    bot.send_message(message.chat.id, 'Что будем проверять?', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def check(message):
    if message.text == 'Хирагана':
        check_hiragana(message)
    elif message.text == 'Катакана':
        check_katakana(message)
    elif message.text == 'Назад':
        back_to_start(message)
    elif message.text in romaji_katakana.values() or message.text in romaji_hiragana.values():
        check_answer(message)
    else:
        bot.send_message(message.chat.id, 'Вы ничего не выбрали. ')

def back_to_start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.add(telebot.types.KeyboardButton('Хирагана'))
    keyboard.add(telebot.types.KeyboardButton('Катакана'))
    bot.send_message(message.chat.id, 'Что будем проверять?', reply_markup=keyboard)

def check_answer(message):
    if 'katakana' in user_data[message.chat.id] and user_data[message.chat.id]['katakana']['current']:
        correct_symbol = user_data[message.chat.id]['katakana']['current']
        correct_romaji = romaji_katakana[correct_symbol]
    elif 'hiragana' in user_data[message.chat.id] and user_data[message.chat.id]['hiragana']['current']:
        correct_symbol = user_data[message.chat.id]['hiragana']['current']
        correct_romaji = romaji_hiragana[correct_symbol]
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так.')
        return

    if message.text.strip().lower() == correct_romaji.strip().lower():
        bot.send_message(message.chat.id, 'Верно!')
        if user_data[message.chat.id]['katakana']['current']:
            check_katakana(message)
        elif user_data[message.chat.id]['hiragana']['current']:
            check_hiragana(message)
    else:
        bot.send_message(message.chat.id, 'Неверно!')
        if user_data[message.chat.id]['katakana']['current']:
            check_katakana(message)
        elif user_data[message.chat.id]['hiragana']['current']:
            check_hiragana(message)

def check_katakana(message):
    questions = user_data[message.chat.id]['katakana']['questions']
    if not questions:
        bot.send_message(message.chat.id, 'Поздравляю! Вы прошли все слоги катаканы!')
        return
    current_question = random.choice(questions)
    user_data[message.chat.id]['katakana']['current'] = current_question
    user_data[message.chat.id]['katakana']['questions'].remove(current_question)
    options = [current_question]
    for _ in range(3):
        option = random.choice(list(romaji_katakana.keys()))
        while option in options:
            option = random.choice(list(romaji_katakana.keys()))
        options.append(option)
    random.shuffle(options)
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for option in options:
        romaji_option = romaji_katakana[option]
        keyboard.add(telebot.types.KeyboardButton(romaji_option))
    keyboard.add(telebot.types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, f"{current_question} – какой это слог?", reply_markup=keyboard)

def check_hiragana(message):
    questions = user_data[message.chat.id]['hiragana']['questions']
    if not questions:
        bot.send_message(message.chat.id, 'Поздравляю! Вы прошли все слоги хираганы!')
        return
    current_question = random.choice(questions)
    user_data[message.chat.id]['hiragana']['current'] = current_question
    user_data[message.chat.id]['hiragana']['questions'].remove(current_question)
    options = [current_question]
    for _ in range(3):
        option = random.choice(list(romaji_hiragana.keys()))
        while option in options:
            option = random.choice(list(romaji_hiragana.keys()))
        options.append(option)
    random.shuffle(options)
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for option in options:
        romaji_option = romaji_hiragana[option]
        keyboard.add(telebot.types.KeyboardButton(romaji_option))
    keyboard.add(telebot.types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, f"{current_question} – какой это слог?", reply_markup=keyboard)

while True:
    try:
        bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(5)

