import toml
from typing import Dict, Any

class Config(dict):  # 继承自字典类型
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reload()  # 初始化时自动加载

    def reload(self) -> None:
        self.clear()
        self.update(toml.load('./config/config.toml'))

        with open('./config/API_KEY', 'r') as f:
            self['API_KEY'] = f.read().strip()
        
        print('config reloaded: ',self)

config: Config = Config() 