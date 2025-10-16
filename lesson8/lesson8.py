# unified_bot.py
# Python 3.10+
import os
import logging
import sqlite3
from datetime import datetime
from telebot import TeleBot, types

# === Настройки ===
TOKEN = "8323344573:AAHwigIa3iFxr2lAa4ZiYZIA8WB-2IYqR8E"
bot = TeleBot(TOKEN, parse_mode="HTML")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("unified-bot")

DB_PATH = "survey.db"

# === База данных (анкета) ===
def db_execute(query: str, params: tuple = ()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur

def init_db():
    db_execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        username TEXT,
        submitted_at TEXT NOT NULL,
        full_name TEXT,
        age INTEGER,
        city TEXT,
        legaltech_area TEXT,
        consent TEXT,
        comments TEXT
    )
    """)
    log.info("DB ready: %s", DB_PATH)

# === Справочник: тексты-заглушки ===
LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Donec non dolor a lorem sodales feugiat. Integer euismod sem et dictum posuere."
)

# === Простые состояния ===
STATE_DEFAULT = "DEFAULT"
STATE_SEARCH = "SEARCH"

# Анкета: шаги
STEP_NONE = 0
STEP_FULLNAME = 1
STEP_AGE = 2
STEP_CITY = 3
STEP_AREA = 4
STEP_CONSENT = 5
STEP_COMMENTS = 6

# Память состояний
user_state: dict[int, str] = {}     # chat_id -> state (справочник)
user_section: dict[int, str] = {}   # chat_id -> "SERVICES"/"FAQ"/"SURVEY" и т.п.
sessions: dict[int, dict] = {}      # анкета: chat_id -> {"step": int, "answers": {...}}

# === Кнопки ===
# Главное меню (справочник)
BTN_COMPANY = "🏢 О компании"
BTN_SERVICES = "🧰 Услуги"
BTN_FAQ = "❓ FAQ"
BTN_CONTACTS = "📞 Контакты"
BTN_SEARCH = "🔎 Поиск"
BTN_SURVEY = "🧩 Опрос"
BTN_MENU = "🏠 Меню"
BTN_BACK = "⬅️ Назад"

# Подменю «Услуги»
BTN_SVC_AUTOMATION = "⚙️ Автоматизация"
BTN_SVC_RISK = "📊 Риск-менеджмент"
BTN_SVC_CONTRACTS = "📝 Договоры"

# Подменю «FAQ»
BTN_FAQ_PRICES = "💵 Цены"
BTN_FAQ_DEADLINES = "⏱ Сроки"
BTN_FAQ_SUPPORT = "🧑‍💻 Поддержка"

# Подменю «Опрос»
BTN_SURVEY_START = "📝 Пройти опрос"
BTN_SURVEY_MY = "📄 Мои ответы"
BTN_SURVEY_DEL = "🗑 Удалить мои данные"
BTN_CANCEL = "❌ Отмена"

# Значения анкеты
AREA_A = "📚 Документооборот/шаблоны"
AREA_B = "⚖️ Судебная аналитика/RAG"
AREA_C = "🤖 Автоматизация и ИИ"
AREA_D = "🔐 Комплаенс/PDPA/GDPR"

CONSENT_YES = "✅ Согласен"
CONSENT_NO = "❎ Не согласен"

# === Клавиатуры ===
def kb_main() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(BTN_COMPANY),
        types.KeyboardButton(BTN_SERVICES),
        types.KeyboardButton(BTN_FAQ),
        types.KeyboardButton(BTN_CONTACTS),
        types.KeyboardButton(BTN_SEARCH),
        types.KeyboardButton(BTN_SURVEY),
    )
    return kb

def kb_back_only() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(BTN_BACK), types.KeyboardButton(BTN_MENU))
    return kb

def kb_services() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(BTN_SVC_AUTOMATION),
        types.KeyboardButton(BTN_SVC_RISK),
        types.KeyboardButton(BTN_SVC_CONTRACTS),
        types.KeyboardButton(BTN_BACK),
        types.KeyboardButton(BTN_MENU),
    )
    return kb

def kb_faq() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(BTN_FAQ_PRICES),
        types.KeyboardButton(BTN_FAQ_DEADLINES),
        types.KeyboardButton(BTN_FAQ_SUPPORT),
        types.KeyboardButton(BTN_BACK),
        types.KeyboardButton(BTN_MENU),
    )
    return kb

def kb_survey_menu() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(BTN_SURVEY_START),
        types.KeyboardButton(BTN_SURVEY_MY),
        types.KeyboardButton(BTN_SURVEY_DEL),
        types.KeyboardButton(BTN_BACK),
        types.KeyboardButton(BTN_MENU),
    )
    return kb

def kb_cancel() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(BTN_CANCEL), types.KeyboardButton(BTN_MENU))
    return kb

def kb_area() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(AREA_A),
        types.KeyboardButton(AREA_B),
        types.KeyboardButton(AREA_C),
        types.KeyboardButton(AREA_D),
        types.KeyboardButton(BTN_CANCEL),
        types.KeyboardButton(BTN_MENU),
    )
    return kb

def kb_consent() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(CONSENT_YES),
        types.KeyboardButton(CONSENT_NO),
        types.KeyboardButton(BTN_CANCEL),
        types.KeyboardButton(BTN_MENU),
    )
    return kb

# === Утилиты состояний ===
def set_state(chat_id: int, state: str) -> None:
    user_state[chat_id] = state

def get_state(chat_id: int) -> str:
    return user_state.get(chat_id, STATE_DEFAULT)

def set_section(chat_id: int, section: str | None) -> None:
    if section is None:
        user_section.pop(chat_id, None)
    else:
        user_section[chat_id] = section

def get_section(chat_id: int) -> str | None:
    return user_section.get(chat_id)

def to_main_menu(chat_id: int):
    set_state(chat_id, STATE_DEFAULT)
    set_section(chat_id, None)
    bot.send_message(chat_id, "🏠 <b>Главное меню</b>\nВыберите раздел:", reply_markup=kb_main())

# === Анкета: сессии ===
def start_session(chat_id: int):
    sessions[chat_id] = {"step": STEP_FULLNAME, "answers": {}}

def end_session(chat_id: int):
    sessions.pop(chat_id, None)

def get_step(chat_id: int) -> int:
    return sessions.get(chat_id, {}).get("step", STEP_NONE)

def set_step(chat_id: int, step: int):
    if chat_id in sessions:
        sessions[chat_id]["step"] = step

def set_answer(chat_id: int, key: str, value):
    if chat_id in sessions:
        sessions[chat_id]["answers"][key] = value

def save_submission(chat_id: int, username: str | None):
    s = sessions.get(chat_id)
    if not s:
        return
    a = s["answers"]
    db_execute(
        """
        INSERT INTO submissions (
            chat_id, username, submitted_at,
            full_name, age, city, legaltech_area, consent, comments
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            username or "",
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            a.get("full_name"),
            a.get("age"),
            a.get("city"),
            a.get("area"),
            a.get("consent"),
            a.get("comments"),
        ),
    )

