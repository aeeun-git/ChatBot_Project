# 🤖 LivelyAI ChatBot

<img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/> <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/> <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white"/>

**LivelyAI ChatBot**은 FastAPI와 React를 기반으로 한 AI 대화 애플리케이션입니다.
사용자는 버튼 클릭만으로 '친구체', '존댓말', '비즈니스', '상냥한 말투', '화난 말투' 등 다양한 말투를 선택해 대화할 수 있으며,
백엔드에서는 OpenAI GPT 모델에 선택된 스타일을 반영한 시스템 프롬프트를 전달합니다.

---

## 🛠 주요 기능

* **대화 스타일 선택**
  다섯 가지 톤(말투) 버튼을 통해 AI의 응답 스타일을 실시간 변경
* **실시간 채팅**
  React 프론트엔드에서 입력 → FastAPI 백엔드로 POST → OpenAI 응답 → 화면 출력
* **의도 분류**
  간단한 텍스트 분류기로 결과 응답에 "인사/작별/감사/칭찬/슬픔" 등의 라벨 표시
* **대화 기록 저장 & 조회**
  SQLite/MySQL에 사용자·AI 메시지 저장, '/history' API로 전체 로그 반환
* **3D 캐릭터 연동**
  "인사" 혹은 "작별" 의도 시 iframe 내 3D 모델 애니메이션 자동 재생

---

## ⚙️ 아키텍처 & 디렉토리 구조

```
chatbot_API/
├─ backend/                  FastAPI 서버
│   ├─ main.py               API 엔드포인트 정의
│   ├─ text_sql.py           DB 모델 & 메시지 저장·조회 로직
│   ├─ text_embed.py         HuggingFace 분류기 로드·사용 모듈
│   ├─ requirements.txt      Python 패키지 목록
│   └─ .env                  환경 변수 (OPENAI_API_KEY, DB 정보)
└─ frontend/                 React 클라이언트
    ├─ public/
    │   └─ viewer.html       3D 캐릭터 뷰어
    ├─ src/
    │   ├─ App.jsx           메인 컴포넌트
    │   ├─ message.css       채팅 인터페이스 스타일
    │   └─ ...               기타 컴포넌트
    └─ package.json          Node.js 패키지 목록
```

---

## 🚀 빠른 시작

1. **리포지터리 클론**

   ```bash
   git clone https://github.com/yourusername/LivelyAI-ChatBot.git
   cd LivelyAI-ChatBot
   ```

2. **백엔드 설정**

   ```bash
   cd backend
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate

   pip install -r requirements.txt

   # .env 파일 생성
   echo OPENAI_API_KEY=your_openai_api_key > .env
   ```

3. **프론트엔드 설정**

   ```bash
   cd ../frontend
   npm install
   ```

4. **서버 & 클라이언트 실행**

   * **백엔드**

     ```bash
     cd ../backend
     uvicorn main:app --reload
     ```

   * **프론트엔드**

     ```bash
     cd ../frontend
     npm start
     ```

---

## 📡 API 명세

### POST '/chat'

* **Request Body**

  ```json
  {
    "user_input": "안녕하세요!",
    "style": "상냥한 말투"
  }
  ```
* **Response Body**

  ```json
  {
    "response": "안녕하세요! 오늘 기분은 어떠신가요?",
    "intent": "인사"
  }
  ```

### GET `/history`

* **Response Body**

  ```json
  [
    {
      "id": 1,
      "speaker": "user",
      "content": "안녕하세요!",
      "timestamp": "2025-05-02T12:34:56"
    },
    {
      "id": 2,
      "speaker": "assistant",
      "content": "안녕하세요! 오늘 기분은 어떠신가요?",
      "timestamp": "2025-05-02T12:34:57"
    }
    // …
  ]
  ```

---

## 🧰 기술 스택

* **백엔드**: Python, FastAPI, SQLAlchemy, SQLite/MySQL
* **AI**: OpenAI GPT-3.5-turbo, HuggingFace Transformers
* **프론트엔드**: React, CSS
* **3D 뷰어**: HTML iframe → Unity/Blender Exported Model

---

## 📝 라이선스

MIT © [aeeun](https://github.com/aeeun-git)

---
