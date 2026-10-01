import os
import asyncio
import threading

import duckdb
from flask import Flask
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_URL = (
    "https://huggingface.co/datasets/"
    "Cyber-insight-309/paytm/resolve/main/user.parquet"
)

# ---------------- HTTP SERVER ----------------

web = Flask(__name__)


@web.route("/")
def home():
    return "Cyber-Paytm Bot is running"


@web.route("/health")
def health():
    return "OK"


def run_web():
    port = int(os.getenv("PORT", "10000"))
    web.run(host="0.0.0.0", port=port)


# ---------------- DATABASE SEARCH ----------------

def search_mobile(mobile):
    con = duckdb.connect(":memory:")

    try:
        query = """
            SELECT *
            FROM read_parquet(?)
            WHERE CAST(mobile AS VARCHAR) = ?
            LIMIT 10
        """

        result = con.execute(query, [DATA_URL, mobile])

        columns = [column[0] for column in result.description]
        rows = result.fetchall()

        return columns, rows

    finally:
        con.close()


# ---------------- KEYBOARDS ----------------

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 Number Search",
                callback_data="search_number"
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍💻 Developer About",
                callback_data="developer_about"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------------- TELEGRAM BOT ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Cyber-Paytm Bot\n\n"
        "Niche button se option choose karo:",
        reply_markup=main_menu(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search_number":
        await query.message.reply_text(
            "🔎 Mobile number bhejo.\n\n"
            "Example: 9876543210"
        )

    elif query.data == "developer_about":
        about_text = (
            "👨‍💻 DEVELOPER ABOUT\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📱 Telegram: @cyber_insight_309\n"
            "📸 Instagram: cyber_insight_309\n\n"
            "🔗 Cyber Insight"
        )
        await query.message.reply_text(
            about_text,
            reply_markup=main_menu(),
        )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile = (update.message.text or "").strip()

    if not mobile.isdigit():
        await update.message.reply_text(
            "❌ Sirf mobile number bhejo.",
            reply_markup=main_menu(),
        )
        return

    status = await update.message.reply_text(
        "🔎 Searching..."
    )

    try:
        columns, rows = await asyncio.to_thread(
            search_mobile,
            mobile
        )

        if not rows:
            await status.edit_text(
                "❌ No result found.",
                reply_markup=main_menu(),
            )
            return

        row = rows[0]

        output = [
            "✅ RESULT FOUND",
            ""
        ]

        for column, value in zip(columns, row):
            if value is None:
                value = "null"

            output.append(
                f"{column}: {value}"
            )

        text = "\n".join(output)

        await status.delete()

        # Telegram message limit protection
        for i in range(0, len(text), 4000):
            await update.message.reply_text(
                text[i:i + 4000]
            )

        await update.message.reply_text(
            "🔄 Aur search karne ke liye button dabao:",
            reply_markup=main_menu(),
        )

    except Exception as error:
        await status.edit_text(
            f"❌ Search Error:\n{error}"
        )


# ---------------- MAIN ----------------

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    # Start HTTP server for Render
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search
        )
    )

    print("🤖 CYBER-PAYTM BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()
