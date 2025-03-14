from .LLM_api_ import GPT
from config import config
import json

def knowledge_acquisition(char):
    response = GPT(config["model"]["prompts"]["llm_prompt"] % char)
    response = response.replace('```json', '').replace('```', '')
    return json.loads(response)
