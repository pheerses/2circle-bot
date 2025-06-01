import os
from aiogram import Bot
from aiogram.types import InputFile
import uuid

async def download_video(bot: Bot, file_id: str) -> str:
    file = await bot.get_file(file_id)
    name = str(uuid.uuid4())
    os.makedirs("media/input", exist_ok=True)
    file_path = f"media/input/{name}.mp4"
    await bot.download_file(file.file_path, destination=file_path)
    return file_path

