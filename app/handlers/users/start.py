from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import UserService
from app.keyboards import user_main_menu
from app.utils import logger
from app.filters import AdminFilter

router = Router()

@router.message(Command("start"), ~AdminFilter())
async def cmd_start(message: Message, session: AsyncSession):
    """Start command - faqat user uchun"""
    try:
        user_service = UserService(session)
        user = await user_service.register_user(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name or "Noma'lum",
            username=message.from_user.username
        )
        
        welcome_text = (
            f"👋 Salom, {user.full_name}!\n\n"
            f"🎬 Siz kino botiga xush kelibsiz!\n"
            f"Kino kodini (3 xonali raqam) kiritib kinolarni ko'ring\n\n"
            f"Misol: 123"
        )
        
        await message.answer(welcome_text, reply_markup=user_main_menu())
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        # Xatolik yuz berganda ham foydalanuvchiga javob qaytarish shart!
        await message.answer("❌ Tizimga ulanishda xatolik yuz berdi. Iltimos, qaytadan /start bosing!")
