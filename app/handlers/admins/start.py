from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import os
from app.keyboards import admin_main_menu
from app.utils import logger

router = Router()

@router.message(Command("start"))
async def admin_start(message: Message):
    """Admin start tekshiruvi"""
    try:
        # Render Environment Variables ichidagi ADMIN_ID ni o'qiymiz
        admin_id_env = os.getenv('ADMIN_ID', '0')
        
        # Logdagi haqiqiy ID bilan solishtiramiz
        if str(message.from_user.id) == str(admin_id_env).strip():
            admin_text = (
                "👨‍💼 Admin panelga xush kelibsiz!\n\n"
                "Pastdagi tugmalardan foydalaning:"
            )
            await message.answer(admin_text, reply_markup=admin_main_menu())
            logger.info(f"Admin {message.from_user.id} tizimga kirdi")
            return  # Admin topildi, pastdagi foydalanuvchi startiga o'tmaydi!
            
    except Exception as e:
        logger.error(f"Error in admin start: {e}")
        
    # Agar admin bo'lmasa, bu handler ishlamaydi va avtomatik 
    # ravishda users/start.py ishga tushib ketadi (propagate bo'ladi).
