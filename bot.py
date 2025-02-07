import logging
import asyncio
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "توکن_ربات_اینجا"

# لیست مجاز برای استفاده از ربات
AUTHORIZED_USERS = [6028678292, 5823758920, 203061831, 1252845815]  # آیدی عددی یوزرها

# لود کردن داده‌ها از فایل JSON
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"words": {}}

# ذخیره داده‌ها در فایل JSON
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()

# دکمه‌های ثابت منو
main_menu = [["➕ افزودن کلمه", "📝 ویرایش کلمه"], ["❌ حذف کلمه", "📋 لیست کلمات"]]

# استارت ربات
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ شما اجازه‌ی استفاده از این ربات را ندارید!")
        return
    await update.message.reply_text(
        "✅ ربات مدیریت لغات فعال شد!\n\nاز دکمه‌های زیر استفاده کنید:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# افزودن کلمه
async def add_word(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        return
    await update.message.reply_text("🔹 لطفاً کلمه‌ای که می‌خواهید اضافه کنید را بفرستید.")
    context.user_data["action"] = "add"

# ویرایش کلمه
async def edit_word(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        return
    await update.message.reply_text("🔹 لطفاً کلمه‌ای که می‌خواهید ویرایش کنید را بفرستید.")
    context.user_data["action"] = "edit"

# حذف کلمه
async def remove_word(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        return
    await update.message.reply_text("🔹 لطفاً کلمه‌ای که می‌خواهید حذف کنید را بفرستید.")
    context.user_data["action"] = "remove"

# نمایش لیست کلمات
async def list_words(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        return
    words_list = "\n".join([f"{word}: {meaning}" for word, meaning in data["words"].items()])
    message = words_list if words_list else "❌ لیست کلمات خالی است!"
    await update.message.reply_text(f"📋 لیست کلمات:\n\n{message}")

# پردازش پیام‌های ورودی
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        return
    text = update.message.text
    action = context.user_data.get("action")

    if action == "add":
        await update.message.reply_text("🔹 معنی این کلمه را ارسال کنید.")
        context.user_data["new_word"] = text
        context.user_data["action"] = "add_meaning"

    elif action == "add_meaning":
        new_word = context.user_data.get("new_word")
        if new_word:
            data["words"][new_word] = text
            save_data(data)
            await update.message.reply_text(f"✅ کلمه '{new_word}' با موفقیت اضافه شد!")
            context.user_data.clear()

    elif action == "edit":
        if text in data["words"]:
            await update.message.reply_text("🔹 لطفاً معنی جدید را بفرستید.")
            context.user_data["word_to_edit"] = text
            context.user_data["action"] = "edit_meaning"
        else:
            await update.message.reply_text("❌ این کلمه در لیست وجود ندارد!")

    elif action == "edit_meaning":
        word_to_edit = context.user_data.get("word_to_edit")
        if word_to_edit:
            data["words"][word_to_edit] = text
            save_data(data)
            await update.message.reply_text(f"✅ معنی کلمه '{word_to_edit}' بروزرسانی شد!")
            context.user_data.clear()

    elif action == "remove":
        if text in data["words"]:
            del data["words"][text]
            save_data(data)
            await update.message.reply_text(f"✅ کلمه '{text}' با موفقیت حذف شد!")
        else:
            await update.message.reply_text("❌ این کلمه در لیست وجود ندارد!")
        context.user_data.clear()

    elif text in data["words"]:
        await update.message.reply_text(f"📖 معنی '{text}': {data['words'][text]}")

# راه‌اندازی ربات
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^➕ افزودن کلمه$"), add_word))
    application.add_handler(MessageHandler(filters.Regex("^📝 ویرایش کلمه$"), edit_word))
    application.add_handler(MessageHandler(filters.Regex("^❌ حذف کلمه$"), remove_word))
    application.add_handler(MessageHandler(filters.Regex("^📋 لیست کلمات$"), list_words))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات فعال شد...")
    application.run_polling()

if name == "main":
    main()