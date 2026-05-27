import os
import json
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from transformers import BertTokenizer, BertForSequenceClassification

# Define features
FEATURES = [
    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Flow Bytes/s', 'Flow Packets/s', 'Fwd Packet Length Mean',
    'Bwd Packet Length Mean', 'Flow IAT Mean', 'Fwd IAT Mean',
    'Bwd IAT Mean', 'Fwd PSH Flags', 'Bwd PSH Flags',
    'Fwd URG Flags', 'Bwd URG Flags', 'Destination Port',
    'Average Packet Size'
]

def main():
    os.makedirs('trained_models', exist_ok=True)
    
    print("Generating mock dataset...")
    np.random.seed(42)
    n_samples = 200
    n_features = len(FEATURES)
    
    # 1. Scaler
    print("Fitting and saving Scaler...")
    X_raw = np.random.rand(n_samples, n_features) * 100
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    joblib.dump(scaler, 'trained_models/scaler.pkl')
    
    # Feature names
    with open('trained_models/feature_names.json', 'w') as f:
        json.dump(FEATURES, f)
        
    # 2. XGBoost
    print("Training and saving XGBoost...")
    # Labels 0: Benign, 1: Brute Force, 2: DDoS/DoS, 3: Port Scan, 4: Botnet
    y = np.random.randint(0, 5, size=n_samples)
    xgb = XGBClassifier(
        n_estimators=10,
        max_depth=3,
        learning_rate=0.1,
        eval_metric='mlogloss',
        random_state=42
    )
    xgb.fit(X_scaled, y)
    joblib.dump(xgb, 'trained_models/xgboost_model.pkl')
    
    # 3. Autoencoder
    print("Training and saving Autoencoder...")
    inp = Input(shape=(n_features,))
    x = Dense(8, activation='relu')(inp)
    x = Dense(4, activation='relu')(x)  # bottleneck
    x = Dense(8, activation='relu')(x)
    out = Dense(n_features, activation='linear')(x)
    autoencoder = Model(inp, out)
    autoencoder.compile(optimizer='adam', loss='mse')
    
    # Train ONLY on "benign" data (label 0)
    X_benign = X_scaled[y == 0]
    if len(X_benign) == 0:
        X_benign = X_scaled[:20]
    autoencoder.fit(X_benign, X_benign, epochs=5, batch_size=4, verbose=0)
    autoencoder.save('trained_models/autoencoder.keras')
    
    # Calculate threshold (95th percentile of reconstruction error)
    reconstructed = autoencoder.predict(X_benign, verbose=0)
    errors = np.mean((X_benign - reconstructed) ** 2, axis=1)
    threshold = float(np.percentile(errors, 95))
    np.save('trained_models/ae_threshold.npy', np.array([threshold]))
    print(f"Autoencoder threshold saved: {threshold:.6f}")
    
    # 4. BERT (tiny)
    print("Initializing and saving tiny BERT classifier...")
    # Using prajjwal1/bert-tiny which has only 2 layers, 128 hidden size
    # Download and save it to the local directory
    model_name = "prajjwal1/bert-tiny"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=5)
    
    # Save locally to match expected path
    model.save_pretrained('trained_models/bert_classifier')
    tokenizer.save_pretrained('trained_models/bert_classifier')
    
    print("All models initialized successfully!")

if __name__ == '__main__':
    main()
