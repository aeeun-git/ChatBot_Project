from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# ▼ 추가: 구글 감정분석 라이브러리
from google.cloud import language_v2

# (1) Google 서비스 계정 키 환경변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Path\chatbot-454403-a78c4d9ba772.json"

# (2) .env 파일 로드
load_dotenv()

# (3) OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

# (4) 구버전 OpenAI 클라이언트 초기화 (옛날 방식)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 대화 기록 저장 (전역 변수)
chat_history = []

# (A) 감정분석 결과를 담을 모델 정의
class SentenceSentiment(BaseModel):
    text: str
    score: float
    magnitude: float

class SentimentData(BaseModel):
    document_score: float
    document_magnitude: float
    language: str
    sentences: list[SentenceSentiment]

# (B) 요청/응답 데이터 모델
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    response: str
    sentiment: SentimentData | None

# (C) 구글 감정분석 함수
def analyze_sentiment(text: str) -> SentimentData:
    """
    Google Cloud Natural Language API를 이용해
    text에 대한 감정분석 결과를 SentimentData 형태로 반환.
    """
    client_nlp = language_v2.LanguageServiceClient()

    document = {
        "content": text,
        "type_": language_v2.Document.Type.PLAIN_TEXT,
    }

    response = client_nlp.analyze_sentiment(
        request={"document": document, "encoding_type": language_v2.EncodingType.UTF8}
    )

    doc_score = response.document_sentiment.score
    doc_magnitude = response.document_sentiment.magnitude
    language = response.language_code

    sentences_list = []
    for s in response.sentences:
        sentences_list.append(
            SentenceSentiment(
                text=s.text.content,
                score=s.sentiment.score,
                magnitude=s.sentiment.magnitude
            )
        )

    return SentimentData(
        document_score=doc_score,
        document_magnitude=doc_magnitude,
        language=language,
        sentences=sentences_list
    )

# (D) OpenAI + 감정분석 통합 엔드포인트
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    1) 사용자 입력에 대해 Google 감정분석
    2) OpenAI (구버전: client.chat.completions.create) 호출
    3) 결과(모델 응답 + 감정분석)를 반환
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다.")

    try:
        user_input = request.user_input
        print(f"👤 사용자 입력: {user_input}")

        # (1) 구글 감정분석
        try:
            sentiment_result = analyze_sentiment(user_input)
            print(f"💬 감정분석 결과: {sentiment_result}")
        except Exception as e:
            print(f"⚠️ 감정분석 실패: {e}")
            sentiment_result = None

        # (2) 이전 대화 기록 + 이번 메시지를 포함한 messages 생성
        messages = [
            {"role": "system", "content": "귀엽고 깝찍한 캐릭터야, 유쾌하고 재미있게 대화해줘"}
        ]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_input})

        # (3) OpenAI 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        print(f"🤖 OpenAI 응답: {ai_response}")

        # (4) 대화 기록 갱신
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": ai_response})

        # (5) 반환 (모델 응답 + 감정분석 결과)
        return {
            "response": ai_response,
            "sentiment": sentiment_result
        }

    except Exception as e:
        print(f"❌ OpenAI API 호출 오류: {e}")
        return {
            "response": "오류 발생: OpenAI API를 사용할 수 없습니다.",
            "sentiment": None
        }
