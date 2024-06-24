from telegram import ForceReply, Update, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.constants import ParseMode
import requests
import json
import os
import ostrovok_api as ostrovok


ALLOWED_USER_IDS = [
    1899008325,
    249484136,
]

QUESTION_INDEX = 0

TOKEN = "6608411270:AAHY6BEDs5rsBSR93WBN5j_lNdUMPqasbV0"
CHAT_IDS_FILE = 'chat_ids.json'

# Define states
AGREE, ASK_NAME, ASK_COMPANY, ASK_POSITION, ASK_EMAIL, CHOOSE_GAME, FAVORITE_LANGUAGE, START_QUIZ, COMMON_QUESTION_1, COMMON_QUESTION_2, COMMON_QUESTION_3, PYTHON_QUIZ, GOLANG_QUIZ, PYTHON_Q3, GOLANG_Q3 = range(15)

PERSONAL_DATA = "Если вы нажимаете 'Я согласен', то вы соглашаетесь с [условиями хранения данных](https://drive.google.com/file/d/18Zs8FaIGkGba1-GiJzqpvaF6ki4Q3V_n/view?usp=sharing)"

intro = 'О, привет! Язык программирования выбран, он поможет пройти квест и получить подарок. Островок отправляет тебя в путешествие в Мерчленд. Но где же он находится?'

final_answer = '''Ты настоящий герой! Подойди на стенд компании Островок и забери свой подарок. Покажи менеджеру свой результат. Тебе еще возвращаться домой, с мерчом это делать намного приятнее)'''

common_questions = [
    ("Чтобы понять в какое полушарие тебя закинет, нужно решить первую задачу: Орел - южное полушарие, Решка - северное полушарие. Ты подкинул монетку 25 раз и судьба явно намекнула тебе. Какая сторона выпадала чаще, если Решка выпала чаще Орла на -(x-5)^2.", ["Северное (Решка)", "Южное (Орел)"], './images/Задача1.jpg'),
    ("Ты обожаешь работать, поэтому не можешь отправиться в Южное полушарие без заявления на отпуск. HR советует указать в бланке конкретную дату. С датами у тебя не очень, кроме своего др ничего не помнишь. Разгадай шифр Цезаря со сдвигом 7 и узнай дату\n\nШифр: `mpyzavmhwyps`",["01.04", "05.08", "21.01", "11.11"],'./images/Задача2.jpg'),
    ("Всё готово к полету в Мерчлэнд! На календаре 1 апреля, чемодан в руках. Таможеннику на границе кажется подозрительным, что ты летишь с единорогом. Он хочет убедиться в твоей адекватности и подсовывает логическую задачку. Начиная с вершины треугольника, двигайся построчно вниз по смежным числам. Найди максимальную сумму чисел", ["44", "17", "23", "67"], './images/Задача3.jpg')
]

common_answers = [
    "Южное (Орел)",
    "01.04",
    "23"
]

python_questions = [
    ('''За правильный ответ тебя пропустили. Задремав в самолете, ты видишь во сне блокнотики и ручки, свитшоты и кружки, футболки и пакеты с логотипами. Мерчлэнд всё ближе! А ты уже идешь получать багаж, узнай номер багажной ленты.''', ["0", "4", "3", "2"], './images/Задача4_Python.jpg'),
    ('''Больше половины пути позади, мерч на горизонте! Ради сохранения своих ног и топового чая от проводницы ты покупаешь билет на поезд. Электронный билет заглючил, придется расшифровать номер состава, чтобы найти его на перроне.''', ["1234", "5678", "0000", "8765"], './images/Задача5_Python.jpg'),
    ('''На мониторе, где должен быть QR-код с подключением к Wi-Fi появилась ошибка. Рядом стоят сотрудники и чешут затылки. Помоги им разобраться, что это за ошибка. (одно ключевое слово, о чём эта ошибка)''', ["скобки", "braces", "parens", "parenthesis"], './images/Задача6_Python.jpg'),
    ('''Ты на месте. Осталось разгадать последний код, чтобы открыть ворота в Мерчленд.''', ["saintostrovok", "ostrovoksaint", "highload", "sainthighload"], './images/Задача7_Python.jpg')
]

python_answers = [
    "3",
    "5678",
    "скобки, скобочки, brac, braces, parens, parenthesis, brackets, __future__",
    "ostrovoksaint"
]

