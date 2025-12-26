from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DataTime, ForeignKey, Integer
from sqlalchemy.sql import func
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# URL Connect
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    creator_id: Mapped[str] = mapped_column(String, index=True)
    video_created_at: Mapped[datetime.datetime] =  mapped_column(DateTime(timezone=True))

    views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    like_count: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, dafault=0)

    created_at: Mapped[datetime.detetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    shapshots = relationship("VideoShapshot", back_populates="video",cascade="all, delete-orphan")

    class VideoSnapshot(Base):
        __tablename__ = 'video_shapshots'

        id: Mapped[str] = mapped_column[String, primary_key=True]
        video_id: Mapped[str] = mapped_column(ForeignKey('video.id', ondelete='CASCADE'), index=True)

        view_count: Mapped[int] = mapped_column(BigInteger)
        likes_count: Mapped[int] = mapped_column(BigInteger)
        comment_count: Mapped[int] = mapped_column(BigInteger)
        reports_count: Mapped[int] = mapped_column(BigInteger)

        delta_views_count: Mapped[int] = mapped_column(BigInteger)
        delta_likes_count: Mapped[int] = mapped_column(BigInteger)
        delta_comments_count: Mapped[int] = mapped_column(BigInteger)
        delta_reports_countL: Mapped[int] = mapped_column(BigInteger)

        create_at: Mapped[datetime.detetime] = mapped_column(DateTime(timezone=True))
        updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

        video = relationship("Video", back_populates="snapshots")

    async def init_db():
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)



