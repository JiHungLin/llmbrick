#!/bin/bash

curl --location '127.0.0.1:8000/chat/completions' \
--header 'Accept: text/event-stream' \
--header 'Content-Type: application/json' \
--data '{
    "model": "gpt-4o",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the weather like today?"}
    ],
    "stream": true,
    "sessionId": "1234567890",
    "temperature": 0.7,
    "maxTokens": 100
}'