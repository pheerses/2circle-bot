from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.utils import executor
import asyncio
import os
from task_queue import enqueue_task, get_ready_task
from download_upload import download_video
from database import init_db, get_balance, decrement_balance

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    balance = (await get_balance(user_id))[0]
    
    if balance <= 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
            [InlineKeyboardButton(text="➕ Пополнить", callback_data="topup")]
        ])
        await message.reply("🚫 У тебя закончились кружочки. Пополни баланс, чтобы продолжить.", reply_markup=keyboard)
        return

    duration = message.video.duration
    if duration > 60:
        await message.reply("⚠️ Видео слишком длинное! Максимум — 1 минута.")
        return

    file_id = message.video.file_id
    file_path = await download_video(bot, file_id)
    output_path = file_path.replace("input", "output").replace(".mp4", "_out.mp4")

    await enqueue_task({
        "input_path": file_path,
        "output_path": output_path,
        "user_id": user_id,
        "chat_id": message.chat.id,
        "message_id": message.message_id
    })

    await message.reply("🎬 Видео принято, обработка началась!")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    balance, is_not_used = await get_balance(message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="➕ Пополнить", callback_data="topup")]
    ])
    if is_not_used:
        msg = "👋 Привет! Тебе выдано 10 бесплатных кружочков.\nОтправь мне видео и я пришлю тебе кружок!"
    elif balance == 0:
        msg = f"👋 Привет! У тебя {balance} кружочков.\nТебе нужно поплнить баланс, чтобы создать кружок из своего видео"
    else:
        msg = f"👋 Привет! У тебя {balance} кружочков.\nОтправь мне видео и я пришлю тебе кружок!"
    await message.answer(msg, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ["balance", "topup"])
async def callback_handler(call: types.CallbackQuery):
    if call.data == "balance":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Пополнить", callback_data="topup")]
        ])
        balance = (await get_balance(call.from_user.id))[0]
        await call.message.answer(f"💰 Осталось кружочков: {balance}", reply_markup=keyboard)
    elif call.data == "topup":
        await call.message.answer("Пополнение пока недоступно 🙈")
    await call.answer()


async def send_ready_videos():
    while True:
        task = get_ready_task()
        if task:
            try:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
                    [InlineKeyboardButton(text="➕ Пополнить", callback_data="topup")]
                ])
                await bot.send_video_note(
                    chat_id=task["chat_id"],
                    video_note=types.InputFile(task["output_path"]),
                    reply_to_message_id=task["message_id"],
                    reply_markup=keyboard
                )
                await decrement_balance(task["user_id"])
                print(f"Отправлено: {task['output_path']}, списан 1 кружочек")
            except Exception as e:
                print("Ошибка отправки видео:", e)
            finally:
                for path in [task["input_path"], task["output_path"]]:
                    if os.path.exists(path):
                        os.remove(path)
        await asyncio.sleep(1)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    async def main():
            await init_db()
            loop = asyncio.get_event_loop()
            loop.create_task(send_ready_videos())
            await dp.start_polling()

    asyncio.run(main())





