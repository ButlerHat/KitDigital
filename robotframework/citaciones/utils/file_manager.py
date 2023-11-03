import json


def store_data(dictionary: dict, file_name: str):
    with open(file_name, 'w', encoding='utf-8') as outfile:
        json.dump(dictionary, outfile)


def restore_data(file_name: str) -> dict:
    with open(file_name, 'r', encoding='utf-8') as outfile:
        return json.load(outfile)