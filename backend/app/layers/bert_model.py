import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from app.utils.logger import get_logger
from app.layers.label_map import ATTACK_LABELS
from pathlib import Path

logger = get_logger('bert')

class BERTLayer:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parents[2]
        model_root = BASE_DIR / "trained_models"

        # -------------------------------------------------
        # 🔥 FIND LATEST BERT MODEL FOLDER AUTOMATICALLY
        # -------------------------------------------------
        bert_folders = sorted(model_root.glob("bert_classifier*"))

        if not bert_folders:
            raise FileNotFoundError("No BERT model found in trained_models/")

        model_path = bert_folders[-1]  # latest folder

        logger.info(f"🧠 Loading LATEST BERT model: {model_path}")

        # -------------------------------------------------
        # LOAD MODEL
        # -------------------------------------------------
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)

        self.model.eval()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

        logger.info(f'BERT model loaded on {self.device}')

    def run(self, preprocessing_output: dict, batch_size: int = 32) -> dict:
        try:
            texts = preprocessing_output['nlp_texts']
            logger.info(f'BERT classifying {len(texts)} texts')
            all_results = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                encoding = self.tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=128, return_tensors='pt'
                )
                encoding = {k: v.to(self.device) for k, v in encoding.items()}

                with torch.no_grad():
                    logits = self.model(**encoding).logits

                probs = torch.softmax(logits, dim=-1).cpu().numpy()
                preds = np.argmax(probs, axis=1)

                for j, (pred, prob) in enumerate(zip(preds, probs)):
                    label = int(pred)
                    all_results.append({
                        'index': i + j,
                        'label': label,
                        'attack_type': ATTACK_LABELS.get(label, f'Class {label}'),
                        'confidence': round(float(np.max(prob)), 4),
                        'logits': logits[j].cpu().numpy().tolist()
                    })

            attack_count = sum(1 for r in all_results if r['label'] != 0)
            logger.info(f'BERT: {attack_count} attacks detected')

            return {
                'status': 'OK',
                'layer': 'bert',
                'predictions': all_results,
                'attack_count': attack_count
            }
        except Exception as e:
            logger.error(f'BERT failed: {e}')
            return {'status': 'ERROR', 'layer': 'bert', 'error': str(e)}
