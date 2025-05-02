// App.jsx (리액트 프론트엔드)

import React, { useState, useEffect, useRef } from "react";
import "./message.css";

function App() {
  const [userInput, setUserInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatBoxRef = useRef(null);
  const [currentIntent, setCurrentIntent] = useState(null);

  // 🎨 대화 스타일 상태
  const [style, setStyle] = useState("친구체");
  const stylesList = ["친구체", "존댓말", "비즈니스"];

  // ✅ 이전 채팅 기록 불러오기
  useEffect(() => {
    fetch("http://localhost:8000/history")
      .then((res) => res.json())
      .then((data) => {
        const formatted = data.map((msg) => ({
          role: msg.speaker === "user" ? "user" : "bot",
          text: msg.content,
          intent: msg.intent || null,
        }));
        setChatHistory(formatted);
      })
      .catch((err) => console.error("📛 이전 대화 불러오기 실패:", err));
  }, []);

  // ✅ 채팅창 자동 스크롤
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatHistory]);

  // ✅ 인사/작별 시 3D 모델 애니메이션 시작
  useEffect(() => {
    if (currentIntent === "인사" || currentIntent === "작별") {
      const iframe = document.getElementById("modelIframe");
      iframe?.contentWindow?.postMessage("start-animation", "*");
      console.log("📤 start-animation 메시지 보냄 (인사/작별)");
    }
  }, [currentIntent]);

  // ✅ 메시지 전송 핸들러
  const handleSend = async () => {
    if (!userInput.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput, style }),
      });

      const data = await res.json();
      setCurrentIntent(data.intent);

      setChatHistory((prev) => [
        ...prev,
        { role: "user", text: userInput },
        { role: "bot",  text: data.response, intent: data.intent || null },
      ]);
      setUserInput("");
    } catch (error) {
      console.error("❌ 서버 연결 실패:", error);
      setChatHistory((prev) => [
        ...prev,
        { role: "bot", text: "서버와 연결할 수 없습니다.", isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div style={styles.wrapper}>
      {/* 왼쪽 3D 모델 iframe */}
      <div style={styles.viewer}>
        <iframe
          id="modelIframe"
          src="/viewer.html"
          title="3D 캐릭터 뷰어"
          width="100%"
          height="100%"
          style={{ border: "none" }}
        />
      </div>

      {/* 오른쪽 채팅창 */}
      <div style={styles.chatArea}>
        <div style={styles.header}>LivelyAIChatbot</div>

        {/* 스타일 선택 버튼 */}
        <div style={styles.styleSelector}>
          {stylesList.map((s) => (
            <button
              key={s}
              onClick={() => setStyle(s)}
              style={{
                ...styles.styleButton,
                fontWeight: style === s ? "bold" : "normal",
              }}
            >
              {s}
            </button>
          ))}
        </div>

        <div style={styles.chatBox} ref={chatBoxRef}>
          {chatHistory.length === 0 ? (
            <p style={styles.placeholder}>대화를 시작하세요!</p>
          ) : (
            chatHistory.map((msg, i) => (
              <div
                key={i}
                className={
                  msg.isError
                    ? "errorMessage"
                    : msg.role === "user"
                    ? "userMessage"
                    : "botMessage"
                }
              >
                {msg.text}
                {msg.role === "bot" && msg.intent && (
                  <p style={styles.actionText}>📌 의도 분류: {msg.intent}</p>
                )}
              </div>
            ))
          )}
        </div>

        <div style={styles.inputContainer}>
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="메시지를 입력하세요..."
            style={styles.input}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            style={styles.button}
          >
            {loading ? "생각 중..." : "➤"}
          </button>
        </div>
      </div>
    </div>
  );
}

// 스타일 객체
const styles = {
  wrapper: {
    display: "flex",
    height: "100vh",
    fontFamily: "Arial, sans-serif",
  },
  viewer: {
    width: "50%",
    backgroundColor: "#f0f0f0",
  },
  chatArea: {
    width: "50%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-end",
    backgroundColor: "#f5f5f5",
    padding: "20px",
  },
  header: {
    fontSize: "20px",
    fontWeight: "bold",
    marginBottom: "10px",
    color: "#FF6666",
  },
  styleSelector: {
    display: "flex",
    gap: "8px",
    marginBottom: "10px",
  },
  styleButton: {
    padding: "6px 12px",
    borderRadius: "12px",
    border: "1px solid #ccc",
    cursor: "pointer",
    backgroundColor: "white",
  },
  chatBox: {
    flex: 1,
    overflowY: "auto",
    padding: "10px",
    backgroundColor: "#fff",
    borderRadius: "10px",
  },
  placeholder: {
    color: "#999",
    textAlign: "center",
    marginTop: "40%",
  },
  actionText: {
    fontSize: "12px",
    color: "#555",
    marginTop: "5px",
  },
  inputContainer: {
    display: "flex",
    marginTop: "10px",
  },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "20px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 15px",
    marginLeft: "10px",
    borderRadius: "20px",
    border: "none",
    backgroundColor: "#FF6666",
    color: "white",
    cursor: "pointer",
  },
};

export default App;
