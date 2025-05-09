import React from "react";

const options = [
  { label: "친근한 친구", prompt: "넌 내 친한 친구야. 반말로 친근하게 이야기해." },
  { label: "지적인 조수", prompt: "넌 매우 똑똑하고 조용한 조수야. 존댓말로 공손하게 설명해줘." },
  { label: "장난꾸러기", prompt: "넌 장난기 많은 캐릭터야. 농담을 자주 하고 자유롭게 말해." },
];

function PersonaSelect({ onSelect }) {
  return (
    <div className="persona-select">
      <h2>원하는 성격을 선택해주세요</h2>
      {options.map((opt) => (
        <button key={opt.label} onClick={() => onSelect(opt.prompt)}>
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default PersonaSelect;
