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
system_message_template = templateEnv.get_template("system-message.jinja2")

def get_api_spec(query: str) -> str:
    # Get the API spec from the OpenAI API
    api_spec = AzureOpenAI.get_api_spec(query)
    return api_spec

def augemented_qa(query: str, context: str) -> str:
    system_message = system_message_template.render(contexts=context)
    messages = [{"role": "system", "content": system_message}, {"role": "user", "content": query}]
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

def generateApiSpec(query: str, context: str) -> Response:
    response = augemented_qa(query, context)
    return {"response": response }

def generateOutputData(query: str, srcDir: str, specDir: str, outDir: str) -> dict:
    api_folder = pathlib.Path(srcDir)
    output_dir = pathlib.Path(outDir)
    apispec_dir = pathlib.Path(specDir)
    for api_file in api_folder.glob("*"):
        with open(api_file, "r", encoding="utf-8") as file:
            file_content = file.read()
        response = generateApiSpec(query, file_content)
        file_name = api_file.stem
        if file_name:
            yml_file = apispec_dir / f"{file_name}.yml"
            if yml_file.exists():
                with open(yml_file, "r", encoding="utf-8") as yml:
                    ground_truth_content = yml.read()
        output = {
            "response": response["response"],
            "query": query,
            "context": file_content,
            "ground_truth": ground_truth_content
        }
        
        with open(output_dir / "output.jsonl", "a", encoding="utf-8") as jsonl_file:
            jsonl_file.write(json.dumps(output) + "\n")

# Main function
if __name__ == "__main__":
    api_folder = pathlib.Path(__file__).parent.resolve() / "../apisrc"
    query='Please be professional, and use below infomation to generate an OpenAPI specification documentation with YAML format:'
    output_dir = pathlib.Path(__file__).parent.resolve() / "../output"
    output_dir.mkdir(exist_ok=True)
    apispec_dir = pathlib.Path(__file__).parent.resolve() / "../apispec"
    generateOutputData(query, api_folder, apispec_dir, output_dir)