def fetch_last_submission(chat_id: int):
    cur = db_execute(
        """
        SELECT id, submitted_at, full_name, age, city, legaltech_area, consent, comments
        FROM submissions
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (chat_id,),
    )
    return cur.fetchone()

def delete_all_for_user(chat_id: int) -> int:
    cur = db_execute("DELETE FROM submissions WHERE chat_id = ?", (chat_id,))
    return cur.rowcount

# === Команды старт/меню ===
@bot.message_handler(commands=["start", "menu"])
def on_start(message):
    init_db()
    bot.send_message(
        message.chat.id,
        "Привет! Это объединённый бот: справочник + анкета.\n"
        "Выберите раздел в меню ниже.",
        reply_markup=kb_main(),
    )

# === Навигация «Меню/Назад» ===
@bot.message_handler(func=lambda m: m.text == BTN_MENU)
def on_menu(message):
    to_main_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == BTN_BACK)
def on_back(message):
    chat_id = message.chat.id
    section = get_section(chat_id)
    if section == "SERVICES":
        bot.send_message(chat_id, "🧰 Услуги — выберите пункт:", reply_markup=kb_services())
    elif section == "FAQ":
        bot.send_message(chat_id, "❓ FAQ — выберите вопрос:", reply_markup=kb_faq())
    elif section == "SURVEY":
        bot.send_message(chat_id, "🧩 Раздел «Опрос» — выберите действие:", reply_markup=kb_survey_menu())
    else:
        to_main_menu(chat_id)

# === Справочник: главные разделы ===
@bot.message_handler(func=lambda m: m.text == BTN_COMPANY)
def on_company(message):
    set_section(message.chat.id, None)
    set_state(message.chat.id, STATE_DEFAULT)
    bot.send_message(message.chat.id, "🏢 <b>О компании</b>\n" + LOREM, reply_markup=kb_back_only())

@bot.message_handler(func=lambda m: m.text == BTN_SERVICES)
def on_services(message):
    set_section(message.chat.id, "SERVICES")
    set_state(message.chat.id, STATE_DEFAULT)
    bot.send_message(message.chat.id, "🧰 Услуги — выберите пункт:", reply_markup=kb_services())

@bot.message_handler(func=lambda m: m.text == BTN_FAQ)
def on_faq(message):
    set_section(message.chat.id, "FAQ")
    set_state(message.chat.id, STATE_DEFAULT)
    bot.send_message(message.chat.id, "❓ FAQ — выберите вопрос:", reply_markup=kb_faq())

@bot.message_handler(func=lambda m: m.text == BTN_CONTACTS)
def on_contacts(message):
    set_section(message.chat.id, None)
    set_state(message.chat.id, STATE_DEFAULT)
    bot.send_message(
        message.chat.id,
        "📞 <b>Контакты</b>\nEmail: contact@example.com\nТел.: +7 (999) 000-00-00\nАдрес: Москва, Ул. Примерная, 1",
        reply_markup=kb_back_only(),
    )

@bot.message_handler(func=lambda m: m.text == BTN_SEARCH)
def on_search(message):
    set_state(message.chat.id, STATE_SEARCH)
    bot.send_message(
        message.chat.id,
        "🔎 Введите поисковый запрос (например, «договор»). Для выхода — «Назад» или «Меню».",
        reply_markup=kb_back_only(),
    )

# Подменю «Услуги»
@bot.message_handler(func=lambda m: m.text in {BTN_SVC_AUTOMATION, BTN_SVC_RISK, BTN_SVC_CONTRACTS})
def on_services_items(message):
    set_section(message.chat.id, "SERVICES")
    texts = {
        BTN_SVC_AUTOMATION: "⚙️ <b>Автоматизация</b>\n" + LOREM,
        BTN_SVC_RISK: "📊 <b>Риск-менеджмент</b>\n" + LOREM,
        BTN_SVC_CONTRACTS: "📝 <b>Договоры</b>\n" + LOREM,
    }
    bot.send_message(message.chat.id, texts[message.text], reply_markup=kb_services())

# Подменю «FAQ»
@bot.message_handler(func=lambda m: m.text in {BTN_FAQ_PRICES, BTN_FAQ_DEADLINES, BTN_FAQ_SUPPORT})
def on_faq_items(message):
    set_section(message.chat.id, "FAQ")
    texts = {
        BTN_FAQ_PRICES: "💵 <b>Цены</b>\n" + LOREM,
        BTN_FAQ_DEADLINES: "⏱ <b>Сроки</b>\n" + LOREM,
        BTN_FAQ_SUPPORT: "🧑‍💻 <b>Поддержка</b>\n" + LOREM,
    }
    bot.send_message(message.chat.id, texts[message.text], reply_markup=kb_faq())

# === Раздел «Опрос» (меню) ===
@bot.message_handler(func=lambda m: m.text == BTN_SURVEY)
def on_survey(message):
    set_section(message.chat.id, "SURVEY")
    set_state(message.chat.id, STATE_DEFAULT)
    bot.send_message(message.chat.id, "🧩 Раздел «Опрос» — выберите действие:", reply_markup=kb_survey_menu())

# Действия раздела «Опрос»
@bot.message_handler(func=lambda m: m.text == BTN_SURVEY_START)
def on_survey_start(message):
    init_db()
    start_session(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Вопрос 1/5: Как Вас зовут? (ФИО или имя)",
        reply_markup=kb_cancel(),
    )

@bot.message_handler(func=lambda m: m.text == BTN_SURVEY_MY)
def on_survey_my(message):
    init_db()
    row = fetch_last_submission(message.chat.id)
    if not row:
        bot.send_message(message.chat.id, "Пока нет сохранённых ответов.", reply_markup=kb_survey_menu())
        return
    (sid, submitted_at, full_name, age, city, area, consent, comments) = row
    bot.send_message(
        message.chat.id,
        "<b>Ваши последние ответы</b>\n"
        f"ID записи: <code>{sid}</code>\n"
        f"Дата (UTC): {submitted_at}\n"
        f"Имя: {full_name or '—'}\n"
        f"Возраст: {age if age is not None else '—'}\n"
        f"Город: {city or '—'}\n"
        f"Зона интереса: {area or '—'}\n"
        f"Согласие: {consent or '—'}\n"
        f"Комментарий: {comments or '—'}",
        reply_markup=kb_survey_menu(),
    )

@bot.message_handler(func=lambda m: m.text == BTN_SURVEY_DEL)
def on_survey_del(message):
    init_db()
    count = delete_all_for_user(message.chat.id)
    bot.send_message(
        message.chat.id,
        f"Удалено записей: <b>{count}</b>.\nМожно пройти опрос заново.",
        reply_markup=kb_survey_menu(),
    )

@bot.message_handler(func=lambda m: m.text == BTN_CANCEL)
def on_cancel(message):
    end_session(message.chat.id)
    bot.send_message(message.chat.id, "Опрос отменён. Возвращаемся в раздел «Опрос».", reply_markup=kb_survey_menu())

# === Анкета: шаги ===
@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_FULLNAME)
def step_fullname(message):
    text = (message.text or "").strip()
    if not text or text in (BTN_CANCEL, BTN_MENU):
        return
    set_answer(message.chat.id, "full_name", text)
    set_step(message.chat.id, STEP_AGE)
    bot.send_message(message.chat.id, "Вопрос 2/5: Укажите возраст (числом).", reply_markup=kb_cancel())

@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_AGE)
def step_age(message):
    text = (message.text or "").strip()
    if not text or text in (BTN_CANCEL, BTN_MENU):
        return
    if not text.isdigit() or not (0 < int(text) < 120):
        bot.send_message(message.chat.id, "Пожалуйста, укажите возраст числом от 1 до 119.")
        return
    set_answer(message.chat.id, "age", int(text))
    set_step(message.chat.id, STEP_CITY)
    bot.send_message(message.chat.id, "Вопрос 3/5: В каком городе Вы находитесь?", reply_markup=kb_cancel())

@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_CITY)
def step_city(message):
    text = (message.text or "").strip()
    if not text or text in (BTN_CANCEL, BTN_MENU):
        return
    set_answer(message.chat.id, "city", text)
    set_step(message.chat.id, STEP_AREA)
    bot.send_message(message.chat.id, "Вопрос 4/5: Что из LegalTech интересует больше всего?", reply_markup=kb_area())

@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_AREA)
def step_area(message):
    if message.text not in {AREA_A, AREA_B, AREA_C, AREA_D}:
        bot.send_message(message.chat.id, "Выберите вариант на клавиатуре ниже.", reply_markup=kb_area())
        return
    set_answer(message.chat.id, "area", message.text)
    set_step(message.chat.id, STEP_CONSENT)
    bot.send_message(message.chat.id, "Вопрос 5/5: Согласны на обработку ответов для учебных целей?", reply_markup=kb_consent())

@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_CONSENT)
def step_consent(message):
    if message.text not in {CONSENT_YES, CONSENT_NO}:
        bot.send_message(message.chat.id, "Выберите «Согласен» или «Не согласен».", reply_markup=kb_consent())
        return
    set_answer(message.chat.id, "consent", message.text)
    set_step(message.chat.id, STEP_COMMENTS)
    bot.send_message(message.chat.id, "Финально: добавьте комментарий (по желанию) или напишите «—».", reply_markup=kb_cancel())

@bot.message_handler(func=lambda m: get_step(m.chat.id) == STEP_COMMENTS)
def step_comments(message):
    text = (message.text or "").strip()
    if not text:
        return
    set_answer(message.chat.id, "comments", None if text in {"-", "—"} else text)
    save_submission(message.chat.id, message.from_user.username if message.from_user else None)
    end_session(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Спасибо! ✅ Ваши ответы сохранены.\nИх можно посмотреть в «📄 Мои ответы».",
        reply_markup=kb_survey_menu(),
    )

# === Обработка поиска (справочник) и фоллбек ===
@bot.message_handler(func=lambda m: True)
def on_any_text(message):
    chat_id = message.chat.id
    if get_state(chat_id) == STATE_SEARCH:
        query = (message.text or "").strip()
        bot.send_message(
            chat_id,
            f"🔍 Результаты по «<b>{types.html.escape(query)}</b>»:\n"
            f"• {LOREM}\n• {LOREM}\n• {LOREM}",
            reply_markup=kb_back_only(),
        )
        return

    # Если идёт опрос — просим ответить в рамках шага
    if get_step(chat_id) != STEP_NONE:
        bot.send_message(chat_id, "Пожалуйста, ответьте на текущий вопрос или нажмите «Отмена».")
        return

    # Иначе подскажем про меню
    bot.send_message(chat_id, "Выберите пункт в меню ниже или нажмите «Меню».", reply_markup=kb_main())

if __name__ == "__main__":
    init_db()
    if TOKEN == "YOUR_TOKEN_HERE":
        log.warning("Пожалуйста, вставьте токен бота (env TELEGRAM_BOT_TOKEN или константа TOKEN).")
    log.info("Bot is polling...")
    bot.infinity_polling(skip_pending=True, timeout=30)