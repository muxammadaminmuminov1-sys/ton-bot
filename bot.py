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
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

# 🔐 TOKEN
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔘 Keyboard
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Yangilash")]
    ],
    resize_keyboard=True
)

# 🔘 INLINE START
start_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Start", callback_data="start")]
    ]
)

# 📊 KURS
def get_rates():
    try:
        ton_data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd",
            timeout=10
        ).json()

        ton_usd = ton_data.get("the-open-network", {}).get("usd")

        usd_data = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10
        ).json()

        usd_uzs = usd_data["rates"]["UZS"]

        ton_uzs = ton_usd * usd_uzs

        return ton_usd, ton_uzs, usd_uzs

    except:
        return None, None, None


# 🧠 CALC
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


# 🚀 START
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Xush kelibsiz!\n💰 TON + USD bot",
        reply_markup=keyboard
    )

    await message.answer(
        "👇 Start bosing",
        reply_markup=start_inline
    )


# 🚀 INLINE START
@dp.callback_query(F.data == "start")
async def start_btn(call: CallbackQuery):
    await call.message.answer(
        "🚀 Bot ishga tushdi!\nTON yoki USD yozing",
        reply_markup=keyboard
    )


# 🔄 YANGILASH (FAKAT KURS)
@dp.message(F.text == "🔄 Yangilash")
async def refresh(message: Message):
    ton_usd, ton_uzs, usd_uzs = get_rates()

    if not ton_usd:
        await message.answer("❌ Kurs yuklanmadi")
        return

    # ⚠️ FAqat TON + USD kurs
    await message.answer(
        f"📊 LIVE KURS\n\n"
        f"1 TON = {ton_usd}$\n"
        f"≈ {int(ton_uzs)} so'm\n\n"
        f"1 USD = {usd_uzs} so'm"
    )


# 💬 MESSAGE HANDLER
@dp.message(F.text)
async def handler(message: Message):
    text = message.text.lower()

    ton_usd, ton_uzs, usd_uzs = get_rates()

    if not ton_usd:
        await message.reply("❌ API muammo")
        return

    # calculator
    result = smart_calc(text, ton_usd, usd_uzs)
    if result:
        await message.reply(result)
        return

    # simple TON
    if "ton" in text:
        await message.reply(
            f"💰 1 TON = {ton_usd}$\n≈ {int(ton_uzs)} so'm"
        )
        return

    # simple USD
    if "usd" in text:
        await message.reply(
            f"💵 1 USD = {usd_uzs} so'm"
        )


# ▶️ RUN FIXED
async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
