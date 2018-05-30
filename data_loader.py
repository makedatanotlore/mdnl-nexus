import json
import os

base_folder = os.path.dirname(__file__)


def init_data(filename):
    with open(os.path.join(base_folder, 'sources', filename), encoding='utf-8') as f:
        data = json.load(f)
        return data
