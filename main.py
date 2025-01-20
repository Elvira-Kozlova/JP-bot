import telebot
import random
import time
import os
from dotenv import load_dotenv
from dictionary_kana_kanji import romaji_katakana, romaji_hiragana, noryoku, noryoku_translate


load_dotenv()


TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("Bot token is not defined. Check your .env file.")

bot = telebot.TeleBot(TOKEN)


user_states = {}
user_data = {}
cooldown_time = 3 # Время ожидания между действиями в секундах



@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'katakana': {'questions': list(romaji_katakana.keys()), 'current': None},
                                  'hiragana': {'questions': list(romaji_hiragana.keys()), 'current': None},
                                  'kanji': {'questions': list(noryoku.keys()),'current': None},
                                  'kanji_translate':{'questions': list(noryoku_translate.keys()), 'current': None},
                                  'stats': {'correct': 0, 'total': 0}  # Статистика для подсчёта
                                }
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Хирагана'))
    keyboard.add(telebot.types.KeyboardButton('Катакана'))
    keyboard.add(telebot.types.KeyboardButton('Кандзи N5-N4'))

    welcome_message = (
        "👋 こんにちは! \n\n"
        "Позволь представиться. Я - бот-сенсей, и я предназначен для проверки знаний каны и кандзи.\n\n"
        "Пока что мои возможности не так совершенны, но создатели сказали, что вскоре буду самым крутым ботом! "
        "Поэтому они велели мне тебе передать, чтобы ты проявил терпение!☝️\n\n"
        "Так-с, что-то я заболтался... Давай приступим!\n\n"
        "📝 Выбери, что хочешь проверить: хирагану, катакану или кандзи.\n\n"
        "👷‍♂️👷‍♀️ Кстати! Если ты заметил какую-то неточность или я начал хандрить, или просто желаешь поблагодарить - "
        "ты всегда можешь обратиться к моим создателям (один из которых указан у меня в описании) и они среагируют."
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def check(message):
    # Проверка на спам
    current_time = time.time()
    last_action_time = user_states.get(message.chat.id, {}).get('last_action_time', 0)

    if current_time - last_action_time < cooldown_time:
        bot.send_message(message.chat.id, "Пожалуйста, подожди несколько секунд перед тем, как нажать на кнопку.")
        return

    # Обновляем время последнего действия
    user_states[message.chat.id] = {'last_action_time': current_time}


    if message.text == 'Главное меню':
        main_menu(message)
        return


    if message.text == 'Хирагана':
        check_hiragana(message)
    elif message.text == 'Катакана':
        check_katakana(message)
    elif message.text == 'Кандзи N5-N4':
        check_kanji(message)
    elif message.text == 'Назад':
        back_to_start(message)
    elif (message.text in romaji_katakana.values() or
          message.text in romaji_hiragana.values() or
          message.text in noryoku.values() or
          message.text in noryoku_translate.values()): 
        check_answer(message)
    else:
        bot.send_message(message.chat.id, 'Ты ничего не выбрал. ')


def back_to_start(message):
    # Сбросить текущее состояние вопросов
    user_data[message.chat.id]['katakana']['current'] = None
    user_data[message.chat.id]['hiragana']['current'] = None
    user_data[message.chat.id]['kanji']['current'] = None
    user_data[message.chat.id]['kanji_check'] = None  # Сбросить выбор между чтением и значением 

    # Сброс статистики
    user_data[message.chat.id]['stats'] = {'correct': 0, 'total': 0}

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Хирагана'))
    keyboard.add(telebot.types.KeyboardButton('Катакана'))
    keyboard.add(telebot.types.KeyboardButton('Кандзи N5-N4'))
    bot.send_message(message.chat.id, 'Что будем проверять?', reply_markup=keyboard)


def check_answer(message):
    correct_symbol = None
    correct_reading = None
    correct_meaning = None  # Инициализация для значений кандзи


    # Проверка для катаканы, хираганы и кандзи
    if user_data[message.chat.id]['katakana']['current']:
        correct_symbol = user_data[message.chat.id]['katakana']['current']
        correct_reading = romaji_katakana[correct_symbol]
    elif user_data[message.chat.id]['hiragana']['current']:
        correct_symbol = user_data[message.chat.id]['hiragana']['current']
        correct_reading = romaji_hiragana[correct_symbol]
    elif user_data[message.chat.id]['kanji']['current']:
        correct_symbol = user_data[message.chat.id]['kanji']['current']
        if user_data[message.chat.id]['kanji_check'] == 'reading':
            correct_reading = noryoku[correct_symbol]
        elif user_data[message.chat.id]['kanji_check'] == 'meaning':
            correct_meaning = noryoku_translate[correct_symbol]


    # Обновление общего числа попыток
    user_data[message.chat.id]['stats']['total'] += 1

    # Проверка ответа
    if correct_reading and message.text.strip().lower() == correct_reading.strip().lower():
        user_data[message.chat.id]['stats']['correct'] += 1  # Обновление правильных ответов
        bot.send_message(message.chat.id, 'Верно!')
    elif correct_meaning and message.text.strip().lower() == correct_meaning.strip().lower():
        user_data[message.chat.id]['stats']['correct'] += 1  # Обновление правильных ответов
        bot.send_message(message.chat.id, 'Верно!')
    else:
        if correct_reading:
            bot.send_message(message.chat.id, f'Неправильно! Правильный ответ: {correct_reading}')
        elif correct_meaning:
            bot.send_message(message.chat.id, f'Неправильно! Правильный ответ: {correct_meaning}')


    # Показ статистики пользователю
    stats = user_data[message.chat.id]['stats']
    bot.send_message(
        message.chat.id,
        f"📊 Твоя статистика: {stats['correct']} правильных ответов из {stats['total']}."
    )


    # Перемещение к следующему вопросу
    if user_data[message.chat.id]['katakana']['current']:
        check_katakana(message)
    elif user_data[message.chat.id]['hiragana']['current']:
        check_hiragana(message)
    elif user_data[message.chat.id]['kanji']['current']:
        if user_data[message.chat.id]['kanji_check'] == 'reading':
            check_kanji_reading(message)
        elif user_data[message.chat.id]['kanji_check'] == 'meaning':
            check_kanji_meaning(message)


def check_katakana(message):
    questions = user_data[message.chat.id]['katakana']['questions']
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    if not questions:
        keyboard.add(telebot.types.KeyboardButton('Главное меню'))
        bot.send_message(message.chat.id, 'Поздравляю! Ты прошёл все слоги катаканы!', reply_markup=keyboard)
        back_to_start(message)
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
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        romaji_option = romaji_katakana[option]
        keyboard.add(telebot.types.KeyboardButton(romaji_option))
    keyboard.add(telebot.types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, f"{current_question} – какой это слог?", reply_markup=keyboard)


def check_hiragana(message):
    questions = user_data[message.chat.id]['hiragana']['questions']
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    if not questions:
        keyboard.add(telebot.types.KeyboardButton('Главное меню'))
        bot.send_message(message.chat.id, 'Поздравляю! Ты прошёл все слоги хираганы!', reply_markup=keyboard)
        back_to_start(message)
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
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        romaji_option = romaji_hiragana[option]
        keyboard.add(telebot.types.KeyboardButton(romaji_option))

    keyboard.add(telebot.types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, f"{current_question} – какой это слог?", reply_markup=keyboard)


def check_kanji(message):
    # Показываем меню выбора чтения или значения
    kanji_menu(message)


def kanji_menu(message):
    # Создаём кнопки для выбора проверки
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    reading_button = telebot.types.KeyboardButton('Чтение')
    meaning_button = telebot.types.KeyboardButton('Значение')
    markup.add(reading_button, meaning_button)

    bot.send_message(message.chat.id, "Что будем проверять: чтение или значение?", reply_markup=markup)
    bot.register_next_step_handler(message, kanji_check_selection)


def kanji_check_selection(message):
    # Проверяем выбор пользователя и сохраняем его выбор
    if message.text == 'Чтение':
        user_data[message.chat.id]['kanji_check'] = 'reading'
        bot.send_message(message.chat.id, 'Ты выбрал проверку чтений кандзи.')
        check_kanji_reading(message)  # Начинаем проверку чтений кандзи
    elif message.text == 'Значение':
        user_data[message.chat.id]['kanji_check'] = 'meaning'
        bot.send_message(message.chat.id, 'Ты выбрал проверку значений кандзи.')
        check_kanji_meaning(message)  # Начинаем проверку значений кандзи
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выбери чтение или значение.')
        kanji_menu(message)


def check_kanji_reading(message):
    questions = user_data[message.chat.id]['kanji']['questions']
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Если список вопросов пуст, сообщаем об этом
    if not questions:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Главное меню'))
        bot.send_message(message.chat.id, 'Поздравляю! Ты прошёл все кандзи!', reply_markup=keyboard)
        back_to_start(message)
        return

    # Выбираем текущий вопрос и сохраняем его в user_data
    current_question = random.choice(questions)
    user_data[message.chat.id]['kanji']['current'] = current_question
    user_data[message.chat.id]['kanji']['questions'].remove(current_question)

    # Продолжаем с кнопками
    options = [current_question]
    for _ in range(3):
        option = random.choice(list(noryoku.keys()))
        while option in options:
            option = random.choice(list(noryoku.keys()))
        options.append(option)
    random.shuffle(options)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        kanji_option = noryoku[option]  # Преобразуем символы кандзи в чтения (кунъёми и онъёми)
        keyboard.add(telebot.types.KeyboardButton(kanji_option))

    keyboard.add(telebot.types.KeyboardButton('Назад'))

    # Отправляем вопрос пользователю
    bot.send_message(message.chat.id, f"{current_question} – как читается этот кандзи?", reply_markup=keyboard)



def check_kanji_meaning(message):
    questions = user_data[message.chat.id]['kanji']['questions']
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    if not questions:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Главное меню'))
        bot.send_message(message.chat.id, 'Поздравляю! Ты прошёл все кандзи!', reply_markup=keyboard)
        back_to_start(message)
        return

    current_question = random.choice(questions)
    user_data[message.chat.id]['kanji']['current'] = current_question
    user_data[message.chat.id]['kanji']['questions'].remove(current_question)

    options = [current_question]
    for _ in range(3):
        option = random.choice(list(noryoku_translate.keys()))
        while option in options:
            option = random.choice(list(noryoku_translate.keys()))
        options.append(option)
    random.shuffle(options)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        meaning_option = noryoku_translate[option]  # Преобразуем кандзи в его значение
        keyboard.add(telebot.types.KeyboardButton(meaning_option))
    keyboard.add(telebot.types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, f"{current_question} – что означает этот кандзи?", reply_markup=keyboard)



@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def main_menu(message):
    back_to_start(message)


while True:
    try:
        bot.polling(non_stop=True, timeout=160, long_polling_timeout=160)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(5)

