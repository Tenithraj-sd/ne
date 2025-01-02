import json
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
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
    }]
# Sample intents data

# Preprocess data
patterns = []
tags = []
tag_classes = []

for intent in intents:
    for pattern in intent['patterns']:
        patterns.append(pattern)
        tags.append(intent['tag'])
    if intent['tag'] not in tag_classes:
        tag_classes.append(intent['tag'])

encoder = LabelEncoder()
encoded_tags = encoder.fit_transform(tags)

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(patterns).toarray()

# Convert labels to categorical
y = tf.keras.utils.to_categorical(encoded_tags, len(tag_classes))

# Build model
model = Sequential()
model.add(Dense(128, input_shape=(X.shape[1],), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(len(tag_classes), activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train model
model.fit(X, y, epochs=200, batch_size=8, verbose=1)

# Save model and data
model.save("chatbot_model.h5")
with open("encoder_classes.json", "w") as f:
    json.dump(encoder.classes_.tolist(), f)
with open("vectorizer.json", "w") as f:
    json.dump(vectorizer.get_feature_names_out().tolist(), f)

# Load model for testing
def chat():
    model = tf.keras.models.load_model("chatbot_model.h5")
    with open("encoder_classes.json") as f:
        classes = json.load(f)
    with open("vectorizer.json") as f:
        vocab = json.load(f)
    vectorizer = CountVectorizer(vocabulary=vocab)

    print("Start chatting (type 'quit' to stop):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        input_data = vectorizer.transform([user_input]).toarray()
        prediction = model.predict(input_data)
        tag = classes[np.argmax(prediction)]
        for intent in intents:
            if intent['tag'] == tag:
                print(random.choice(intent['responses']))

chat()
