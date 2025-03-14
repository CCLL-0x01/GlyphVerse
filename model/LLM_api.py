from config import API_KEY, config
from openai import OpenAI

client = OpenAI(api_key=API_KEY, base_url=config["model"]["LLM"]["LLM_base_url"])

def GPT(input:str)->str:
    response = client.chat.completions.create(
        model=config["model"]["LLM"]["model_name"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": input},
        ],
        stream=False
    )

    return response.choices[0].message.content