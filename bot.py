import asyncio
import requests
import re
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command

# 🔐 TOKEN (Render ENV)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔘 Reply keyboard (bottom button)
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Yangilash")]
    ],
    resize_keyboard=True
)

# 🔘 Inline START button (tapada chiqadi)
start_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Start", callback_data="start")]
    ]
)

# 📊 Kurs olish
def get_rates():
    try:
        ton_data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd",
            timeout=10
        ).json()

        ton_usd = ton_data["the-open-network"]["usd"]

        usd_data = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10
        ).json()

        usd_uzs = usd_data["rates"]["UZS"]

        ton_uzs = ton_usd * usd_uzs

        return ton_usd, ton_uzs, usd_uzs

    except:
        return 0, 0, 0

# 🧠 Kalkulyator
def smart_calc(text, ton_usd, usd_uzs):
    text = text.lower()

    ton = re.search(r"([\d\.]+)\s*ton", text)
    if ton:
        amount = float(ton.group(1))
        return f"💰 {amount} TON ≈ {int(amount * ton_usd * usd_uzs)} so'm"

    usd = re.search(r"([\d\.]+)\s*usd", text)
    if usd:
        amount = float(usd.group(1))
        return f"💵 {amount} USD ≈ {int(amount * usd_uzs)} so'm"

    return None

# 🚀 /start command
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Xush kelibsiz!\n💰 TON + USD live kurs bot",
        reply_markup=keyboard
    )

    await message.answer(
        "👇 Boshlash uchun tugmani bosing:",
        reply_markup=start_inline
    )

# 🚀 INLINE START BUTTON CLICK
@dp.callback_query(F.data == "start")
async def start_btn(call):
    await call.message.answer(
        "🚀 Bot ishga tushdi!\nEndi TON yoki USD yozing",
        reply_markup=keyboard
    )

# 🔄 UPDATE BUTTON
@dp.message(F.text == "🔄 Yangilash")
async def refresh(message: Message):
    ton_usd, ton_uzs, usd_uzs = get_rates()

    if ton_usd == 0:
        await message.answer("❌ Kurs yuklanmadi")
        return

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

    if ton_usd == 0:
        await message.reply("❌ Internet yoki API muammo")
        return

    result = smart_calc(text, ton_usd, usd_uzs)
    if result:
        await message.reply(result)
        return

    if "ton" in text:
        await message.reply(
            f"💰 1 TON = {ton_usd}$\n≈ {int(ton_uzs)} so'm"
        )
        return

    if "usd" in text:
        await message.reply(
            f"💵 1 USD = {usd_uzs} so'm"
        )

# ▶️ RUN
async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
