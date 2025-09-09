import logging
import requests
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Payment addresses (fill these later in your .env)
PAYMENT_ADDRESSES = {
    "Solana": os.getenv("SOL_ADDRESS", "YOUR_SOL_ADDRESS"),
    "Ethereum": os.getenv("ETH_ADDRESS", "YOUR_ETH_ADDRESS"),
    "BSC": os.getenv("BSC_ADDRESS", "YOUR_BSC_ADDRESS"),
    "SUI": os.getenv("SUI_ADDRESS", "YOUR_SUI_ADDRESS"),
    "XRP": os.getenv("XRP_ADDRESS", "YOUR_XRP_ADDRESS"),
}

# Base packages in SOL
PACKAGES = {
    "3 SOL – 3 hrs": 3,
    "9 SOL – 6 hrs": 9,
    "21 SOL – 15 hrs": 21,
    "50 SOL – 24 hrs": 50,
    "100 SOL – 48 hrs": 100,
}

# Initialize bot
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Temporary user data storage
user_data = {}

# --- Step 1: Start ---
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

# --- Step 2: Select chain ---
@dp.callback_query_handler(lambda c: c.data.startswith("chain_"))
async def process_chain(callback_query: types.CallbackQuery):
    chain = callback_query.data.split("_")[1]
    user_data[callback_query.from_user.id] = {"chain": chain}
    await bot.send_message(callback_query.from_user.id, f"✅ You selected {chain}.\n\nPlease enter the Contract Address (CA) of your project:")
    await callback_query.answer()

# --- Step 3: Receive CA ---
@dp.message_handler(lambda msg: msg.from_user.id in user_data and "ca" not in user_data[msg.from_user.id])
async def receive_ca(message: types.Message):
    user_data[message.from_user.id]["ca"] = message.text
    chain = user_data[message.from_user.id]["chain"]

    kb = InlineKeyboardMarkup(row_width=1)
    for package in PACKAGES.keys():
        kb.add(InlineKeyboardButton(package, callback_data=f"package_{package}"))

    await message.answer(f"✅ CA saved: `{message.text}`\n\nNow choose a package for {chain}:", parse_mode="Markdown", reply_markup=kb)

# --- Step 4: Select package ---
@dp.callback_query_handler(lambda c: c.data.startswith("package_"))
async def process_package(callback_query: types.CallbackQuery):
    package_name = callback_query.data.replace("package_", "")
    sol_amount = PACKAGES[package_name]
    chain = user_data[callback_query.from_user.id]["chain"]
    ca = user_data[callback_query.from_user.id]["ca"]

    # Show payment address
    address = PAYMENT_ADDRESSES.get(chain, "NO_ADDRESS_SET")

    await bot.send_message(
        callback_query.from_user.id,
        f"📝 Order summary:\n"
        f"- Chain: {chain}\n"
        f"- Project CA: `{ca}`\n"
        f"- Package: {package_name}\n\n"
        f"💳 Please send **{sol_amount} {('SOL' if chain == 'Solana' else chain)}** to:\n"
        f"`{address}`",
        parse_mode="Markdown",
    )
    await callback_query.answer()

# --- Run ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
