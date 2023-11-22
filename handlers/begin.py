import os
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from openai import AsyncOpenAI
from aiogram.filters import Command
from dotenv import load_dotenv
from misc import help_message, picture
from sql_intergrate import get_or_create_user

router = Router()
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

language = 'ru'


@router.message(Command("start"))
async def process_start_command(message: types.Message):
    await message.answer(" Хо - хо - хо, как себя вели в этом году, детишки? Хорошо? ❄️❄️⛄️❄️❄️")


@router.message(Command("help"))
async def process_help_command(message: types.Message):
    await message.answer(help_message)


client = AsyncOpenAI(
    api_key=openai_key
)


# @router.message(Command("pic"))
# async def pic_test(message: types.Message):
#     content = "Веселый новый год"
#     path = await picture(content)
#     cat = FSInputFile(path)
#     await message.answer_photo(cat)


@router.message(F.text)
async def message_response(message: types.Message):
    user_id = message.from_user.id
    user = get_or_create_user(user_id)
    counter = user.counter
    if counter < 20:
        user_text = message.text
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model="gpt-3.5-turbo",
        )
        gpt_reply = chat_completion.choices[0].message.content
        await message.answer(gpt_reply)
    elif counter == 20 :
        content = "Веселый новый год"
        path = await picture(content)
        cat = FSInputFile(path)
        await message.answer_photo(cat)
    else:
        message.answer("С Новым Годом мой маленький друг")
