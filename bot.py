import asyncio
import requests
import re
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# 🔐 TOKEN (Render ENV dan olinadi)
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔘 Button
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Yangilash")]
    ],
    resize_keyboard=True
)

# 📊 Kurs olish
def get_rates():
    ton_data = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
    ).json()

    ton_usd = ton_data["the-open-network"]["usd"]

    usd_data = requests.get(
        "https://open.er-api.com/v6/latest/USD"
    ).json()

    usd_uzs = usd_data["rates"]["UZS"]

    ton_uzs = ton_usd * usd_uzs

    return ton_usd, ton_uzs, usd_uzs

# 🧠 Kalkulyator
def smart_calc(text, ton_usd, usd_uzs):
    text = text.lower()

    # TON hisob
    ton = re.search(r"([\d\.]+)\s*ton", text)
    if ton:
        amount = float(ton.group(1))
        return f"💰 {amount} TON ≈ {int(amount * ton_usd * usd_uzs)} so'm"

    # USD hisob
    usd = re.search(r"([\d\.]+)\s*usd", text)
    if usd:
        amount = float(usd.group(1))
        return f"💵 {amount} USD ≈ {int(amount * usd_uzs)} so'm"

    return None

# 🚀 START
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Bot ishga tushdi!\n💰 TON + USD kurs bot",
        reply_markup=keyboard
    )

# 🔄 BUTTON
@dp.message(F.text == "🔄 Yangilash")
async def refresh(message: Message):
    ton_usd, ton_uzs, usd_uzs = get_rates()

    await message.answer(
        f"💰 KRIPTO KURS\n\n"
        f"1 TON = {ton_usd}$\n"
        f"≈ {int(ton_uzs)} so'm\n\n"
        f"💵 1 USD = {usd_uzs} so'm"
    )

# 💬 MAIN HANDLER
@dp.message(F.text)
async def handler(message: Message):
    text = message.text.lower()

    ton_usd, ton_uzs, usd_uzs = get_rates()

    # kalkulyator (12 ton, 10 usd)
    result = smart_calc(text, ton_usd, usd_uzs)
    if result:
        await message.reply(result)
        return

    # oddiy TON
    if "ton" in text:
        await message.reply(
            f"💰 1 TON = {ton_usd}$\n≈ {int(ton_uzs)} so'm"
        )
        return

    # oddiy USD
    if "usd" in text:
        await message.reply(
            f"💵 1 USD = {usd_uzs} so'm"
        )

# ▶️ RUN
async def main():
    await dp.start_polling(bot)

asyncio.run(main())
