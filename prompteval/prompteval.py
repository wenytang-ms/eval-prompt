import jinja2
import pathlib
import os
from openai import AzureOpenAI
from typing import TypedDict
from azure.identity import get_bearer_token_provider, AzureCliCredential
import re
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
    response = augemented_qa(context, languageId)
    return {"response": response }

templateLoader = jinja2.FileSystemLoader(pathlib.Path(__file__).parent.resolve())
templateEnv = jinja2.Environment(loader=templateLoader)
user_message_template2 = templateEnv.get_template("user-message.jinja2")

def get_openai_client():
    if('FALSE' == os.environ['RBAC']):
        return AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            rbac_token=os.environ["AZURE_OPENAI_RBAC_TOKEN"]
        )
    else:
        token_provider = get_bearer_token_provider(
                AzureCliCredential(), "https://cognitiveservices.azure.com/.default"
            )
        return AzureOpenAI(
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider
            )

def augemented_qa(context: str, languageId: str) -> str:
    user_message = user_message_template2.render(contexts=context, languageId=languageId)
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