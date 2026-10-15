import os
import yaml

def load_yaml(filename: str) -> dict:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'configs', filename)
    if not os.path.exists(config_path):
        config_path = os.path.join(base_dir, 'config', filename)
        
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"File konfigurasi tidak ditemukan: {config_path}")
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            return data
    except yaml.YAMLError as e:
        raise ValueError(f"Format YAML tidak valid pada file {filename}: {e}")
