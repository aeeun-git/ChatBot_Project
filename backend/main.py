from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

from text_sql_9 import Text_SQL
from text_embed_9 import TEXT_Embed
from security import get_password_by_username, user_exists

# 환경 설정
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OpenAI API 키가 없습니다.")
client = OpenAI(api_key=OPENAI_API_KEY)

# 클래스 인스턴스
db = Text_SQL()
embedder = TEXT_Embed()

# FastAPI 초기화
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ChatRequest(BaseModel):
    user_input: str
    system_prompt: str

class ChatResponse(BaseModel):
    response: str
    intent: str | None = None

# 텍스트 파일 저장
def save_chat_to_file(user_input: str, ai_response: str):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"👤 사용자: {user_input}\n")
        f.write(f"🤖 AI: {ai_response}\n")
        f.write("=" * 40 + "\n")

# /chat 엔드포인트


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        messages = [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content.strip()
        intent = embedder.classify_intent(ai_response)

        # 저장 (파일 + DB)
        save_chat_to_file(request.user_input, ai_response)
        db.save_message("user", request.user_input)
        db.save_message("assistant", ai_response)

        return {"response": ai_response, "intent": intent}
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return {"response": "서버 오류 발생", "intent": None}

# /history 엔드포인트
@app.get("/history")
def get_chat_history():
    try:
        return db.get_all_messages()
    except Exception as e:
        print(f"❌ 히스토리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="대화 기록 조회 오류")

# 🔐 사용자 인증 관련 임포트
from security import get_password_by_username, user_exists

# ✅ 사용자 로그인 요청 모델
class VerifyRequest(BaseModel):
    username: str
    password: str

# ✅ /verify 엔드포인트 추가
@app.post("/verify")
def verify_user(data: VerifyRequest):
    if not user_exists(data.username):
        return {"success": False, "reason": "not_found"}
    correct_pwd = get_password_by_username(data.username)
    if data.password == correct_pwd:
        return {"success": True}
    return {"success": False, "reason": "wrong_password"}

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register_user(request: RegisterRequest):
    try:
        exists = db.user_exists(request.username)
        if exists:
            raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
        success = db.add_user(request.username, request.password)
        if success:
            return {"message": f"{request.username}님, 가입을 환영합니다!"}
        else:
            raise HTTPException(status_code=500, detail="가입 실패. 서버 에러.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))