import json


def get_variables(file_name: str) -> dict:
    with open(file_name, 'r', encoding='utf-8') as outfile:
        return json.load(outfile)
    
