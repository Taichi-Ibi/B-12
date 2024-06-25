from pathlib import Path

import yaml
from dotmap import DotMap

class ConfigLoader:
    _instance = None
    _yaml_file = Path('src/.env/config.yaml')  # クラス変数としてYAMLファイルパスを保持

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        if not self._yaml_file.exists():
            raise FileNotFoundError(f"The file {self._yaml_file} does not exist.")
        with self._yaml_file.open('r') as file:
            yaml_data = yaml.safe_load(file)
        self.config = DotMap(yaml_data)

    def get_config(self):
        return self.config
    
if __name__=="__main__":
    config_loader = ConfigLoader()
    config = config_loader.get_config()
    from pprint import pprint
    pprint(config)