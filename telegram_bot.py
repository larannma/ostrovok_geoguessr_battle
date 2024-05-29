from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, MessageHandler
from telegram.constants import ParseMode
import ostrovok_api as ostrovok

TOKEN="6608411270:AAFxz3exgwwitxaoDgjsGMIlxluRDo-Bxno"

AGREE, ASK_NAME, ASK_EMAIL, COMPLETE = range(4)

PERSONAL_DATA = "Соглашение об обработке персональных данных"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.message.chat_id, text='🏖')

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
            caption="Введите ваше имя:"
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
    await update.message.reply_text("Введите ваш email:")
    return ASK_EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Спасибо! Ваш код для игры в geoguessr: exgw")
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGREE: [CallbackQueryHandler(agreement)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
        },
        fallbacks=[],
        per_user=True
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()