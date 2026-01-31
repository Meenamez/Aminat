import os
import logging
import random
import string
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8443))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

# State definitions for conversation
ASKING_ADDRESS, = range(1)

# User trading state storage (in production, use a database)
user_states: Dict[int, bool] = {}

def generate_wallet_address():
    """Generate a random ETH-like wallet address"""
    chars = string.ascii_lowercase + string.digits
    return '0x' + ''.join(random.choice(chars) for _ in range(40))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with buttons"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data='deposit'),
            InlineKeyboardButton("📈 Trade", callback_data='trade')
        ],
        [
            InlineKeyboardButton("⏯️ Start/Stop Trading", callback_data='toggle_trading'),
            InlineKeyboardButton("💸 Withdraw", callback_data='withdraw')
        ],
        [
            InlineKeyboardButton("📊 Balance", callback_data='balance')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *Welcome to ETH Demo Trading Bot*\n\n"
        "Select an option below to get started:\n"
        "• Deposit: Get ETH deposit address\n"
        "• Trade: Execute demo trades\n"
        "• Start/Stop: Control trading\n"
        "• Withdraw: Withdraw profits\n"
        "• Balance: Check your balance\n\n"
        "_This is a demo trading bot for educational purposes only._",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'deposit':
        wallet_address = generate_wallet_address()
        await query.edit_message_text(
            f"📍 *ETH Deposit Address*\n\n"
            f"`{wallet_address}`\n\n"
            f"✅ Send ETH to this address to fund your account.\n"
            f"⚠️ Only send ETH to this address.\n\n"
            f"_Demo address - Not a real wallet_",
            parse_mode='Markdown'
        )
    
    elif query.data == 'trade':
        # Simulate trade execution
        trade_id = ''.join(random.choices(string.digits, k=8))
        profit_loss = random.uniform(-50, 150)
        
        if profit_loss > 0:
            message = f"✅ *Trade Executed Successfully!*\n\nTrade ID: `{trade_id}`\nProfit: +${profit_loss:.2f}\n\n_Hurry! I'm going into the ETH market now to make more profit for you!_ 🚀"
        else:
            message = f"⚠️ *Trade Executed with Loss*\n\nTrade ID: `{trade_id}`\nLoss: ${abs(profit_loss):.2f}\n\n_Market conditions are challenging. I'll adjust the strategy._"
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    elif query.data == 'toggle_trading':
        # Toggle trading state for user
        if user_id not in user_states:
            user_states[user_id] = False
        
        user_states[user_id] = not user_states[user_id]
        status = "ACTIVE 🟢" if user_states[user_id] else "STOPPED 🔴"
        
        await query.edit_message_text(
            f"🔄 *Trading Status Updated*\n\n"
            f"Status: **{status}**\n\n"
            f"Trading has been {'started' if user_states[user_id] else 'stopped'}.\n"
            f"Your bot is now {'actively trading' if user_states[user_id] else 'inactive'}.",
            parse_mode='Markdown'
        )
    
    elif query.data == 'withdraw':
        await query.edit_message_text(
            "💳 *Withdraw ETH*\n\n"
            "Please enter your Ethereum wallet address to withdraw 10 ETH profit:\n\n"
            "Format: `0x...` (42 characters)\n"
            "_Example: 0x71C7656EC7ab88b098defB751B7401B5f6d8976F_",
            parse_mode='Markdown'
        )
        return ASKING_ADDRESS
    
    elif query.data == 'balance':
        # Generate demo balance
        eth_balance = round(random.uniform(0.5, 5.0), 4)
        usd_value = eth_balance * random.uniform(1800, 2200)
        profit = random.uniform(0, 2.5)
        
        await query.edit_message_text(
            f"📊 *Account Balance*\n\n"
            f"• ETH Balance: `{eth_balance:.4f} ETH`\n"
            f"• USD Value: `${usd_value:.2f}`\n"
            f"• Total Profit: `{profit:.4f} ETH`\n"
            f"• Account Status: `ACTIVE`\n\n"
            f"_Demo balances - Not real funds_",
            parse_mode='Markdown'
        )

async def handle_withdraw_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ETH address input for withdrawal"""
    eth_address = update.message.text.strip()
    
    # Simple ETH address validation
    if not (eth_address.startswith('0x') and len(eth_address) == 42):
        await update.message.reply_text(
            "❌ Invalid ETH address format. Please enter a valid Ethereum address starting with '0x' (42 characters total).\n\n"
            "Try again:"
        )
        return ASKING_ADDRESS
    
    # Generate transaction hash
    tx_hash = '0x' + ''.join(random.choices(string.hexdigits.lower(), k=64))
    
    await update.message.reply_text(
        f"🎉 *Withdrawal Successful!*\n\n"
        f"✅ 10 ETH profit is coming your way!\n\n"
        f"• Recipient: `{eth_address[:10]}...{eth_address[-8:]}`\n"
        f"• Amount: 10 ETH\n"
        f"• Transaction: [{tx_hash[:16]}...](https://etherscan.io/tx/{tx_hash})\n"
        f"• Estimated Time: 5-10 minutes\n\n"
        f"_Congratulations! Your profit will arrive soon._ 🚀\n"
        f"_Note: This is a demo transaction._",
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    # Show main menu again
    await start(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Operation cancelled.")
    await start(update, context)
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await update.message.reply_text(
        "🤖 *ETH Demo Trading Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/balance - Check your balance\n"
        "/status - Check trading status\n\n"
        "*Features:*\n"
        "• Demo ETH trading simulation\n"
        "• Virtual deposit/withdrawal\n"
        "• Trading start/stop control\n"
        "• Balance tracking\n\n"
        "_This is an educational demo only._",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check trading status"""
    user_id = update.effective_user.id
    status = user_states.get(user_id, False)
    
    await update.message.reply_text(
        f"📈 *Trading Status*\n\n"
        f"Status: {'🟢 ACTIVE' if status else '🔴 STOPPED'}\n"
        f"User ID: `{user_id}`\n"
        f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"_Use Start/Stop button to control trading._",
        parse_mode='Markdown'
    )

def main():
    """Start the bot"""
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for withdrawal
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='withdraw')],
        states={
            ASKING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("balance", button_handler))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start the bot
    if WEBHOOK_URL:
        # Webhook mode for Render
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        # Polling mode for development
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
