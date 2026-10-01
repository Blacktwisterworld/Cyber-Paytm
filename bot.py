import os
import asyncio
import duckdb
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_URL = "https://huggingface.co/datasets/Cyber-insight-309/paytm/resolve/main/user.parquet"


def search_mobile(mobile):
    con = duckdb.connect(":memory:")

    try:
        query = """
        SELECT *
        FROM read_parquet(?)
        WHERE mobile = ?
        LIMIT 10
        """

        result = con.execute(query, [DATA_URL, mobile])
        columns = [x[0] for x in result.description]
        rows = result.fetchall()

        return columns, rows

    finally:
        con.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 Mobile number bhejo.\n\n"
        "Example: 9876543210"
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile = update.message.text.strip()

    if not mobile.isdigit():
        await update.message.reply_text(
            "❌ Sirf mobile number bhejo."
        )
        return

    msg = await update.message.reply_text("🔎 Searching...")

    try:
        columns, rows = await asyncio.to_thread(
            search_mobile,
            mobile
        )

        if not rows:
            await msg.edit_text("❌ No result found.")
            return

        row = rows[0]

        output = ["✅ RESULT FOUND", ""]

        for column, value in zip(columns, row):
            if value is None:
                value = "null"

            output.append(f"{column}: {value}")

        text = "\n".join(output)

        await msg.delete()

        # Telegram message limit protection
        for i in range(0, len(text), 4000):
            await update.message.reply_text(text[i:i + 4000])

    except Exception as e:
        await msg.edit_text(
            f"❌ Error:\n{str(e)}"
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable missing"
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search
        )
    )

    print("🤖 BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()
