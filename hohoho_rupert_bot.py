import asyncio
import logging
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher, types
import os
from dotenv import load_dotenv
from aiogram import F
from handlers import begin
from misc import recognise

openai_key = os.getenv("OPENAI_API_KEY")

language = 'ru'

load_dotenv()
TelegramToken = os.getenv("TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TelegramToken)
dp = Dispatcher()

dp.include_router(begin.router)

client = AsyncOpenAI(
    api_key=openai_key
)
bot_name = "masterbot"
personage = "Дед Мороз"


@dp.message(F.voice)
async def converting_audio(message: types.Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    current_directory = os.getcwd()
    audio_directory = os.path.join(current_directory, "AUDIO/")
    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory)
    audio_path = audio_directory + "audio.ogg"
    audio_path_full_converted = audio_directory + "audio.wav"
    await bot.download_file(file_path, audio_path)
    os.system("ffmpeg -i " + audio_path + "  " + audio_path_full_converted)
    text = recognise(audio_path_full_converted)
    os.remove(audio_path)
    os.remove(audio_path_full_converted)
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    gpt_reply = chat_completion.choices[0].message.content
    await message.answer(gpt_reply)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
