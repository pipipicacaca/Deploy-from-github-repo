import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = "8634162308:AAFYWloUyejhzsWiGNU_s9gWhdUCgxuVtUI"
CHANNEL_WORD = -1003914309575
CHANNEL_PPT = -1003931579263
CHANNEL_PDF = -1003943396683
CHANNEL_EXCEL = -1003590590648
CHANNEL_OTHER = -1003918169469

logging.basicConfig(level=logging.INFO)
chat_files = {}

def get_channel(file_name):
    name = file_name.lower()
    if name.endswith((".doc", ".docx")):
        return CHANNEL_WORD
    elif name.endswith((".ppt", ".pptx")):
        return CHANNEL_PPT
    elif name.endswith(".pdf"):
        return CHANNEL_PDF
    elif name.endswith((".xls", ".xlsx", ".csv")):
        return CHANNEL_EXCEL
    return CHANNEL_OTHER

async def handle_file(update, context):
    message = update.message
    if not message:
        return
    chat_id = message.chat_id
    if chat_id not in chat_files:
        chat_files[chat_id] = []
    file_info = None
    if message.document:
        file_info = {"message_id": message.message_id, "chat_id": chat_id, "name": message.document.file_name or "file"}
    elif message.photo:
        file_info = {"message_id": message.message_id, "chat_id": chat_id, "name": "photo.jpg"}
    if file_info:
        chat_files[chat_id].append(file_info)
        await message.reply_text("OK: " + file_info["name"])

async def sort_command(update, context):
    chat_id = update.message.chat_id
    files = chat_files.get(chat_id, [])
    if not files:
        await update.message.reply_text("No files yet!")
        return
    await update.message.reply_text("Sorting " + str(len(files)) + " files...")
    count = 0
    for f in files:
        try:
            await context.bot.forward_message(chat_id=get_channel(f["name"]), from_chat_id=f["chat_id"], message_id=f["message_id"])
            count += 1
        except Exception as e:
            logging.error(e)
    chat_files[chat_id] = []
    await update.message.reply_text("Done! Sorted: " + str(count))

async def start_command(update, context):
    await update.message.reply_text("Bot is ready! Send files and type /sort")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("sort", sort_command))
app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
app.run_polling()
