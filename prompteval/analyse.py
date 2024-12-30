import subprocess
import pathlib
from typing import List, Tuple
import json
def spectral_analyse(filename: str, ruleset_url: str, output_dir: str, file_out: str) -> str:
    print("src file name: ", filename)
    print("out file name: ", file_out)
    try:
        subprocess.run(["spectral", "lint", filename, "--ruleset", ruleset_url, "--format", "json", "-o", file_out], shell=True, check=True, capture_output=True, text=True, cwd=output_dir)
    except subprocess.CalledProcessError as e:
        print("CalledProcessError Error ==== :", e)

def get_content_from_file(api_folder: str, file: str) -> str:
    try:    
        with open(pathlib.Path(api_folder, file), "r", encoding="utf-8") as file:
            text = file.read()
            return text
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return

def text_to_json_objects(api_folder: str, file: str) -> List[dict]:
    text = get_content_from_file(api_folder, file)
    json_objects = []
    if not text:
        print("No content in the file")
        return []
    try:
        json_objects = json.loads(text)
        if isinstance(json_objects, dict):
            json_objects = [json_objects]
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return json_objects

def any_spec_res(jsons: List[dict]) -> Tuple[List[dict], dict]:
    results = []
    calc = {'warn': 0, 'error': 0, 'info': 0}
    for item in jsons:
        result = {}
        if 'severity' in item and 'code' in item and 'message' in item:
            result['severity'] = item['severity']
            result['code'] = item['code']
            result['message'] = item['message']
        if result:
            if result['severity'] == 0:
                calc['error'] += 1
            elif result['severity'] == 1:
                calc['warn'] += 1
            elif result['severity'] == 2:
                calc['info'] += 1
            if result not in results:
                results.append(result)
    return results, calc