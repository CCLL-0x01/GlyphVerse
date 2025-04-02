from .LLM_api_ import GPT
from config import config
import json

def knowledge_acquisition(char):
    with open(config['model']['LLM']['cache_path']) as f:
        cache=json.load(f)
        char_cache=cache.get(char,None)
    if char_cache:
        return char_cache
    else:
        for _ in range(3):
            try:
                response = GPT(config["model"]["prompts"]["llm_prompt"] % char)
                response_json = json.loads(response.replace('```json', '').replace('```', ''))
                assert response_json['sub_prompt']
                assert response_json['surr_prompt']
                assert response_json['surr_prompt'][0]
                cache.update({
                    char:{
                        'sub_prompt':response_json['sub_prompt'],
                        'surr_prompt':response_json['surr_prompt']
                    }
                })
                with open(config['model']['LLM']['cache_path'],'w') as f:
                    f.write(json.dumps(cache,indent=4,ensure_ascii=False))
                return response_json
            except Exception as e:
                print(f'{str(e)}, try again')
        raise Exception('error loading prompts')

