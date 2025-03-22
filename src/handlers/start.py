from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start_handler(msg: types.Message):
    await msg.answer(text=f'Hello, {msg.from_user.first_name}')
