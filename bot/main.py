from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram.utils import executor
import asyncio
import os
from task_queue import enqueue_task, get_ready_task
from download_upload import download_video

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_video(message: types.Message):
    duration = message.video.duration
    if duration > 60:
        await message.reply("⚠️ Видео слишком длинное! Максимум — 1 минута.")
        return

    file_id = message.video.file_id
    file_path = await download_video(bot, file_id, message.video.file_unique_id)
    output_path = file_path.replace("input", "output").replace(".mp4", "_out.mp4")

    await enqueue_task({
        "input_path": file_path,
        "output_path": output_path,
        "user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "message_id": message.message_id
    })

    await message.reply("Видео принято, обработка началась!")


async def send_ready_videos():
    while True:
        task = get_ready_task()
        if task:
            try:
                await bot.send_video_note(
                    chat_id=task["chat_id"],
                    video_note=types.InputFile(task["output_path"]),
                    reply_to_message_id=task["message_id"]
                )
                print(f"Отправлено: {task['output_path']}")
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

    loop = asyncio.get_event_loop()
    loop.create_task(send_ready_videos())
    executor.start_polling(dp, skip_updates=True)



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    loop = asyncio.get_event_loop()
    loop.create_task(send_ready_videos())
    executor.start_polling(dp, skip_updates=True)



