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

# =========================================================
# HTTP SERVER
# =========================================================

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


# =========================================================
# DATABASE SEARCH
# =========================================================

def search_mobile(mobile):
    con = duckdb.connect(":memory:")

    try:
        query = """
            SELECT *
            FROM read_parquet(?)
            WHERE CAST(mobile AS VARCHAR) = ?
            LIMIT 10
        """

        result = con.execute(
            query,
            [DATA_URL, mobile]
        )

        columns = [
            column[0]
            for column in result.description
        ]

        rows = result.fetchall()

        return columns, rows

    finally:
        con.close()


# =========================================================
# MAIN MENU
# =========================================================

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


# =========================================================
# START COMMAND
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "╔══════════════════════════╗\n"
        "       🤖 CYBER-PAYTM\n"
        "╚══════════════════════════╝\n\n"
        "Welcome! 👋\n\n"
        "Select an option below:",
        reply_markup=main_menu()
    )


# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "search_number":

        await query.edit_message_text(
            "╔══════════════════════════╗\n"
            "       🔎 SEARCH NUMBER\n"
            "╚══════════════════════════╝\n\n"
            "📱 Please send the mobile number."
        )

    elif query.data == "developer":

        await query.edit_message_text(
            "╔══════════════════════════╗\n"
            "        👨‍💻 DEVELOPER\n"
            "╚══════════════════════════╝\n\n"
            "📱 Telegram\n"
            "@cyber_insight_309\n\n"
            "📸 Instagram\n"
            "cyber_insight_309\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Cyber-Paytm"
        )


# =========================================================
# NUMBER SEARCH
# =========================================================

async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    mobile = (update.message.text or "").strip()

    if not mobile.isdigit():

        await update.message.reply_text(
            "❌ INVALID INPUT\n\n"
            "Please send a valid mobile number."
        )

        return

    status = await update.message.reply_text(
        "🔎 Searching...\n"
        "Please wait."
    )

    try:

        # IMPORTANT:
        # Actual database search happens here.

        columns, rows = await asyncio.to_thread(
            search_mobile,
            mobile
        )

        # -------------------------------------------------
        # NO RESULT
        # -------------------------------------------------

        if not rows:

            await status.edit_text(
                "╔══════════════════════════╗\n"
                "        ❌ NO RESULT\n"
                "╚══════════════════════════╝\n\n"
                f"📱 Number: {mobile}\n\n"
                "No matching record was found."
            )

            return

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        output = [
            "╔══════════════════════════╗",
            "        🔎 SEARCH RESULT",
            "╚══════════════════════════╝",
            "",
            f"📱 Number: {mobile}",
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            ""
        ]

        row = rows[0]

        for column, value in zip(columns, row):

            if value is None:
                value = "null"

            label = column.replace(
                "_",
                " "
            ).title()

            output.append(
                f"🔹 {label}"
            )

            output.append(
                f"   {value}"
            )

            output.append("")

        # -------------------------------------------------
        # CREDIT
        # -------------------------------------------------

        output.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            "",
            "👨‍💻 Developer",
            "📱 Telegram: @cyber_insight_309",
            "📸 Instagram: cyber_insight_309",
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "🤖 Cyber-Paytm"
        ])

        text = "\n".join(output)

        await status.delete()

        # -------------------------------------------------
        # TELEGRAM MESSAGE LIMIT
        # -------------------------------------------------

        for i in range(
            0,
            len(text),
            4000
        ):

            await update.message.reply_text(
                text[i:i + 4000]
            )

    except Exception as error:

        print(
            "SEARCH ERROR:",
            error
        )

        await status.edit_text(
            "╔══════════════════════════╗\n"
            "        ❌ SEARCH ERROR\n"
            "╚══════════════════════════╝\n\n"
            "Something went wrong while searching.\n\n"
            "Please try again."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    # Start Render HTTP server
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Buttons
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Mobile number
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search
        )
    )

    print(
        "🤖 CYBER-PAYTM BOT ONLINE"
    )

    app.run_polling()


if __name__ == "__main__":
    main()
