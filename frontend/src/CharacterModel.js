// src/CharacterModel.js
import React, { useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF, useAnimations } from "@react-three/drei";

// 3D 애니메이션을 보여줄 컴포넌트
function AnimatedModel({ intent }) {
  const group = useRef();
  const { scene, animations } = useGLTF("/hello_motion.glb"); // 모델 경로 (public 폴더 기준)
  const { actions, mixer } = useAnimations(animations, group);

  // intent가 바뀔 때 해당 액션 실행
  useEffect(() => {
    if (!actions) return;
    if (intent === "LABEL_2" && actions["Wave"]) {  // "LABEL_2"는 인사
      actions["Wave"].reset().fadeIn(0.3).play();
    } else if (intent === "LABEL_3" && actions["Goodbye"]) {  // "LABEL_3"은 작별
      actions["Goodbye"].reset().fadeIn(0.3).play();
    }
  }, [intent, actions]);

  useFrame((_, delta) => mixer?.update(delta));

  return <primitive ref={group} object={scene} scale={1.5} />;
}

export default function CharacterModel({ intent }) {
  return (
    <Canvas camera={{ position: [0, 1.5, 4], fov: 45 }}>
      <ambientLight />
      <directionalLight position={[1, 1, 1]} />
      <OrbitControls />
      <AnimatedModel intent={intent} />
    </Canvas>
  );
}
