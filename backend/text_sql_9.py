import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# .env 로드
load_dotenv()

# 환경변수로부터 DB 접속 정보 읽어오기
MYSQL_USER     = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "aeeun")       # 수정된 비밀번호
MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB       = os.getenv("MYSQL_DB", "chat_db")

# MySQL 연결 URL
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# SQLAlchemy 세팅
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 테이블 모델
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    speaker    = Column(String(10), nullable=False)
    content    = Column(Text,   nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# DB 조작 클래스
class Text_SQL:
    def __init__(self):
        self.SessionLocal = SessionLocal

    def save_message(self, speaker: str, content: str):
        with self.SessionLocal() as session:
            msg = ChatMessage(speaker=speaker, content=content)
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg

    def get_all_messages(self):
        with self.SessionLocal() as session:
            messages = (
                session
                .query(ChatMessage)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )
            return [
                {
                    "speaker":    m.speaker,
                    "content":    m.content,
                    "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                for m in messages
            ]
