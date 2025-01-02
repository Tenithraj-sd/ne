import numpy as np
import json
import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.utils import to_categorical
import random

# Load the model and preprocessing tools
model = tf.keras.models.load_model("chatbot_model.h5")
with open("encoder_classes.json") as f:
    classes = json.load(f)
with open("vectorizer.json") as f:
    vocab = json.load(f)
vectorizer = CountVectorizer(vocabulary=vocab)

# Example of predefined intents (you can modify or load your actual intents here)
intents = [
    {
        "tag": "greeting",
        "patterns": [
            "Hi",
            "Hello",
            "Hey",
            "How are you",
            "What's up"
        ],
        "responses": [
            "Hi there",
            "Hello",
            "Hey",
            "I'm fine, thank you",
            "Nothing much"
        ]
    },
    {
        "tag": "goodbye",
        "patterns": [
            "Bye",
            "Goodbye",
            "See you",
            "Take care"
        ],
        "responses": [
            "Goodbye!",
            "See you later!",
            "Take care!"
        ]
    },
    # Add more intents as needed
]

# Extract patterns and tags for training and testing
patterns = []
tags = []

for intent in intents:
    for pattern in intent['patterns']:
        patterns.append(pattern)
        tags.append(intent['tag'])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(patterns, tags, test_size=0.2, random_state=42)

# Transform text data into numeric vectors using the pre-trained vectorizer
X_train_vec = vectorizer.transform(X_train).toarray()
X_test_vec = vectorizer.transform(X_test).toarray()

# Convert the tags (labels) into numeric values using the class index
y_train_num = [classes.index(tag) for tag in y_train]
y_test_num = [classes.index(tag) for tag in y_test]

# One-hot encode the labels (targets)
y_train_one_hot = to_categorical(y_train_num, num_classes=len(classes))
y_test_one_hot = to_categorical(y_test_num, num_classes=len(classes))

# Compile the model with categorical crossentropy loss and accuracy metric
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model on the training data
model.fit(X_train_vec, np.array(y_train_one_hot), epochs=5, batch_size=8, verbose=1)

# Evaluate the model on the test data
y_pred = model.predict(X_test_vec)
y_pred_labels = np.argmax(y_pred, axis=1)  # Get the index of the highest probability (predicted class)

# Calculate accuracy
accuracy = accuracy_score(y_test_num, y_pred_labels)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Display classification report (includes precision, recall, and F1-score)
print("\nClassification Report:")
print(classification_report(y_test_num, y_pred_labels, target_names=classes))

# Display confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test_num, y_pred_labels))
