from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Формируем URL подключения
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# --- МОДЕЛИ (Строго по ТЗ) ---

class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[str] = mapped_column(String, primary_key=True)  # ID может быть строкой (YouTube ID и т.д.)
    creator_id: Mapped[str] = mapped_column(String, index=True)
    video_created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    # Финальные метрики
    views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    likes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(),
                                                          server_default=func.now())

    # Связь для удобства (хотя в raw SQL запросах от LLM она не нужна, но нам пригодится)
    snapshots = relationship("VideoSnapshot", back_populates="video", cascade="all, delete-orphan")


class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey('videos.id', ondelete='CASCADE'), index=True)

    # Текущие значения
    views_count: Mapped[int] = mapped_column(BigInteger)
    likes_count: Mapped[int] = mapped_column(BigInteger)
    comments_count: Mapped[int] = mapped_column(BigInteger)
    reports_count: Mapped[int] = mapped_column(BigInteger)

    # Дельты (прирост)
    delta_views_count: Mapped[int] = mapped_column(BigInteger)
    delta_likes_count: Mapped[int] = mapped_column(BigInteger)
    delta_comments_count: Mapped[int] = mapped_column(BigInteger)
    delta_reports_count: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))  # Время замера
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="snapshots")


# Функция инициализации БД (создание таблиц)
async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Раскомментируй, если надо пересоздать
        await conn.run_sync(Base.metadata.create_all)
