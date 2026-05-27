import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import pickle
import os

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../dataset/burnout.csv'))

X = df[['MBI1', 'MBI2', 'MBI3', 'MBI4', 'MBI5']]
y = df['Burnout']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
auc = roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovr', average='weighted')

print(f"Accuracy  : {accuracy:.2f}")
print(f"Precision : {precision:.2f}")
print(f"Recall    : {recall:.2f}")
print(f"AUC       : {auc:.2f}")

model_dir = os.path.dirname(__file__)
with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
    pickle.dump(model, f)
with open(os.path.join(model_dir, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(le, f)

import json
metrics = {
    'accuracy': round(accuracy * 100, 1),
    'precision': round(precision * 100, 1),
    'recall': round(recall * 100, 1),
    'auc': round(auc, 3)
}
with open(os.path.join(model_dir, 'metrics.json'), 'w') as f:
    json.dump(metrics, f)

print("Model saved: model/model.pkl")
print("Metrics saved: model/metrics.json")
