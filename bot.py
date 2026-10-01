import os
import asyncio
import threading

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


# ---------------- MENU ----------------

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 Search Number",
                callback_data="search_number"
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍💻 Developer",
                callback_data="developer"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "╔══════════════════════════╗\n"
        "       🤖 CYBER-PAYTM\n"
        "╚══════════════════════════╝\n\n"
        "Welcome! 👋\n\n"
        "Please select an option:",
        reply_markup=main_menu()
    )


# ---------------- BUTTON HANDLER ----------------

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if query.data == "search_number":

        await query.edit_message_text(
            "🔎 SEARCH NUMBER\n\n"
            "📱 Please send the mobile number."
        )

    elif query.data == "developer":

        await query.edit_message_text(
            "╔══════════════════════════╗\n"
            "       👨‍💻 DEVELOPER\n"
            "╚══════════════════════════╝\n\n"
            "📱 Telegram\n"
            "@cyber_insight_309\n\n"
            "📸 Instagram\n"
            "cyber_insight_309\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Cyber-Paytm"
        )


# ---------------- NUMBER HANDLER ----------------

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mobile = (update.message.text or "").strip()

    if not mobile.isdigit():
        await update.message.reply_text(
            "❌ Invalid input.\n\n"
            "Please send a valid mobile number."
        )
        return

    status = await update.message.reply_text(
        "🔎 Searching...\n"
        "Please wait."
    )

    try:
        # ------------------------------------------------
        # YAHAN APNA EXISTING SEARCH FUNCTION CALL KARO
        # ------------------------------------------------
        #
        # columns, rows = await asyncio.to_thread(
        #     search_mobile,
        #     mobile
        # )
        #
        # ------------------------------------------------

        # Temporary placeholder
        columns = []
        rows = []

        if not rows:
            await status.edit_text(
                "❌ NO RESULT FOUND\n\n"
                f"📱 Number: {mobile}"
            )
            return

        row = rows[0]

        output = [
            "╔══════════════════════════╗",
            "       🔎 SEARCH RESULT",
            "╚══════════════════════════╝",
            "",
        ]

        for column, value in zip(columns, row):

            if value is None:
                value = "null"

            label = column.replace("_", " ").title()

            output.append(f"🔹 {label}")
            output.append(f"   {value}")
            output.append("")

        # ---------------- CREDIT ----------------

        output.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            "👨‍💻 Developer",
            "Telegram: @cyber_insight_309",
            "Instagram: cyber_insight_309",
            "━━━━━━━━━━━━━━━━━━━━",
            "🤖 Cyber-Paytm"
        ])

        text = "\n".join(output)

        await status.delete()

        # Telegram message limit
        for i in range(0, len(text), 4000):
            await update.message.reply_text(
                text[i:i + 4000]
            )

    except Exception as error:

        await status.edit_text(
            "❌ SEARCH ERROR\n\n"
            "Something went wrong."
        )

        print(error)


# ---------------- MAIN ----------------

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

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