go_answers = [
    "3",
    "5678",
    "body, defer, close, дефер после ошибки",
    "saint"
]

golang_questions = [
    ('''За правильный ответ тебя пропустили. Задремав в самолете, ты видишь во сне блокнотики и ручки, свитшоты и кружки, футболки и пакеты с логотипами. Мерчлэнд всё ближе! А ты уже идешь получать багаж, узнай номер багажной ленты.''', ["3", "5", "0", "1"], './images/Задача4_Go.jpg'),
    ('''Больше половины пути позади, мерч на горизонте! Ради сохранения своих ног и топового чая от проводницы ты покупаешь билет на поезд. Электронный билет заглючил, придется расшифровать номер состава, чтобы найти его на перроне.''', ["1234", "0000", "5678", "8765"], './images/Задача5_Go.jpg'),
    ('''На мониторе, где должен быть QR-код с подключением к Wi-Fi появилась ошибка. Рядом стоят сотрудники и чешут затылки. Помоги им разобраться, что это за ошибка. (одно ключевое слово, о чём эта ошибка)''', ["body", "defer", "close", "дефер после ошибки"], './images/Задача6_Go.jpg'),
    ('''Ты на месте. Осталось разгадать последний код, чтобы открыть ворота в Мерчленд.''', ["sainthighload", "saint", "ostrovok", "saintostrovok"], './images/Задача7_Go.jpg')
]

def get_question_and_options(language, question_index):
    print(language, question_index)
    if language == 'python':
        question, options, image = python_questions[question_index]
    elif language == 'golang':
        question, options, image = golang_questions[question_index]
    return question, options, image

