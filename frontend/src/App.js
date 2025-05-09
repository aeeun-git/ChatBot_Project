import React, { useState } from "react";
import Login from "./Login";
import Chat from "./Chat";
import PersonaSelect from "./PersonaSelect"; // 새 컴포넌트

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  if (!isLoggedIn) {
    return <Login onLoginSuccess={(name) => {
      setUserName(name);
      setIsLoggedIn(true);
    }} />;
  }

  if (!systemPrompt) {
    return <PersonaSelect onSelect={setSystemPrompt} />;
  }

  return <Chat user={userName} systemPrompt={systemPrompt} />;
}

export default App;