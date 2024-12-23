# Prompt Evaluation

## Setup Python Environment

1. Ensure Python and `poetry`
1. run `poetry shell`
1. run `poetry install`
1. create `.env` file in root folder

## Setup Env

``` env
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

## Evaluation with Python NoteBook

1. Follow `prompt.ipynb` to see the evaluation result

## Evaluation with AI Toolkit

1. install `ms-windows-ai-studio.windows-ai-studio` extension for VSCode
1. `Tools` -> `Evaluation` -> `Create Evaluation`
1. import dataset from `output/output.jsonl`
1. Run Evaluation from GitHub App
