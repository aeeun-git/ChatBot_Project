
import pandas as pd
import matplotlib.pyplot as plt
from datasets import Dataset, DatasetDict
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
    pipeline
)
from sklearn.model_selection import train_test_split
from transformers.trainer_callback import TrainerCallback
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import torch
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams['font.family'] = 'Malgun Gothic'


# ▶ CSV 불러오기
data_path = "intent_dataset_varied_1000.csv"
df = pd.read_csv(data_path)

# ▶ 라벨 매핑
label_list = sorted(df["label"].unique().tolist())
label_map = {label: i for i, label in enumerate(label_list)}
inv_label_map = {i: label for label, i in label_map.items()}
df["labels"] = df["label"].map(label_map)

# ▶ 훈련/검증 나누기
train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["labels"], random_state=42)
ds = DatasetDict({
    "train": Dataset.from_pandas(train_df[["sentence", "labels"]]),
    "validation": Dataset.from_pandas(val_df[["sentence", "labels"]])
})

# ▶ 토크나이저 및 모델
tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
model = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=len(label_list)
)

# ▶ 전처리
def preprocess(example):
    return tokenizer(example["sentence"], truncation=True, padding="max_length", max_length=64)

ds = ds.map(preprocess, batched=True)

# ▶ 손실 기록용 콜백
train_losses = []
eval_losses = []

class LossCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if "loss" in logs:
            train_losses.append(logs["loss"])
        if "eval_loss" in logs:
            eval_losses.append(logs["eval_loss"])

# ▶ 하이퍼파라미터 수정 + GPU 자동 사용
training_args = TrainingArguments(
    output_dir="./trained_intent_model",
    per_device_train_batch_size=8,
    num_train_epochs=10,
    learning_rate=2e-5,
    logging_steps=10,
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss"
)

# ▶ Trainer 설정
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=ds["train"],
    eval_dataset=ds["validation"],
    callbacks=[LossCallback()],
)

# ▶ 학습 시작
trainer.train()

# ▶ 모델 저장
model.save_pretrained("./trained_intent_model")
tokenizer.save_pretrained("./trained_intent_model")

# ▶ 손실 시각화
plt.plot(train_losses, label="Train Loss")
plt.plot(eval_losses, label="Validation Loss")
plt.xlabel("Logging Steps")
plt.ylabel("Loss")
plt.legend()
plt.title("Training & Validation Loss")
plt.grid()
plt.tight_layout()
plt.savefig("training_loss_plot_updated.png")

# ▶ 분류기 생성 및 전체 예측
clf = pipeline("text-classification", model="./trained_intent_model", tokenizer="./trained_intent_model", top_k=1, device=0 if torch.cuda.is_available() else -1)

# ▶ 전체 검증셋에 대해 예측
val_texts = val_df["sentence"].tolist()
true_labels = val_df["labels"].tolist()
pred_labels = []

for text in val_texts:
    pred = clf(text)
    label_num = int(pred[0][0]["label"].split("_")[-1])
    pred_labels.append(label_num)

# ▶ 분류 리포트 출력
print("\n📊 Classification Report:")
print(classification_report(true_labels, pred_labels, target_names=label_list))

# ▶ 혼동 행렬 시각화
cm = confusion_matrix(true_labels, pred_labels)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=label_list, yticklabels=label_list)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig("confusion_matrix_updated.png")
