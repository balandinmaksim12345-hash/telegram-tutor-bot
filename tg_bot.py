import json
import logging
import os
import random
from collections import defaultdict

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS = []
TOPICS_BY_SUBJECT = defaultdict(set)
YOUR_WIFE_TELEGRAM_ID = 1355808970

def load_questions():
    global QUESTIONS, TOPICS_BY_SUBJECT
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            QUESTIONS = data.get("questions", [])
        logger.info(f"Загружено {len(QUESTIONS)} вопросов.")
    except Exception as e:
        logger.error(f"Ошибка загрузки вопросов: {e}")
        QUESTIONS = []

    TOPICS_BY_SUBJECT.clear()
    for q in QUESTIONS:
        subject = q.get("subject", "unknown")
        topic = q.get("topic", "Общее")
        TOPICS_BY_SUBJECT[subject].add(topic)
    logger.info(f"Темы: {dict(TOPICS_BY_SUBJECT)}")


async def main_menu(update_or_query, context, is_callback=False):
    keyboard = [
        [InlineKeyboardButton("📝 Записаться на урок", callback_data="signup")],
        [InlineKeyboardButton("💰 Цены и условия", callback_data="prices")],
        [InlineKeyboardButton("📚 Русский язык", callback_data="subject_russian")],
        [InlineKeyboardButton("📖 Литература", callback_data="subject_literature")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 Здравствуйте! Я бот-помощник Баландиной Полины Антоновны.\nВыберите действие:"
    if is_callback:
        await update_or_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context, is_callback=False)


async def show_topics(query, subject, title):
    topics = list(TOPICS_BY_SUBJECT.get(subject, []))
    if not topics:
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        await query.edit_message_text(f"{title}\n\nНет тем.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    keyboard = []
    for topic in topics:
        callback = f"test_{subject}_{topic}"
        keyboard.append([InlineKeyboardButton(topic, callback_data=callback)])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    await query.edit_message_text(f"{title}\n\nВыберите тему для теста:", reply_markup=InlineKeyboardMarkup(keyboard))


async def start_test(query, context, subject, topic):
    filtered = [q for q in QUESTIONS if q.get("subject") == subject and q.get("topic") == topic]
    if not filtered:
        await query.edit_message_text("❌ Вопросов по этой теме нет.")
        return

    context.user_data["test_questions"] = filtered.copy()
    context.user_data["test_subject"] = subject
    context.user_data["test_topic"] = topic
    await send_random_question(query, context)


async def send_random_question(update_or_query, context, is_new=False):
    questions = context.user_data.get("test_questions", [])
    if not questions:
        await update_or_query.edit_message_text("❌ Нет вопросов.")
        return

    q = random.choice(questions)
    context.user_data["current_question"] = q

    text = f"❓ {q['question']}"
    keyboard = []
    for i, opt in enumerate(q["options"]):
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"ans_{i}")])
    keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_new:
        await update_or_query.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update_or_query.edit_message_text(text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "signup":
        context.user_data["state"] = "signup_name"
        await query.edit_message_text("📝 Как вас зовут?")

    elif data == "prices":
        text = (
            "💰 **Цены:**\n"
            "• Индивидуальное (60 мин) — 1500 руб.\n"
            "• Парное (60 мин) — 1000 руб.\n"
            "• Экспресс к ЕГЭ (90 мин) — 2000 руб.\n\n"
            "Первое занятие **бесплатно**!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "subject_russian":
        await show_topics(query, "russian", "📚 Русский язык")

    elif data == "subject_literature":
        await show_topics(query, "literature", "📖 Литература")

    elif data.startswith("test_"):
        parts = data.split("_", 2)
        if len(parts) == 3:
            subject = parts[1]
            topic = parts[2]
            await start_test(query, context, subject, topic)

    elif data.startswith("ans_"):
        selected = int(data.split("_")[1])
        current_q = context.user_data.get("current_question")
        if not current_q:
            await query.edit_message_text("Ошибка. Начните тест заново.")
            return

        correct = current_q.get("correct_option_index", 0)

        if selected == correct:
            result = current_q.get("feedback_correct", "✅ Верно! 👍")
        else:
            result = current_q.get("feedback_incorrect", f"❌ Неверно. Правильный ответ: {current_q['options'][correct]}")

        keyboard = [
            [InlineKeyboardButton("➡️ Следующий вопрос", callback_data="next_question")],
            [InlineKeyboardButton("🏠 В меню", callback_data="back_to_main")]
        ]
        await query.edit_message_text(
            f"{result}\n\nНажмите «Следующий вопрос» для продолжения.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "next_question":
        await send_random_question(query, context)

    elif data == "back_to_main":
        for key in ["test_questions", "current_question", "test_subject", "test_topic"]:
            context.user_data.pop(key, None)
        await main_menu(query, context, is_callback=True)

    else:
        await query.edit_message_text("Неизвестная команда. /start")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    text = update.message.text

    if state == "signup_name":
        context.user_data["student_name"] = text
        context.user_data["state"] = "signup_age"
        await update.message.reply_text(f"Приятно познакомиться, {text}! В каком классе ученик?")

    elif state == "signup_age":
        if not text.isdigit():
            await update.message.reply_text("Введите число.")
            return
        context.user_data["student_age"] = text
        context.user_data["state"] = "signup_score"
        await update.message.reply_text("Укажите желаемый балл (ЕГЭ/ОГЭ)?")

    elif state == "signup_score":
        context.user_data["student_score"] = text
        name = context.user_data.get("student_name", "Не указано")
        age = context.user_data.get("student_age", "Не указано")
        score = context.user_data.get("student_score", "Не указано")

        try:
            await context.bot.send_message(
                chat_id=YOUR_WIFE_TELEGRAM_ID,
                text=(
                    f"📝 **НОВАЯ ЗАЯВКА!**\n\n"
                    f"👤 Имя: {name}\n"
                    f"📚 Класс: {age}\n"
                    f"🎯 Желаемый балл: {score}"
                ),
                parse_mode="Markdown"
            )
            await update.message.reply_text("✅ Заявка отправлена! Преподаватель свяжется с вами.")
        except Exception as e:
            logger.error(f"Ошибка при отправке заявки: {e}")
            await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.")

        for key in ["state", "student_name", "student_age", "student_score"]:
            context.user_data.pop(key, None)

    else:
        await main_menu(update, context, is_callback=False)


def main():
    load_questions()
    if not QUESTIONS:
        logger.warning("Нет вопросов. Бот будет работать без тестов.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Бот запущен и готов к работе!")
    logger.info(f"Сообщения будут отправляться на ID: {YOUR_WIFE_TELEGRAM_ID}")
    
    app.run_polling()


if __name__ == "__main__":
    main()
