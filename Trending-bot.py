import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Payment addresses (fill these in your .env)
PAYMENT_ADDRESSES = {
    "Solana": os.getenv("SOL_ADDRESS", "YOUR_SOL_ADDRESS"),
    "Ethereum": os.getenv("ETH_ADDRESS", "YOUR_ETH_ADDRESS"),
    "BSC": os.getenv("BSC_ADDRESS", "YOUR_BSC_ADDRESS"),
    "SUI": os.getenv("SUI_ADDRESS", "YOUR_SUI_ADDRESS"),
    "XRP": os.getenv("XRP_ADDRESS", "YOUR_XRP_ADDRESS"),
}

# Separate packages for each chain
PACKAGES = {
    "Solana": {
        "3 SOL – 3 hrs": "3 SOL",
        "9 SOL – 6 hrs": "9 SOL",
        "21 SOL – 15 hrs": "21 SOL",
        "50 SOL – 24 hrs": "50 SOL",
        "100 SOL – 48 hrs": "100 SOL",
    },
    "Ethereum": {
        "0.15 ETH – 3 hrs": "0.15 ETH",
        "0.45 ETH – 6 hrs": "0.45 ETH",
        "1.06 ETH – 15 hrs": "1.06 ETH",
        "2.52 ETH – 24 hrs": "2.52 ETH",
        "5.05 ETH – 48 hrs": "5.05 ETH",
    },
    "BSC": {
        "0.75 BNB – 3 hrs": "0.75 BNB",
        "2.24 BNB – 6 hrs": "2.24 BNB",
        "5.22 BNB – 15 hrs": "5.22 BNB",
        "12.43 BNB – 24 hrs": "12.43 BNB",
        "24.9 BNB – 48 hrs": "24.9 BNB",
    },
    "SUI": {
        "183 SUI – 3 hrs": "183 SUI",
        "549 SUI – 6 hrs": "549 SUI",
        "1279 SUI – 15 hrs": "1279 SUI",
        "3047 SUI – 24 hrs": "3047 SUI",
        "6094 SUI – 48 hrs": "6094 SUI",
    },
    "XRP": {
        "221 XRP – 3 hrs": "221 XRP",
        "663 XRP – 6 hrs": "663 XRP",
        "1546 XRP – 15 hrs": "1546 XRP",
        "3680 XRP – 24 hrs": "3680 XRP",
        "7361 XRP – 48 hrs": "7361 XRP",
    },
}

# Initialize bot
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Temporary user storage
user_data = {}

# --- Start ---
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Solana", callback_data="chain_Solana"),
        InlineKeyboardButton("Ethereum", callback_data="chain_Ethereum"),
        InlineKeyboardButton("BSC", callback_data="chain_BSC"),
        InlineKeyboardButton("SUI", callback_data="chain_SUI"),
        InlineKeyboardButton("XRP", callback_data="chain_XRP"),
    )
    await message.answer("👋 Welcome! Choose your blockchain network:", reply_markup=kb)

# --- Select chain ---
@dp.callback_query_handler(lambda c: c.data.startswith("chain_"))
async def process_chain(callback_query: types.CallbackQuery):
    chain = callback_query.data.split("_")[1]
    user_data[callback_query.from_user.id] = {"chain": chain}
    await bot.send_message(callback_query.from_user.id, f"✅ You selected {chain}.\n\nPlease enter the Contract Address (CA) of your project:")
    await callback_query.answer()

# --- Receive CA ---
@dp.message_handler(lambda msg: msg.from_user.id in user_data and "ca" not in user_data[msg.from_user.id])
async def receive_ca(message: types.Message):
    user_data[message.from_user.id]["ca"] = message.text
    chain = user_data[message.from_user.id]["chain"]

    kb = InlineKeyboardMarkup(row_width=1)
    for package in PACKAGES[chain].keys():
        kb.add(InlineKeyboardButton(package, callback_data=f"package_{package}"))

    await message.answer(f"✅ CA saved: `{message.text}`\n\nNow choose a package for {chain}:", parse_mode="Markdown", reply_markup=kb)

# --- Select package ---
@dp.callback_query_handler(lambda c: c.data.startswith("package_"))
async def process_package(callback_query: types.CallbackQuery):
    package_name = callback_query.data.replace("package_", "")
    user_id = callback_query.from_user.id
    chain = user_data[user_id]["chain"]
    ca = user_data[user_id]["ca"]

    token_amount = PACKAGES[chain][package_name]
    address = PAYMENT_ADDRESSES.get(chain, "NO_ADDRESS_SET")

    await bot.send_message(
        user_id,
        f"📝 Order summary:\n"
        f"- Chain: {chain}\n"
        f"- Project CA: `{ca}`\n"
        f"- Package: {package_name}\n\n"
        f"💳 Please send **{token_amount}** to:\n"
        f"`{address}`",
        parse_mode="Markdown",
    )
    await callback_query.answer()

# --- Run bot ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