def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_chat_id(chat_id):
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        with open(CHAT_IDS_FILE, 'w') as file:
            json.dump(chat_ids, file)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    save_chat_id(chat_id)
    await context.bot.send_message(chat_id=chat_id, text='🏖')

    keyboard = [
        [
            InlineKeyboardButton("Я согласен", callback_data="agree"),
            InlineKeyboardButton("Не согласен", callback_data="disagree"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(PERSONAL_DATA, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    return AGREE

async def agreement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = query.message.chat.id
    await query.answer()
    await update.callback_query.edit_message_reply_markup(None)
    if query.data == "agree":
        try:
            ostrovok.create_user(user_id, username, chat_id)
        except:
            pass
        await context.bot.send_message(chat_id, text='✈️')
        await context.bot.send_photo(
            chat_id,
            photo='./images/Привет.jpg',
            caption="Твое имя"
        )
        return ASK_NAME
    else:
        keyboard = [
        [
            InlineKeyboardButton("Я согласен", callback_data="agree"),
            InlineKeyboardButton("Не согласен", callback_data="disagree"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(PERSONAL_DATA, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        return AGREE

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    user_id = update.effective_user.id
    try:
        ostrovok.set_user_name(user_id, context.user_data['name'])
    except:
        pass
    await update.message.reply_text("Название компании")
    return ASK_COMPANY

async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['company'] = update.message.text
    query = update.callback_query
    # await query.answer()
    # chat_id = query.message.chat.id
    user_id = update.effective_user.id
    try:
        ostrovok.set_user_company(user_id, context.user_data['company'])
    except:
        pass
    await update.message.reply_text("Твоя должность")
    return ASK_POSITION

async def ask_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text

    user_id = update.effective_user.id
    try:
        ostrovok.set_user_jobTitle(user_id, context.user_data['position'])
    except:
        pass
    await update.message.reply_text("Твой email")
    return ASK_EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    user_id = update.effective_user.id
    try:
        ostrovok.set_user_email(user_id, context.user_data['email'])
    except:
        print("Error setting user's email")

    keyboard = [
        [InlineKeyboardButton("Python", callback_data='python')],
        [InlineKeyboardButton("Go", callback_data='golang')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери язык, на котором бы ты хотел пройти испытания", reply_markup=reply_markup)
    return FAVORITE_LANGUAGE
    # keyboard = [
    #     [InlineKeyboardButton("Командная игра Геогессер", callback_data='geoguessr')],
    #     [InlineKeyboardButton("Задачки", callback_data='puzzles')]
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text("Выбери в какую игру ты будешь играть", reply_markup=reply_markup)
    # return CHOOSE_GAME

async def choose_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    game_choice = query.data
    chat_id = query.message.chat.id
    user_id = update.effective_user.id
    code = ''
    
    if game_choice == 'geoguessr':
        try:
            responce = requests.get(f"http://heyyouhere.space:1566/get_code?id={user_id}")
            ans = responce.json()
            code = ans['code']
            await query.edit_message_text(f"Твой ключ `{code}`", parse_mode=ParseMode.MARKDOWN)
        except:
            print("error in creating geoguessr code")
        # logic for the GeoGuessr game
        keyboard = [
            [InlineKeyboardButton("Пройти квиз", callback_data='puzzles')],
        ]
        # await update.callback_query.edit_message_reply_markup(None)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Отлично, теперь ты можешь пройти турнир по geoguessr, а также пройти квиз", reply_markup=reply_markup)

        return CHOOSE_GAME
    elif game_choice == 'puzzles':
        await query.edit_message_text("Ты выбрал Задачки.")
        context.user_data['question_index'] = 0  # Initialize question index
        # await update.callback_query.edit_message_reply_markup(None)
        await query.message.reply_text(intro, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Далее", callback_data="start_quiz")]]))

        return START_QUIZ
        # keyboard = [
        #     [InlineKeyboardButton("Python", callback_data='python')],
        #     [InlineKeyboardButton("Go", callback_data='golang')]
        # ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        # await query.message.reply_text("Выберите язык, на котором бы хотели пройти квиз", reply_markup=reply_markup)
        # return FAVORITE_LANGUAGE

    return FAVORITE_LANGUAGE

async def favorite_language(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    favorite_language = query.data
    context.user_data['favorite_language'] = favorite_language
    await update.callback_query.edit_message_reply_markup(None)
    user_id = update.effective_user.id
    try:
        pass
        ostrovok.set_favorite_language(user_id, favorite_language)
        # ostrovok.set(user_id, favorite_language)
    except:
        pass
    keyboard = [
        [InlineKeyboardButton("Командная игра Геогессер", callback_data='geoguessr')],
        [InlineKeyboardButton("Задачки", callback_data='puzzles')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выбери в какую игру ты будешь играть", reply_markup=reply_markup)
    return CHOOSE_GAME
    # context.user_data['question_index'] = 0  # Initialize question index
    # await update.callback_query.edit_message_reply_markup(None)
    # await query.message.reply_text(intro, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Далее", callback_data="start_quiz")]]))

    # return START_QUIZ

async def start_quiz(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()
    await update.callback_query.edit_message_reply_markup(None)
    question, options, image = common_questions[0]
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
            chat_id,
            photo=image,
            caption=question,
            reply_markup=reply_markup
        )

    return COMMON_QUESTION_1

async def handle_common_question_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()
    selected_answer = query.data
    user_id = update.effective_user.id
    # print("ANSWER", selected_answer)
    if selected_answer == common_answers[0]:
        try:
            ostrovok.add_points_to_user(user_id, 1)
        except:
            pass
        # print("Correct")
        # add point to the db
    else:
        pass
        # print("Incorrect")

    question, options, image = common_questions[1]
    await update.callback_query.edit_message_reply_markup(None)
    await query.message.reply_text(f'{selected_answer}. Ответ засчитан, поехали дальше!')

    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
            chat_id,
            photo=image,
            caption=question,
            reply_markup=reply_markup
        )

    return COMMON_QUESTION_2

async def handle_common_question_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()
    selected_answer = query.data
    await update.callback_query.edit_message_reply_markup(None)
    user_id = update.effective_user.id
    
    if selected_answer == common_answers[1]:
        try:
            ostrovok.add_points_to_user(user_id, 1)
        except:
            pass
        # print("Correct")
        # add point to the db
    else:
        pass
        # print("Incorrect")

    # print("ANSWER", selected_answer)
    await query.message.reply_text(f'{selected_answer}. Ответ засчитан, поехали дальше!')
    question, options, image = common_questions[2]
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=question,
            reply_markup=reply_markup
        )

    return COMMON_QUESTION_3

async def handle_common_question_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global QUESTION_INDEX
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()
    selected_answer = query.data
    user_id = update.effective_user.id
    # print("ANSWER", selected_answer)
    if selected_answer == common_answers[2]:
        try:
            ostrovok.add_points_to_user(user_id, 1)
        except:
            pass
        # print("Correct")
        # add point to the db
    else:
        pass
        # print("Incorrect")
    await query.message.reply_text(f'{selected_answer}. Ответ засчитан, поехали дальше!')
    await update.callback_query.edit_message_reply_markup(None)
    favorite_language = context.user_data['favorite_language']
    context.user_data['question_index'] = 0
    QUESTION_INDEX = 0

    question, options, image = get_question_and_options(favorite_language, 0)
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
                chat_id=chat_id,
                photo=image,
                caption=question,
                reply_markup=reply_markup
            )

    # await query.message.reply_text(question, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    if favorite_language == 'python':
        return PYTHON_QUIZ
    elif favorite_language == 'golang':
        return GOLANG_QUIZ

async def handle_python_q3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.lower().strip()
    correct_answers = ["скобки", "скобочки", "brac", "braces", "parens", "parenthesis", "brackets", "__future__"]
    # print("ANSWER", answer)
    user_id = update.effective_user.id
    if any(correct in answer for correct in correct_answers):
        try:
            ostrovok.add_points_to_user(user_id, 1)
        except:
            print('there was an error adding the point')
        # print("Correct")
    else:
        pass
        # print("Incorrect")
    await update.message.reply_text(f'{answer}. Ответ засчитан, поехали дальше!')
    return await continue_python_quiz(update, context)

async def handle_golang_q3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.lower().strip()
    correct_answers = ["body", "defer", "close", "дефер после ошибки"]
    # print("ANSWER", answer)
    if any(correct in answer for correct in correct_answers):
        user_id = update.effective_user.id

        try:
            ostrovok.add_points_to_user(user_id, 1)
        except:
            print('there was an error adding the point')
        # print("Correct")
    else:
        pass
        # print("Incorrect")
    await update.message.reply_text(f'{answer}. Ответ засчитан, поехали дальше!')
    return await continue_golang_quiz(update, context)

async def continue_python_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global QUESTION_INDEX
    chat_id = update.message.chat.id
    # question_index = context.user_data['question_index']
    QUESTION_INDEX += 1
    next_question_index = QUESTION_INDEX

    question, options, image = get_question_and_options('python', next_question_index)
    keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id,
        photo=image,
        caption=question,
        reply_markup=reply_markup
    )

    return PYTHON_QUIZ

async def continue_golang_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global QUESTION_INDEX
    chat_id = update.message.chat.id
    # question_index = context.user_data['question_index']
    QUESTION_INDEX += 1
    next_question_index = QUESTION_INDEX

    question, options, image = get_question_and_options('golang', next_question_index)
    keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id,
        photo=image,
        caption=question,
        reply_markup=reply_markup
    )

    return GOLANG_QUIZ

async def handle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global QUESTION_INDEX
    query = update.callback_query
    chat_id = update.callback_query.message.chat.id
    await query.answer()
    await update.callback_query.edit_message_reply_markup(None)
    user_id = update.effective_user.id
    favorite_language = context.user_data['favorite_language']
    try:
        requests.get(f'http://heyyouhere.space:1566/get_code?id={chat_id}&team={favorite_language}')
    except:
        pass
    # question_index = context.user_data['question_index']
    selected_answer = query.data

    await query.message.reply_text(f'{selected_answer}. Ответ засчитан, поехали дальше!')

    # Process the current question answer here if needed
    if favorite_language == 'python':
        if QUESTION_INDEX == 0 and selected_answer == python_answers[0]:  
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
        if QUESTION_INDEX == 1 and selected_answer == python_answers[1]:
  
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
        if QUESTION_INDEX == 3 and selected_answer == python_answers[3]:
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
    elif favorite_language == 'golang':
        if QUESTION_INDEX == 0 and selected_answer == go_answers[0]:
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
        if QUESTION_INDEX == 1 and selected_answer == go_answers[1]:
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
        if QUESTION_INDEX == 3 and selected_answer == go_answers[3]:
            try:
                ostrovok.add_points_to_user(user_id, 1)
            except:
                print('there was an error adding the point')
    # print("ANSWER",selected_answer, QUESTION_INDEX)
    # sent point and add if correct on server
    if QUESTION_INDEX + 1 < len(python_questions if favorite_language == 'python' else golang_questions):
        next_question_index = QUESTION_INDEX + 1

        # Handle the third question differently
        if next_question_index == 2:
            question, options, image = get_question_and_options(favorite_language, next_question_index)
            await context.bot.send_photo(chat_id, photo=image, caption=question)
            QUESTION_INDEX += 1
            return PYTHON_Q3 if favorite_language == 'python' else GOLANG_Q3
        else:
            question, options, image = get_question_and_options(favorite_language, next_question_index)
            keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_photo(
                chat_id,
                photo=image,
                caption=question,
                reply_markup=reply_markup
            )

            QUESTION_INDEX += 1

            return PYTHON_QUIZ if favorite_language == 'python' else GOLANG_QUIZ
    else:
        keyboard = [
            [InlineKeyboardButton("Получить код", callback_data='get_code')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # print(user_id)
        try:
            data = ostrovok.get_total_points(user_id)
        except:
            pass
        total_points = data['total_points']
        res = 'баллов'
        match total_points:
            case 1:
                res = 'балл'
            case 2 | 3 | 4:
                res = 'балла'
            case _ :
                res = 'баллов'
        await context.bot.send_message(chat_id=chat_id, text=f"Конец викторины. Спасибо за участие! У тебя {total_points} {res} из 7")
        await context.bot.send_message(chat_id=chat_id, text="Если ты еще не принял участие в командном соревновании в игре geoguessr или забыл код", reply_markup=reply_markup)
        return ConversationHandler.END


async def get_geoguessr_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = update.callback_query.message.chat.id
    selected_answer = query.data
    await query.answer()
    user_id = update.effective_user.id
    code = ''

    if selected_answer == 'get_code':
        try:
            responce = requests.get(f"http://heyyouhere.space:1566/get_code?id={user_id}")
            ans = responce.json()
            code = ans['code']
            await query.edit_message_text(f"Твой ключ `{code}`", parse_mode=ParseMode.MARKDOWN)
        except:
            print("error in creating geoguessr code")
    # return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Диалог отменен.')
    return ConversationHandler.END


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_after_command = ' '.join(context.args)
    user_id = update.effective_user.id
    message = text_after_command

    try:
        all_users = ostrovok.get_all_users()

        if user_id in ALLOWED_USER_IDS:   
            for user in all_users:
                chat_id = user['chat_id']
                try:
                    await context.bot.send_message(chat_id=chat_id, text=message)
                except:
                    pass
    except:
        pass

async def send_message_python(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_after_command = ' '.join(context.args)
    user_id = update.effective_user.id
    message = text_after_command

    try:
        all_users = ostrovok.get_all_users()

        if user_id in ALLOWED_USER_IDS:   
            for user in all_users:
                chat_id = user['chat_id']
                favorite_language = user['favorite_language']
                if favorite_language == 'python':
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=message)
                    except:
                        pass
    except:
        pass

async def send_message_golang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_after_command = ' '.join(context.args)
    user_id = update.effective_user.id
    message = text_after_command

    try:
        all_users = ostrovok.get_all_users()

        if user_id in ALLOWED_USER_IDS:   
            for user in all_users:
                chat_id = user['chat_id']
                favorite_language = user['favorite_language']
                if favorite_language == 'golang':
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=message)
                    except:
                        pass
    except:
        pass

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGREE: [CallbackQueryHandler(agreement)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            ASK_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_position)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            FAVORITE_LANGUAGE: [CallbackQueryHandler(favorite_language)],
            CHOOSE_GAME: [CallbackQueryHandler(choose_game)],
            START_QUIZ: [CallbackQueryHandler(start_quiz)],
            COMMON_QUESTION_1: [CallbackQueryHandler(handle_common_question_1)],
            COMMON_QUESTION_2: [CallbackQueryHandler(handle_common_question_2)],
            COMMON_QUESTION_3: [CallbackQueryHandler(handle_common_question_3)],
            PYTHON_QUIZ: [CallbackQueryHandler(handle_quiz)],
            GOLANG_QUIZ: [CallbackQueryHandler(handle_quiz)],
            PYTHON_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_python_q3)],
            GOLANG_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_golang_q3)],
        },
        fallbacks=[CallbackQueryHandler(get_geoguessr_code)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("send_message", send_message))
    application.add_handler(CommandHandler("send_message_python", send_message_python))
    application.add_handler(CommandHandler("send_message_golang", send_message_golang))
    application.add_handler(CallbackQueryHandler(get_geoguessr_code))

    application.run_polling()

if __name__ == '__main__':
    main()
