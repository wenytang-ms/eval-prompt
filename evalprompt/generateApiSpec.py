# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=ANN201,ANN001,RET505
import os
import pathlib
import random
import time
from functools import partial
import jinja2
import requests
import re
from concurrent.futures import ThreadPoolExecutor
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from typing import List, Tuple, TypedDict
import json
from dotenv import load_dotenv
load_dotenv("../.env")
# Create a session for making HTTP requests
session = requests.Session()

# Set up Jinja2 for templating
templateLoader = jinja2.FileSystemLoader(pathlib.Path(__file__).parent.resolve())
templateEnv = jinja2.Environment(loader=templateLoader)
user_message_template2 = templateEnv.get_template("user-message2.jinja2")

def get_api_spec(query: str) -> str:
    # Get the API spec from the OpenAI API
    api_spec = AzureOpenAI.get_api_spec(query)
    return api_spec

def augemented_qa(context: str, languageId: str) -> str:
    user_message = user_message_template2.render(contexts=context, languageId=languageId)
    messages = [{"role": "user", "content": user_message}]
    with AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    ) as client:
        response = client.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"), messages=messages, temperature=0.7, max_tokens=800
        )
        return response.choices[0].message.content

class Response(TypedDict):
    response: str
    context: str

def generateApiSpec(context: str, languageId: str) -> Response:
    response = augemented_qa(context, languageId)
    return {"response": response }

def get_language_from_extension(extension: str) -> str:
    extension_to_language = {
        "cs": "csharp",
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "c": "c",
        "cpp": "c++"
    }
    return extension_to_language.get(extension, "unknown")

def generateOutputData(srcDir: str, specDir: str, outDir: str) -> dict:
    api_folder = pathlib.Path(srcDir)
    apispec_dir = pathlib.Path(specDir)
    output_dir = pathlib.Path(outDir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = pathlib.Path(output_dir, "output.jsonl")
    output_file.touch(exist_ok=True)
    for api_file in api_folder.glob("*"):
        with open(api_file, "r", encoding="utf-8") as file:
            file_content = file.read()
        file_extension = api_file.suffix[1:]  # Get the file extension without the dot
        language = get_language_from_extension(file_extension)
        response = generateApiSpec(file_content, language)
        file_name = api_file.stem
        if file_name:
            yml_file = apispec_dir / f"{file_name}.yml"
            if yml_file.exists():
                with open(yml_file, "r", encoding="utf-8") as yml:
                    ground_truth_content = yml.read()
        output = {
            "response": response["response"],
            "context": file_content,
            "ground_truth": ground_truth_content
        }
        
        with open(output_file, "a", encoding="utf-8") as jsonl_file:
            jsonl_file.write(json.dumps(output) + "\n")

# Main function
if __name__ == "__main__":
    api_folder = pathlib.Path(__file__).parent.resolve() / "../apisrc"
    output_dir = pathlib.Path(__file__).parent.resolve() / "../output"
    output_dir.mkdir(exist_ok=True)
    apispec_dir = pathlib.Path(__file__).parent.resolve() / "../apispec"
    generateOutputData(api_folder, apispec_dir, output_dir)