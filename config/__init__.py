import toml

config:dict = toml.load('./config/config.toml')

API_KEY:str=""
with open('./config/API_KEY',"r") as f:
    API_KEY=f.read()
