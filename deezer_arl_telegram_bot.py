import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from deezer_arl import get_arl_list  # Import the function from your existing script

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# List of allowed user IDs
ALLOWED_USERS = [userid1,userid2]
BOT_TOKEN = 'bot_token'

def restricted(func):
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            await update.message.reply_text("Esto no es para ti.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

# Define the command handler function
@restricted
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Dame ARL", callback_data='dame_arl')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hola! Envia /dame_arl para obtener un ARL o presiona el botón.', reply_markup=reply_markup)


@restricted
async def dame_arl(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id  # Get the chat ID from the update
    await context.bot.send_message(chat_id=chat_id, text="Buscando ARLs...")
    url = 'https://rentry.org/firehawk52#deezer-arls'
    arl_list = get_arl_list(url)

    if len(arl_list) > 0:
        telegram_message = '\n\n'.join([str(arl) for arl in arl_list])
    else:
        telegram_message = 'No se encontraron ARLs.'

    await context.bot.send_message(chat_id=chat_id, text="ARL encontrado!:\n " + str(telegram_message), parse_mode='MarkdownV2')

@restricted
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'dame_arl':
        await dame_arl(update, context)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dame_arl", dame_arl))
    application.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()