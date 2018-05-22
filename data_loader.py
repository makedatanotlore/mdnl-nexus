import json
import os

base_folder = os.path.dirname(__file__)


def init_char_data():
    with open(os.path.join(base_folder, 'sources', 'char_data.json'), encoding='utf-8') as f:
        data = json.load(f)
        return data


def init_name_data():
    with open(os.path.join(base_folder, 'sources', 'name_data.json'), encoding='utf-8') as f:
        data = json.load(f)
        return data
