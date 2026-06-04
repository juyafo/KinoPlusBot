from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import MovieService, UserService
from app.keyboards import user_main_menu
from app.utils import logger
from app.models import Movie

router = Router()

@router.message(F.text, ~F.text.startswith("/"))
async def search_movie(message: Message, session: AsyncSession, state: FSMContext):
    """Kino qidirish - kod + nomi bo'yicha"""
    try:
        query = message.text.strip()
        movie_service = MovieService(session)
        user_service = UserService(session)
        
        # 🌟 AVTOMATIK RO'YXATDAN O'TKAZISH (Muammoning yechimi)
        # Agar foydalanuvchi start bosmasdan to'g'ri kino kodini yozgan bo'lsa, xato bermasligi uchun bazaga qo'shamiz
        try:
            await user_service.register_user(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name or "Noma'lum",
                username=message.from_user.username
            )
        except Exception as db_err:
            # Agar allaqachon bazada bo'lsa unique xato berishi mumkin, uni o'tkazib yuboramiz
            pass

        # Kod bo'yicha qidiruv (3 xonali)
        if query.isdigit() and len(query) == 3:
            movie = await movie_service.get_movie_by_code(query)
            
            if not movie:
                await message.answer(
                    f"❌ Kod {query} topilmadi!\n\n"
                    "Boshqa kod kiritib ko'ring",
                    reply_markup=user_main_menu()
                )
                logger.warning(f"User {message.from_user.id} searched non-existent code {query}")
                return
            
            # Ko'rish tarixiga qo'shish
            await user_service.add_to_watch_history(message.from_user.id, movie.id)
            
            # Inline tugmalar
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="👍 Like", callback_data=f"like_{movie.id}"),
                    InlineKeyboardButton(text="👎 Dislike", callback_data=f"dislike_{movie.id}"),
                ],
                [
                    InlineKeyboardButton(text="⭐ Rating", callback_data=f"rate_{movie.id}"),
                    InlineKeyboardButton(text="❤️ Sevimli", callback_data=f"favorite_{movie.id}"),
                ],
            ])
            
            caption = (
                f"🎬 <b>{movie.title}</b>\n\n"
                f"👤 Rejissyori: {movie.director or 'Noma\'lum'}\n"
                f"📅 Yili: {movie.year or 'Noma\'lum'}\n"
                f"📂 Kategoriyasi: {movie.category or 'Noma\'lum'}\n"
                f"⭐ Reyting: {movie.rating:.1f}/5.0\n\n"
                f"📖 Tavsifi: {movie.description or 'Tavsif yo\'q'}"
            )
            
            await message.answer_video(
                video=movie.file_id,
                caption=caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            logger.info(f"User {message.from_user.id} watched movie {movie.id}")
        
        else:
            # Nomi bo'yicha qidiruv
            movies = await movie_service.search_by_title(query)
            
            if not movies:
                await message.answer(
                    f"❌ '{query}' nomi bo'yicha kino topilmadi!\n\n"
                    "Boshqa nomi kiritib ko'ring",
                    reply_markup=user_main_menu()
                )
                return
            
            # Birinchi 5 ta natija
            results_text = f"🔍 '{query}' bo'yicha {len(movies)} ta natija:\n\n"
            
            for i, movie in enumerate(movies[:5], 1):
                results_text += (
                    f"{i}. 🎬 <b>{movie.title}</b>\n"
                    f"   👤 {movie.director or 'Noma\'lum'}\n"
                    f"   📅 {movie.year or 'Noma\'lum'}\n"
                    f"   🔑 Kod: <code>{movie.code}</code>\n\n"
                )
            
            await message.answer(
                results_text + "Kino kodini kiritib ko'ring",
                reply_markup=user_main_menu(),
                parse_mode="HTML"
            )
            logger.info(f"User {message.from_user.id} searched by title: {query}")
            
    except Exception as e:
        logger.error(f"Error in search_movie: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi!",
            reply_markup=user_main_menu()
        )
