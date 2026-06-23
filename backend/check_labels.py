import re
from app.layers.label_map import ATTACK_LABELS

be_label = ATTACK_LABELS[12]
print("Backend  label:", repr(be_label))

with open('../frontend/src/utils/attackLabels.js', encoding='utf-8') as f:
    content = f.read()

m = re.search(r"12: '([^']+)'", content)
fe_label = m.group(1) if m else 'NOT FOUND'
print("Frontend label:", repr(fe_label))
print("Match:", be_label == fe_label)
