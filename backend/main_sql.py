from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# ✅ .env 파일 로드 및 OpenAI 키 설정
load_dotenv("env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OpenAI API 키가 설정되지 않았습니다.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ FastAPI 앱 설정
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MySQL 연결 정보
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rlaehdrjs0820")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "chat_db")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ 대화 메시지 저장 테이블
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    speaker = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ✅ 요청/응답 모델 정의
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    response: str

# ✅ 대화 로그 파일 저장
def save_chat_to_file(user_input: str, ai_response: str):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"👤 사용자: {user_input}\n")
        f.write(f"🤖 AI: {ai_response}\n")
        f.write("=" * 40 + "\n")

# ✅ 챗봇 대화 처리 API
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        user_input = request.user_input

        messages = [
            {"role": "system", "content": "귀엽고 깝찍한 캐릭터야~ 유쾌하게 대화해줘!"},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        # ✅ 텍스트 파일 저장
        save_chat_to_file(user_input, ai_response)

        # ✅ DB 저장
        with SessionLocal() as db:
            db.add(ChatMessage(speaker="user", content=user_input))
            db.add(ChatMessage(speaker="assistant", content=ai_response))
            db.commit()

        return {"response": ai_response}

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return {"response": "오류 발생: 대화 처리 중 문제 발생"}

# ✅ /history API - 이전 대화 전체 불러오기
@app.get("/history")
def get_chat_history():
    with SessionLocal() as db:
        messages = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
        return [
            {
                "speaker": msg.speaker,
                "content": msg.content,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for msg in messages
        ]
