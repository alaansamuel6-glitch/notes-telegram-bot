import telebot
from telebot import types
import threading
import time
import re
from datetime import datetime, timedelta

from config import token
from database import (
    init_db, add_reminder, get_user_reminders, get_all_pending, 
    delete_reminder, add_note, get_notes, delete_note
)

bot = telebot.TeleBot(token)
user_states = {}

def parse_when(raw: str) -> datetime | None:
    raw = raw.strip()
    if raw.startswith("+"):
        match = re.fullmatch(r"\+(\d+)([mhd])", raw.lower())
        if not match:
            return None
        num, unit = int(match.group(1)), match.group(2)
        delta = {
            "m": timedelta(minutes=num),
            "h": timedelta(hours=num),
            "d": timedelta(days=num),
        }[unit]
        return datetime.now() + delta
    try:
        return datetime.strptime(raw, "%d.%m.%Y %H:%M")
    except ValueError:
        return None

def reminder_worker():
    print("⏰ Поток напоминаний запущен...")
    while True:
        now = datetime.now()
        pending = get_all_pending()
        
        for rid, user_id, text, at in pending:
            remind_at = datetime.strptime(at, "%Y-%m-%d %H:%M")
            if remind_at <= now:
                try:
                    bot.send_message(
                        user_id,
                        f"🔔 <b>Напоминание!</b>\n\n📝 {text}",
                        parse_mode="HTML"
                    )
                    # Физически удаляем из базы после отправки
                    delete_reminder(rid)
                except Exception as e:
                    print(f"Ошибка отправки для {user_id}: {e}")
        
        time.sleep(30)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Добавить дело"), types.KeyboardButton("📋 Мои дела"))
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой ежедневник-напоминалка.\n\n"
        "Я помогу не забыть о делах и сохраню твои заметки.\n"
        "Для заметок используй: /note <текст>",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        "📖 <b>Как пользоваться:</b>\n\n"
        "1. Нажми <b>📝 Добавить дело</b> (или /add)\n"
        "2. Напиши текст дела\n"
        "3. Напиши время: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code> или <code>+30m</code>\n\n"
        "📒 <b>Заметки:</b>\n"
        "/note <текст> — сохранить заметку\n"
        "/notes — показать все заметки",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['add'])
@bot.message_handler(func=lambda m: m.text == "📝 Добавить дело")
def cmd_add(message):
    user_states[message.chat.id] = {"state": "waiting_text"}
    bot.send_message(message.chat.id, "📝 Что нужно сделать? (или /cancel для отмены)")

@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    if message.chat.id in user_states:
        del user_states[message.chat.id]
    bot.send_message(message.chat.id, "❌ Отменено.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['list'])
@bot.message_handler(func=lambda m: m.text == "📋 Мои дела")
def cmd_list(message):
    items = get_user_reminders(message.from_user.id)
    if not items:
        bot.send_message(message.chat.id, "📭 Пока нет предстоящих дел.")
        return

    for rid, text, at in items:
        dt = datetime.strptime(at, "%Y-%m-%d %H:%M")
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{rid}"),
            types.InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{rid}")
        )
        bot.send_message(
            message.chat.id, 
            f"📝 <b>{text}</b>\n🕐 {dt.strftime('%d.%m.%Y %H:%M')}", 
            parse_mode="HTML", 
            reply_markup=markup
        )

@bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id]["state"] == "waiting_text")
def process_text(message):
    user_states[message.chat.id]["text"] = message.text
    user_states[message.chat.id]["state"] = "waiting_time"
    bot.send_message(
        message.chat.id,
        "⏰ Когда напомнить?\nФормат: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code> или <code>+30m</code>, <code>+2h</code>, <code>+1d</code>",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id]["state"] == "waiting_time")
def process_time(message):
    remind_at = parse_when(message.text)
    
    if not remind_at:
        bot.send_message(message.chat.id, "❌ Не понял дату. Введи ещё раз (например, +30m):")
        return
    if remind_at <= datetime.now():
        bot.send_message(message.chat.id, "⚠️ Это время уже прошло. Введи будущее время.")
        return

    text = user_states[message.chat.id]["text"]
    rid = add_reminder(message.from_user.id, text, remind_at)
    
    del user_states[message.chat.id]
    
    bot.send_message(
        message.chat.id,
        f"✅ Записал!\n\n📝 <b>{text}</b>\n🕐 {remind_at.strftime('%d.%m.%Y %H:%M')}\nID: <code>{rid}</code>",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['note'])
def save_note(message):
    text = message.text.replace("/note", "").strip()
    if not text:
        bot.send_message(message.chat.id, "Напиши так: /note Купить хлеб")
        return
    
    add_note(message.from_user.id, text)
    bot.send_message(message.chat.id, "✅ Заметка сохранена!")

@bot.message_handler(commands=['notes'])
def show_notes(message):
    notes = get_notes(message.from_user.id)
    if not notes:
        bot.send_message(message.chat.id, "📭 Заметок нет.")
        return
    
    for nid, text in notes:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🗑 Удалить", callback_data=f"delnote_{nid}"))
        bot.send_message(message.chat.id, f"📒 {text}", reply_markup=markup)

@bot.message_handler(commands=['delnote'])
def remove_note(message):
    try:
        nid = int(message.text.split()[1])
        delete_note(nid)
        bot.send_message(message.chat.id, "🗑 Удалено.")
    except:
        bot.send_message(message.chat.id, "Напиши так: /delnote 1")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("done_", "delete_", "delnote_")))
def callback_actions(call):
    parts = call.data.split("_")
    action, rid = parts[0], int(parts[1])
    
    if action in ("done", "delete"):
        delete_reminder(rid)
        bot.edit_message_text("🗑 Дело удалено (или выполнено).", call.message.chat.id, call.message.message_id)
    elif action == "delnote":
        delete_note(rid)
        bot.edit_message_text("🗑 Заметка удалена.", call.message.chat.id, call.message.message_id)
        
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=reminder_worker, daemon=True).start()
    print("🚀 Бот NoteSbot запущен!")
    bot.infinity_polling()
