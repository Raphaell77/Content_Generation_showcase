from analysis.search_videos import PATH_YOUTUBE_DATA
import json
import regex as re


def write_in_json(data: dict[str, list[str]], path: str):
    try:
        if not isinstance(data, dict):
            decoded = data.encode().decode("unicode_escape")
            data = json.loads(decoded)

        json_str = json.dumps(data, indent=4, ensure_ascii=False)

        json_str = re.sub( # regex von gemini
                    r'\[\n\s*([\d,\.\s]+)\n\s*\]',
                    lambda match: '[' + re.sub(r'\s+', ' ', match.group(1)).strip() + ']', 
                    json_str
                )

        with open(path, 'w', encoding="UTF-8") as file:
            file.write(json_str)
            print(f"Successfully inserted data into {path}")
            return
            
    except FileNotFoundError:
        print(f"Error: file {path} was not found.")


def read_json(path):
    try:
        with open(path, 'r', encoding='utf8') as file:
            data = json.load(file)
            print("Successfully read data")
            return data
            
    except FileNotFoundError:
        print(f'Error: file {path} was not found.')



def delete_json_data(path):
    try:
        with open(path, 'w') as file:
            pass
        print(f"Successfully deleted data of {path}")
                
    except FileNotFoundError:
        print(f'Error: file {path} was not found.')

    return


