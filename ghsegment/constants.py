import json

WATCH_URL_JSON_PATH = 'biliup_urls.json'
BILIUP_INFO_PATH = 'biliup_info.json'

def get_data(data_path = WATCH_URL_JSON_PATH, default_data = []):
    try: 
        with open(data_path) as f:
            return json.load(f)
    except:
        return default_data

def get_watched_URL():
    return get_data()

def get_biliup_data():
    return get_data(BILIUP_INFO_PATH, {})

def write_watched_URL(urls):
    with open(WATCH_URL_JSON_PATH, 'w') as f:
        json.dump(urls, f, indent=4)

def write_biliup_data(data):
    with open(BILIUP_INFO_PATH, 'w') as f:
        json.dump(data, f, indent=4)