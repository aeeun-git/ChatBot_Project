import React, { useState } from "react";
import "./login.css";

const knownUsers = ["hohoyeol", "minji"];

function Login({ onLoginSuccess }) {
  const [step, setStep] = useState("welcome");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [attempts, setAttempts] = useState(0);
  const [loginError, setLoginError] = useState(null);

  const handleNameSubmit = () => {
    if (knownUsers.includes(name)) {
      setStep("checkName");
    } else {
      if (attempts >= 1) {
        setStep("newUser");
      } else {
        setStep("unknownName");
        setAttempts(attempts + 1);
      }
    }
  };

  const handleFirstTimeClick = () => {
    setStep("newUser");
  };

  const handlePasswordSubmit = async () => {
    try {
      const res = await fetch("http://localhost:8000/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: name, password }),
      });
      const data = await res.json();
      if (data.success) {
        onLoginSuccess(name);
      } else {
        setLoginError(data.reason === "wrong_password" ? "❌ 비밀번호가 틀렸어요." : "❌ 사용자 없음");
      }
    } catch (err) {
      setLoginError("❌ 서버 오류 발생");
    }
  };

  const renderContent = () => {
    switch (step) {
      case "welcome":
        return (
          <>
            <p>안녕하세요!<br />반가워요!</p>
            <p>처음 오셨으면 저를 눌러주세요!</p>
            <button onClick={handleFirstTimeClick}>👋 처음이에요</button>
            <p>다시 오시나요?<br />이름을 알려주세요!</p>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="이름 입력"
            />
            <button onClick={handleNameSubmit}>다음</button>
          </>
        );
      case "checkName":
        return (
          <>
            <p>{name}님 반가워요!</p>
            <p>비밀번호는요?</p>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호 입력"
            />
            <button onClick={handlePasswordSubmit}>확인</button>
            {loginError && <p style={{ color: "red" }}>{loginError}</p>}
          </>
        );
      case "unknownName":
        return (
          <>
            <p>음... 모르는 이름이에요.</p>
            <p>다시 확인해주시겠어요?</p>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="이름 다시 입력"
            />
            <button onClick={handleNameSubmit}>확인</button>
          </>
        );
      case "newUser":
        return (
          <>
            <p>우리 처음 만나네요!<br />반가워요!!</p>
            <p>이름을 알려주시겠어요?</p>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="새 이름 입력"
            />
            <button onClick={() => setStep("checkName")}>확인</button>
          </>
        );
      default:
        return <p>오류 발생</p>;
    }
  };

  return (
    <div className="login-wrapper">
      <div className="login-box">
        {renderContent()}
      </div>
    </div>
  );
}

export default Login;
