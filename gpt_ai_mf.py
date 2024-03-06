#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-03-05 Fil - Future code Yandex.Practicum
Multi-functional AI-bot
README.md for more

GPT-functions
"""

import requests
from transformers import AutoTokenizer

model = "mistralai/Mistral-7B-Instruct-v0.2"


# Токенайзер
def count_tokens(text):
    tokenizer = AutoTokenizer.from_pretrained(model)
    return len(tokenizer.encode(text))


# Получение ответа от языковой модели
def get_resp(
        system_content,
        assistant_content,
        user_data_uid: dict):
    return requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},

        json={
            "messages": [
                {"role": "system",
                 "content": system_content},
                {"role": "user",
                 "content": user_data_uid['task']},
                {"role": "assistant",
                 "content": assistant_content +
                            user_data_uid['answer']},
            ],
            "temperature": 0.9,
            "max_tokens": 100
        }
    )
