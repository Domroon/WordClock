import json


def get_config():
    f = open('config.json', 'r')
    return json.loads(f.read())


def change_config(key, value):
    config = get_config()
    config[key] = value
    f = open('config.json', 'r')
    f.write(json.dumps(config))
    f.close()


config = get_config()