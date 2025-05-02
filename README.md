# 🤖 ChatBot_Project

<img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/> <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/> <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white"/>

간단한 **FastAPI** + **React** 기반 AI 채팅 애플리케이션.  
사용자는 톤(친구체/존댓말/비즈니스/상냥한 말투/화난 말투)을 버튼으로 선택해 AI와 대화할 수 있으며,  
과거 대화 기록(API) 조회, 키워드 기반 의도 분류, 3D 모델 애니메이션 연동 기능을 제공합니다.

## 📦 프로젝트 구조

chatbot\_API/
├── backend/                # FastAPI 서버
│   ├── main\_9.py           # 엔트리포인트
│   ├── text\_sql\_9.py       # DB(메시지 저장) 모듈
│   ├── text\_embed\_9.py     # HuggingFace intent 분류기 모듈
│   ├── requirements.txt    # Python dependencies
│   └── .env                # 환경 변수 (API 키, DB 설정)
└── frontend/               # React 클라이언트
├── public/
│   └── viewer.html     # 3D 모델 뷰어
├── src/
│   ├── App.jsx         # 메인 컴포넌트
│   ├── message.css     # 채팅 스타일
│   └── ...             # 기타 컴포넌트 및 설정 파일
└── package.json        # Node.js dependencies

## ⚙️ 설치 및 실행

### 1. 저장소 클론
git clone https://github.com/yourusername/ChatBot_Project.git
cd ChatBot_Project

### 2. 백엔드 설정

cd backend
# 가상환경 생성 & 활성화 (선택)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 (.env.example 참고)
# OPENAI_API_KEY=여러분의_OpenAI_API_키

### 3. 프론트엔드 설정

cd ../frontend
npm install

### 4. 서버 & 클라이언트 실행

* **백엔드** (포트 8000)

cd ../backend
uvicorn main_9:app --reload


* **프론트엔드** (포트 3000)

cd ../frontend
npm start

브라우저에서 `http://localhost:3000` 으로 접속하세요.

## 🚀 주요 기능

1. **톤(스타일) 선택**
   친구체, 존댓말, 비즈니스, 상냥한 말투, 화난 말투 등 버튼 클릭으로 시스템 프롬프트 변경
2. **대화 기록 조회**
   `/history` API 호출로 이전 대화 전체 리스트 반환
3. **의도 분류**
   HuggingFace Transformers 기반 간단 분류기로 “인사/작별/감사/칭찬/슬픔” 등 라벨링
4. **3D 모델 연동**
   인사·작별 의도 시 `postMessage("start-animation")` 로 viewer.html 내 애니메이션 트리거
5. **파일 로그 저장**
   'chat_log.txt` 에 사용자·AI 대화 기록을 매 대화마다 append


## 📡 API 명세

### POST `/chat`

* **Request**

  ```json
  {
    "user_input": "안녕?",
    "style": "친구체"
  }
  ```
* **Response**

  ```json
  {
    "response": "어이~ 잘 지냈어?",
    "intent": "인사"
  }
  ```

### GET `/history`

* **Response**

  ```json
  [
    { "id": 1, "speaker": "user",      "content": "안녕?",        "timestamp": "2025-05-02T10:00:00" },
    { "id": 2, "speaker": "assistant", "content": "어이~ 잘 지냈어?", "timestamp": "2025-05-02T10:00:01" },
    …
  ]
  ```

## 🔑 환경 변수

```dotenv
# OpenAI
OPENAI_API_KEY=여러분의_OpenAI_API_키

# (선택) MySQL 사용 시
# MYSQL_USER=
# MYSQL_PASSWORD=
# MYSQL_HOST=
# MYSQL_PORT=
# MYSQL_DB=
```

---

## 📝 라이선스

MIT © [aeeun](https://github.com/aeeun-git)
