# Prompt Evaluation

## Setup Python Environment

1. Ensure Python and `poetry`
1. Run `poetry shell`
1. Run `poetry install`
1. Create `.env` file in root folder
1. Install spectral globally `npm install -g @stoplight/spectral-cli`

## Setup Env
if use RBAC just set `RBAC` as `TRUE`, else set `FALSE`

``` env
RBAC=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

## Evaluation with Python NoteBook

1. Follow `prompt-eval.ipynb` to see the evaluation result
1. All results exist in `results` folder