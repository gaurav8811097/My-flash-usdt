from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)

BOT_TOKEN = 8384357405:AAFIwvG8MtdpGzB3waC8GYHeJoOKZjXO_QQ

# States
LANGUAGE, PAYMENT_METHOD, DEAL_AMOUNT, WALLET, DESCRIPTION, CONFIRM = range(6)

# Temporary user data storage
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select your language:", reply_markup=reply_markup)
    return LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("TON Wallet 💎", callback_data="method_ton")],
        [InlineKeyboardButton("Stars 🌟", callback_data="method_stars")],
        [InlineKeyboardButton("USDT 💰", callback_data="method_usdt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose payment receipt method:", reply_markup=reply_markup)
    return PAYMENT_METHOD

async def choose_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method = query.data.split("_")[1]
    context.user_data["method"] = method.upper()

    if method == "stars":
        await query.edit_message_text(
            "💼 Creating a deal\nEnter the deal amount in Stars in format: 100.5"
        )
    else:
        await query.edit_message_text(
            f"🔑 Add your {method.upper()} wallet:\nPlease send your wallet address"
        )
    return DEAL_AMOUNT if method == "stars" else WALLET

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text
    method = context.user_data.get("method")

    if method == "STARS":
        await update.message.reply_text(
            f"📝 Specify what you offer in this deal for {update.message.text} Stars:\nExample: 10 Caps and Pepe..."
        )
        return DESCRIPTION
    else:
        await update.message.reply_text("🔑 Add your TON wallet:\nPlease send your wallet address")
        return WALLET

async def get_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wallet"] = update.message.text
    method = context.user_data.get("method")

    if method == "USDT":
        await update.message.reply_text(
            "💼 Creating a deal\nEnter the deal amount in USDT in format: 100.5"
        )
        return DEAL_AMOUNT
    else:
        await update.message.reply_text(
            "📝 Specify what you offer in this deal:\nExample: 10 Caps and Pepe..."
        )
        return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    amount = context.user_data.get("amount", "100.0")
    method = context.user_data.get("method", "STARS")

    context.user_data["description"] = description

    text = (
        f"✅ Deal successfully created!\n"
        f"💰 Amount: {amount} {method}\n"
        f"📜 Description: {description}\n"
        f"🔗 Link for buyer: https://t.me/NexusGiftRobobot?start=f6atvhpidq"
    )

    keyboard = [[InlineKeyboardButton("❌ Cancel Deal", callback_data="cancel_deal")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def cancel_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Deal #f6atvhpidq has been canceled.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process canceled.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(select_language, pattern="^lang_")],
            PAYMENT_METHOD: [CallbackQueryHandler(choose_method, pattern="^method_")],
            DEAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            CONFIRM: [CallbackQueryHandler(cancel_deal, pattern="^cancel_deal$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

