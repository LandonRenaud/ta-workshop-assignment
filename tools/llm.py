import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "INSERT_YOUR_API_KEY_HERE"),
)

def call_llm_json(prompt: str, system_prompt: str = "You output valid JSON.") -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    kwargs = {
        "model": os.getenv("LLM_MODEL", "gpt-5.6-luna"),
        "messages": messages,
    }

    kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    response_text = response.choices[0].message.content

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": response_text}