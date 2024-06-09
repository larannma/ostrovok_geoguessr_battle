from telegram import ForceReply, Update, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.constants import ParseMode
import json
import os

TOKEN = "6608411270:AAHY6BEDs5rsBSR93WBN5j_lNdUMPqasbV0"
CHAT_IDS_FILE = 'chat_ids.json'

# Define states
AGREE, ASK_NAME, ASK_COMPANY, ASK_POSITION, ASK_EMAIL, CHOOSE_GAME, FAVORITE_LANGUAGE, START_QUIZ, COMMON_QUESTION_1, COMMON_QUESTION_2, COMMON_QUESTION_3, PYTHON_QUIZ, GOLANG_QUIZ = range(13)

PERSONAL_DATA = "Если вы нажимаете продолжить, то вы соглашаетесь с условиями хранения данных"

intro = 'Привет, о великий повелитель кода. Язык программирования выбран, он поможет пройти квест и получить подарок. Островок отправляет тебя в путешествие за мерчом. Но где находится этот Мерчленд?'

final_answer = '''Ты настоящий герой! Подойди на стенд компании Островок и забери свой подарок. Покажи менеджеру свой результат. Тебе еще возвращаться домой, с мерчом это делать намного приятнее)'''

common_questions = [
    ("Чтобы понять в какое полушарие тебя закинет, нужно решить первую задачу: Орел - южное полушарие, Решка - северное полушарие. Ты подкинул монетку 50 раз и судьба явно намекнула тебе. Какая сторона выпадала чаще, если Решка выпала чаще Орла на (x-5)^2.", ["Северное (Решка)", "Южное (Орел)"]),
    "Ты обожаешь работать, поэтому не можешь отправиться в Южное полушарие без заявления на отпуск. HR советует указать в бланке конкретную дату. С датами у тебя не очень, кроме своего др ничего не помнишь. Разгадай шифр Цезаря со сдвигом 7 и узнай дату",
    ("Всё готово к полету в Мерчлэнд! На календаре 1 апреля, чемодан в руках. Таможеннику на границе кажется подозрительным, что ты летишь с единорогом. Он хочет убедиться в твоей адекватности и подсовывает логическую задачку. Найди последовательность с наибольшей суммой чисел:", ["44", "17", "23", "67"])
]

python_questions = [
    ('''За правильный ответ тебя пропустили. Задремав в самолете, ты видишь во сне блокнотики и ручки, свитшоты и кружки, футболки и пакеты с логотипами. Мерчлэнд всё ближе! А ты уже идешь получать багаж, узнай номер багажной ленты.```python\nx = 0
a = 5
b = 5
if a > 0:
    if b < 0:
        x = x + 5
    elif a > 5:
        x = x + 4
    else:
        x = x + 3
else:
    x = x + 2
print(x)\n```''', ["0", "4", "3", "2"]),
    ('''Все бывшие не заслуживали столько усилий, сколько вложено в прохождение этого испытания. Получается, мерч Островка лучше любых отношений. Скоро вы встретитесь! Местный аэроэкспресс уже ждет на перроне, но на каком?```python\nclass A:
    def my_password(self):
        print("1234")

class B(A):
    def my_password(self):
        print("5678")

class C(A):
    def my_password(self):
        print("0000")

class D(B, C):
    pass

d = D()
d.my_password()
\n```''', ["1234", "5678", "0000", "8765"]),
    ('''Поезд прибыл только ночью, пришлось менять колесо в пути.  Вызвать такси не удается, твой интернет не работает, пытаешься подключиться к wi-fi, но пароль подсказать некому. Угадать пароль — проще простого! ```python\nx = {'a': 1, 'b': 2}\nSyntaxError: not a chance\n```''', ["скобки", "braces", "parens", "parenthesis"]),
    ('''Ты на месте. Осталось разгадать последний код, чтобы открыть ворота в Мерчленд.```python\na = {'saint', 'high', 'load'}
b = {'high', 'load', 'ostrovok'}
x = list(a^b)
print(sorted(x))\n```''', ["saintostrovok", "ostrovoksaint", "highload", "sainthighload"])
]

golang_questions = [
    ('''За правильный ответ тебя пропустили. Задремав в самолете, ты видишь во сне блокнотики и ручки, свитшоты и кружки, футболки и пакеты с логотипами. Мерчлэнд всё ближе! А ты уже идешь получать багаж, узнай номер багажной ленты.```go\npackage main

import "fmt"

func fun() bool {
	return false
}

func main() {
	switch fun(); {
	case true:
		fmt.Println(3)
	case false:
		fmt.Println(5)
       default:
		fmt.Println(0)
	}
}
```''', ["11", "10", "12", "13"]),
    ('''Все бывшие не заслуживали столько усилий, сколько вложено в прохождение этого испытания. Получается, мерч Островка лучше любых отношений. Скоро вы встретитесь! Местный аэроэкспресс уже ждет на перроне, но на каком?```go\npackage main
import "fmt"
var password string = "1234"
func init() {
        password = "0000"
}
func init() {
        password = "5678"
}
func main() {
        fmt.Println(password)\n```''', ["1234", "0000", "5678", "8765"]),
    ('''Поезд прибыл только ночью, пришлось менять колесо в пути.  Вызвать такси не удается, твой интернет не работает, пытаешься подключиться к wi-fi, но пароль подсказать некому. Угадать пароль — проще простого! ```go\nfunc main() {  
    resp, err := http.Get("https://example.org")
    defer resp.Body.Close()
    if err != nil {
        fmt.Println(err)
        return
    }

    body, err := ioutil.ReadAll(resp.Body)
    // ...
}

// panic: runtime error: invalid memory address or nil pointer dereference
\n```''', ["body", "defer", "close", "дефер после ошибки"]),
    ('''Ты на месте. Осталось разгадать последний код, чтобы открыть ворота в Мерчленд.```go\npackage main

import (
"fmt"
"strings"
)

func main() {
	src := []string{"saint", "high", "load"}
	dst := []string{"ostrovok"}
	copy(dst, src)
	fmt.Println(strings.Join(dst, ""))
}
\n```''', ["sainthighload", "saint", "ostrovok", "saintostrovok"])
]

