import streamlit as st
import json
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
import random

# Load model and preprocessing tools
model = tf.keras.models.load_model("chatbot_model.h5")
with open("encoder_classes.json") as f:
    classes = json.load(f)
with open("vectorizer.json") as f:
    vocab = json.load(f)
vectorizer = CountVectorizer(vocabulary=vocab)

# Predefined intents (keep this if you have them hardcoded or load from file if needed)
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


def get_response(user_input):
    input_data = vectorizer.transform([user_input]).toarray()
    prediction = model.predict(input_data)
    tag = classes[np.argmax(prediction)]
    for intent in intents:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return "Sorry, I didn't understand that."

# Streamlit interface
st.title("Chatbot")
st.write("Hello! Ask me anything.")

if 'responses' not in st.session_state:
    st.session_state.responses = []

def process_input():
    user_input = st.session_state.user_input
    response = get_response(user_input)
    st.session_state.responses.append((user_input, response))
    st.session_state.user_input = ""  # Clear the input field

# Input field and handling with Enter key
st.text_input("You: ", key="user_input", on_change=process_input)

# Display chat history with the latest message at the top
for user_msg, bot_msg in reversed(st.session_state.responses):
    st.write(f"You: {user_msg}")
    st.write(f"Bot: {bot_msg}")
