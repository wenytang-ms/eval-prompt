import pathlib
from typing import List
import json
class AnswerLengthEvaluator:
    def __init__(self):
        pass

    def get_content_from_file(api_folder: str, file: str) -> str:
        try:    
            with open(pathlib.Path(api_folder, file), "r", encoding="utf-8") as file:
                text = file.read()
                return text
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return

    def text_to_json_objects(self, api_folder: str, file: str) -> List[dict]:
        text = self.get_content_from_file(api_folder, file)
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

    def any_spec_res(jsons: List[dict]) -> List[str]:
        results = []
        for item in jsons:
            result = {}
            if 'severity' in item:
                result['severity'] = item['severity']
            if 'code' in item and 'message' in item:
                result['code'] = item['code']
                result['message'] = item['message']
            if result:
                results.append(result)
        return results

    def __call__(self, *, out_dir: str, out_file: str):
        res = self.any_spec_res(self.text_to_json_objects(out_dir, out_file))
        return {"error": res.count("error"), "warn": res.count("warn")}