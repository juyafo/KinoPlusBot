from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from .base import Base

class UserMovie(Base):
    """Foydalanuvchining kino ko'rish tarixi"""
    __tablename__ = "user_movies"
    
    id = Column(Integer, primary_key=True)
    # INTEGER o'rniga BigInteger qilindi, chunki bu yerga Telegram ID yoki katta ID kirishi mumkin
    user_id = Column(BigInteger, nullable=False) 
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    comment = Column(Text, nullable=True)
    is_favorite = Column(String(10), default="no", nullable=False)

class UserNotification(Base):
    """Foydalanuvchi bildirishnomalari"""
    __tablename__ = "user_notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False) # Bu ham BigInteger qilindi
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
