import asyncio
import logging

from aiogram.types import FSInputFile
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher, types
import os
from dotenv import load_dotenv
from aiogram import F
from handlers import begin
from misc import recognise, check_message, picture
from sql_intergrate import get_or_create_user, increase_counter, get_prompt, update_prompt

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


# @dp.message(F.voice)
# async def converting_audio(message: types.Message):
#     file_id = message.voice.file_id
#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#     current_directory = os.getcwd()
#     audio_directory = os.path.join(current_directory, "AUDIO/")
#     if not os.path.exists(audio_directory):
#         os.makedirs(audio_directory)
#     audio_path = audio_directory + "audio.ogg"
#     audio_path_full_converted = audio_directory + "audio.wav"
#     await bot.download_file(file_path, audio_path)
#     os.system("ffmpeg -i " + audio_path + "  " + audio_path_full_converted)
#     text = recognise(audio_path_full_converted)
#     os.remove(audio_path)
#     os.remove(audio_path_full_converted)
#     chat_completion = await client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": text,
#             }
#         ],
#         model="gpt-3.5-turbo",
#     )
#     gpt_reply = chat_completion.choices[0].message.content
#     await message.answer(gpt_reply)
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
    user_id = message.from_user.id
    user = get_or_create_user(user_id, bot_name)
    counter = user.counter
    if counter < 20:
        # counter += 1
        user_text = text
        message_status = check_message(user_text)
        if message_status == "good":
            increase_counter(user_id)
            old_prompt = get_prompt(user_id)
            prompt = "Ты " + personage + ", настоящий, все по канону. На все вопросы отвечаешь, как если бы ты был " \
                                         "им. Важно — тебе могут писать дети,и ты обязан соблюдать возрастное " \
                                         "ограничение PG-13. Стараешься давать им добрые, хорошие советы и пожелания, " \
                                         "даже если они пишут грубости. Прредыдущий разговор был такой '" + old_prompt + \
                     "', учти это но на старые вопросы не отвыечай, а теперь отвечай  на новый вопрос с учетом предыдущего диалого. Новый вопрос " + user_text

            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )
            gpt_reply = chat_completion.choices[0].message.content
            update_prompt(user_id, user_text)
            await message.answer(gpt_reply)
        elif message_status == "bad_word":
            increase_counter(user_id)
            text = "Не ругайся, маленький шалунишка"
            await message.answer(text)
        elif message_status == "too long":
            text = "Охохо, ты совсем запутал старенького дедушку, давай покороче"
            await message.answer(text)
            increase_counter(user_id)
    elif counter == 20:
        text = "Ну вот и поговорили достаточно. Время идти дальше, столько дел перед праздниками!"
        old_prompt = get_prompt(user_id)
        content = "Ты " + personage + ", настоящий, все по канону. Предыдущие темы разговора'" + old_prompt + "' Возьми из них основные три темы волнующие собеседника и нарисуй на основании их картинку"
        filepath = await picture(content, user_id)
        cat = FSInputFile(filepath)
        await message.answer_photo(cat)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при удалении файла: {str(e)}")
        await message.answer(text)
        increase_counter(user_id)
    elif counter > 20:
        increase_counter(user_id)
        message.answer("С Новым Годом мой маленький друг")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
