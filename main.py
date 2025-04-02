from server import create_server
from config import config
import os

def prepare_environment():
    dirs=['./temp','./model/model_weights','./model/loras']
    for directory in dirs:
        if not os.path.exists(directory):
            os.mkdir(directory)
    
    if not os.path.exists('./config/API_KEY'):
        raise EnvironmentError('./config/API_KEY not found, please put your LLM api key there.')
    if not os.path.exists('./temp/LLM_cache.json'):
        with open('./temp/LLM_cache.json','w') as f:
            f.write('{}')
    if not os.path.exists('./web/dist'):
        print('Web UI not built, building now ...')
        os.system('cd ./web && npm run build')

if __name__ == '__main__':
    prepare_environment()

    app = create_server()
    app.run(**config["server"])