def get_question_and_options(language, question_index):
    if language == 'python':
        question, options = python_questions[question_index]
    elif language == 'golang':
        question, options = golang_questions[question_index]
    return question, options

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

    await update.message.reply_text(PERSONAL_DATA, reply_markup=reply_markup)
    
    return AGREE

async def agreement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "agree":
        await query.edit_message_text(text="Спасибо за ваше согласие.", reply_markup=None)
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='./images/greetings.png',
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
        await update.callback_query.edit_message_reply_markup(None)
        await query.message.reply_text(PERSONAL_DATA, reply_markup=reply_markup)
        return AGREE

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Название компании")
    return ASK_COMPANY

async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['company'] = update.message.text
    await update.message.reply_text("Твоя должность")
    return ASK_POSITION

async def ask_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text
    await update.message.reply_text("Твой email")
    return ASK_EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Командная игра Геогессер", callback_data='geoguessr')],
        [InlineKeyboardButton("Задачки", callback_data='puzzles')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери в какую игру ты будешь играть", reply_markup=reply_markup)
    return CHOOSE_GAME

async def choose_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    game_choice = query.data

    if game_choice == 'geoguessr':
        await query.edit_message_text("Ты выбрал командную игру Геогессер. Твой ключ AKJLWFH")
        # logic for the GeoGuessr game
        return ConversationHandler.END
    elif game_choice == 'puzzles':
        await query.edit_message_text("Вы выбрали Задачки.")
        keyboard = [
            [InlineKeyboardButton("Python", callback_data='python')],
            [InlineKeyboardButton("Golang", callback_data='golang')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите язык, на котором бы хотели пройти квиз", reply_markup=reply_markup)
        return FAVORITE_LANGUAGE

    return FAVORITE_LANGUAGE

async def favorite_language(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    favorite_language = query.data
    context.user_data['favorite_language'] = favorite_language
    context.user_data['question_index'] = 0  # Initialize question index

    await query.message.reply_text(intro, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Далее", callback_data="start_quiz")]]))

    return START_QUIZ

async def start_quiz(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    question, options = common_questions[0]
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(question, reply_markup=reply_markup)

    return COMMON_QUESTION_1

async def handle_common_question_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    selected_answer = query.data

    await query.edit_message_text(text=f"Your answer: {selected_answer}. Next question:")

    await query.message.reply_text(common_questions[1])

    return COMMON_QUESTION_2

async def handle_common_question_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text

    await update.message.reply_text(f"Ваш ответ: {answer}. Следующий вопрос:")

    question, options = common_questions[2]
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(question, reply_markup=reply_markup)

    return COMMON_QUESTION_3

async def handle_common_question_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    selected_answer = query.data

    await query.edit_message_text(text=f"Ваш ответ: {selected_answer}. Следующий вопрос:")

    favorite_language = context.user_data['favorite_language']
    context.user_data['question_index'] = 0  # Reset for specific questions

    question, options = get_question_and_options(favorite_language, 0)
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(question, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    if favorite_language == 'python':
        return PYTHON_QUIZ
    elif favorite_language == 'golang':
        return GOLANG_QUIZ

async def handle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    selected_answer = query.data

    favorite_language = context.user_data['favorite_language']
    question_index = context.user_data['question_index']

    context.user_data['question_index'] += 1

    if question_index + 1 < len(python_questions if favorite_language == 'python' else golang_questions):
        next_question_index = question_index + 1
        question, options = get_question_and_options(favorite_language, next_question_index)
        keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Ваш ответ: {selected_answer}. Следующий вопрос:", parse_mode=ParseMode.MARKDOWN)
        await query.message.reply_text(question, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

        return PYTHON_QUIZ if favorite_language == 'python' else GOLANG_QUIZ
    else:
        await query.edit_message_text(text=final_answer)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Диалог отменен.')
    return ConversationHandler.END

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ' '.join(context.args)
    chat_ids = load_chat_ids()
    for chat_id in chat_ids:
        await context.bot.send_message(chat_id=chat_id, text=message)

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
            CHOOSE_GAME: [CallbackQueryHandler(choose_game)],
            FAVORITE_LANGUAGE: [CallbackQueryHandler(favorite_language)],
            START_QUIZ: [CallbackQueryHandler(start_quiz)],
            COMMON_QUESTION_1: [CallbackQueryHandler(handle_common_question_1)],
            COMMON_QUESTION_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_common_question_2)],
            COMMON_QUESTION_3: [CallbackQueryHandler(handle_common_question_3)],
            PYTHON_QUIZ: [CallbackQueryHandler(handle_quiz)],
            GOLANG_QUIZ: [CallbackQueryHandler(handle_quiz)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("send_message", send_message))

    application.run_polling()

if __name__ == '__main__':
    main()
