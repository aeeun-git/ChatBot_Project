
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from google.cloud import language_v2
from sentence_transformers import SentenceTransformer, util

# ▶ 환경 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Path\chatbot-454403-a78c4d9ba772.json"
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OpenAI API 키가 없습니다.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ▶ FastAPI 초기화
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

# ▶ 감정분석 결과 모델
class SentenceSentiment(BaseModel):
    text: str
    score: float
    magnitude: float

class SentimentData(BaseModel):
    document_score: float
    document_magnitude: float
    language: str
    sentences: list[SentenceSentiment]

# ▶ 요청/응답 모델
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    response: str
    sentiment: SentimentData | None
    action: dict | None

# ▶ 감정 분석
def analyze_sentiment(text: str) -> SentimentData:
    client_nlp = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}

    response = client_nlp.analyze_sentiment(request={"document": document, "encoding_type": language_v2.EncodingType.UTF8})

    sentences = [
        SentenceSentiment(
            text=s.text.content,
            score=s.sentiment.score,
            magnitude=s.sentiment.magnitude,
        ) for s in response.sentences
    ]

    return SentimentData(
        document_score=response.document_sentiment.score,
        document_magnitude=response.document_sentiment.magnitude,
        language=response.language_code,
        sentences=sentences,
    )

# ▶ 행동 정의 및 분류
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

action_candidates = {
    "wave_hand": ["안녕", "하이", "반가워요", "좋은 하루 보내"],
    "bow": ["고마워", "감사해요", "정말 고맙습니다"],
    "wave_goodbye": ["잘 가", "또 봐", "이만 가볼게"]
}

action_type_to_category = {
    "wave_hand": "인사",
    "bow": "감사",
    "wave_goodbye": "작별"
}

def detect_action(text: str):
    input_embedding = embedding_model.encode(text, convert_to_tensor=True)
    best_action, best_score = None, 0.0

    for action, phrases in action_candidates.items():
        phrase_embeddings = embedding_model.encode(phrases, convert_to_tensor=True)
        score = util.pytorch_cos_sim(input_embedding, phrase_embeddings).max().item()
        if score > best_score:
            best_score = score
            best_action = action

    return best_action, best_score

def determine_intensity(score: float, magnitude: float) -> str:
    if abs(score) >= 0.5 or magnitude >= 2.0:
        return "strong"
    elif abs(score) >= 0.2 or magnitude >= 1.0:
        return "normal"
    else:
        return "weak"

# ▶ /chat 엔드포인트
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    user_input = request.user_input
    print(f"👤 입력: {user_input}")

    try:
        sentiment_result = analyze_sentiment(user_input)
    except Exception as e:
        print(f"⚠️ 감정 분석 실패: {e}")
        sentiment_result = None

    messages = [
        {"role": "system", "content": "귀엽고 깝찍한 캐릭터야, 유쾌하고 재미있게 대화해줘"},
        *chat_history,
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        print(f"🤖 GPT 응답: {ai_response}")
    except Exception as e:
        print(f"❌ OpenAI 호출 실패: {e}")
        return {"response": "OpenAI API 호출 오류", "sentiment": sentiment_result, "action": None}

    # 대화 기록 저장
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": ai_response})

    # ▶ 행동 판단
    action_type, similarity = detect_action(user_input)
    intensity = determine_intensity(sentiment_result.document_score, sentiment_result.document_magnitude) if sentiment_result else "normal"
    category = action_type_to_category.get(action_type, "기타")

    return {
        "response": ai_response,
        "sentiment": sentiment_result,
        "action": {
            "type": action_type,
            "category": category,
            "intensity": intensity,
            "similarity_score": similarity
        }
    }