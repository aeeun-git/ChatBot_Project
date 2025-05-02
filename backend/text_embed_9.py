from transformers import pipeline
import torch

class TEXT_Embed:
    def __init__(self):
        try:
            self.clf = pipeline(
                "text-classification",
                model="./trained_intent_model",
                tokenizer="./trained_intent_model",
                top_k=1,
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ 의도 분류기 로드 완료!")
        except Exception as e:
            print(f"❌ 분류기 로드 실패: {e}")
            self.clf = None

        self.label_map = {
            "LABEL_0": "감사",
            "LABEL_1": "슬픔",
            "LABEL_2": "인사",
            "LABEL_3": "작별",
            "LABEL_4": "칭찬"
        }

    def classify_intent(self, text):
        if self.clf is None:
            return None
        prediction = self.clf(text)[0][0]["label"]
        return self.label_map.get(prediction, "알 수 없음")
