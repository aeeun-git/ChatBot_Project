# app.py (FastAPI 백엔드)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional

from openai import OpenAI
from dotenv import load_dotenv
import os

from text_sql_9 import Text_SQL
from text_embed_9 import TEXT_Embed

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
    # 선택 가능한 스타일을 제한
    style: Optional[Literal["친구체", "존댓말", "비즈니스"]] = "친구체"

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None

# 스타일별 시스템 프롬프트 매핑
STYLE_PROMPTS = {
    "친구체":   "너는 나의 친구야. 반말로 유쾌하게 대답해줘.",
    "존댓말":   "너는 나의 어시스턴트야. 공손하고 정중하게 대답해줘.",
    "비즈니스": "너는 전문 컨설턴트야. 비즈니스 어투로 간결하게 답변해줘."
}

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
        system_prompt = STYLE_PROMPTS.get(request.style, STYLE_PROMPTS["친구체"])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": request.user_input}
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
        raise HTTPException(status_code=500, detail="서버 오류 발생")

# /history 엔드포인트
@app.get("/history")
def get_chat_history():
    try:
        return db.get_all_messages()
    except Exception as e:
        print(f"❌ 히스토리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="대화 기록 조회 오류")
