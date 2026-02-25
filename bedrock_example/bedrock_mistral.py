"""Mistral 3 on AWS Bedrock via OpenAI SDK using bearer token auth."""

import os
from openai import OpenAI

token = os.environ["AWS_BEARER_TOKEN_BEDROCK"]

client = OpenAI(
    api_key=token,
    base_url="https://bedrock-runtime.us-west-2.amazonaws.com/openai/v1",
    default_headers={"Authorization": f"Bearer {token}"},
)

response = client.chat.completions.create(
    model="mistral.mistral-large-3-675b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain LLMs."},
    ],
    max_tokens=256,
    temperature=0.7,
)

print("Model:", response.model)
print("Response:", response.choices[0].message.content)
print("Tokens used:", response.usage.total_tokens)
