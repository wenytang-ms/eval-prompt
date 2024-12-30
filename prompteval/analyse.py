import subprocess
import pathlib
from typing import List, Tuple
import json
import os
import pprint
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

class specRes:
    def __init__(self, severity, code, message):
        self.severity = severity
        self.code = code
        self.message = message

    def __eq__(self, other):
        if isinstance(other, specRes):
            return self.severity == other.severity and self.code == other.code and self.message == other.message
        return False

    def __hash__(self):
        return hash(self.severity) ^ hash(self.code) ^ hash(self.message)
    
    def __str__(self):
        return f"Severity: {self.severity}, Code: {self.code}, Message: {self.message}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_json(self):
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message
        }

def any_spec_res(jsons: List[dict]) -> Tuple[set[dict], dict]:
    unique_results = set()
    for item in jsons:
        if 'severity' in item and 'code' in item and 'message' in item:
            item = specRes(item['severity'], item['code'], item['message'])
            if item not in unique_results:
                unique_results.add(item)
    return unique_results

if __name__ == "__main__":
    ruleset_url = "https://raw.githubusercontent.com/Azure/APICenter-Analyzer/preview/resources/rulesets/oas.yaml"
    res_folder_path = pathlib.Path('../results')
    unique_results = set()
    calcs = []
    for res_file in res_folder_path.glob("*"):
        if res_file.suffix == ".yml":
            out_file = os.path.basename(res_file.stem + "_output.json")
            spectral_analyse(os.path.basename(res_file), ruleset_url, res_folder_path, os.path.basename(out_file))
            res = any_spec_res(text_to_json_objects(res_folder_path, out_file))
            for item in res:
                unique_results.add(item)
    output_jsonl_file  = res_folder_path / "output.jsonl"
    with open(output_jsonl_file, 'w', encoding="utf-8") as json_file:
        for item in unique_results:
            # 将每个对象转换回JSON字符串，并写入文件，每个对象占一行
            json.dump(item.to_json(), json_file)
            json_file.write('\n')