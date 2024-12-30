import jinja2
import pathlib
import os
import json
from openai import AzureOpenAI
from typing import TypedDict
from azure.identity import get_bearer_token_provider, AzureCliCredential
import re
import pystache
import shutil

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

class Response(TypedDict):
    response: str
    context: str

def generateApiSpec(context: str, languageId: str) -> Response:
    response = get_res_from_openai(context, languageId)
    return {"response": response }

templateLoader = jinja2.FileSystemLoader(pathlib.Path(__file__).parent.resolve())
templateEnv = jinja2.Environment(loader=templateLoader)
user_message_template2 = templateEnv.get_template("user-message.jinja2")

def get_prompt(context: json):
    path = pathlib.Path(__file__).parent.resolve()
    with open(path / '../prompts/genSpecFromApiCode.mustache', 'r') as f:
        template = f.read()
        rendered = pystache.render(template, context)
        return rendered

def get_openai_client():
    if os.environ['RBAC'] == "TRUE":
        token_provider = get_bearer_token_provider(
                AzureCliCredential(), "https://cognitiveservices.azure.com/.default"
            )
        return AzureOpenAI(
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider
        )
    else:
        return AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )

def get_res_from_openai(context: str, languageId: str) -> str:
    context = {
        "contexts": context,
        "languageId": languageId
    }
    user_message = get_prompt(context)
    messages = [{"role": "user", "content": user_message}]
    client=get_openai_client()
    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"), messages=messages, temperature=0.7, max_tokens=800
    )
    return response.choices[0].message.content

def remove_code_block_format(text):
    # 移除代码块的开始和结束标记
    text = re.sub(r'^```yaml.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text

def clean_folder(folder_path):
    # 检查文件夹是否存在
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # 遍历文件夹中的所有内容
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # 如果是文件，则删除
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # 如果是目录，则递归删除
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"The folder {folder_path} does not exist.")
