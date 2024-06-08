# evaluation-exploration

This is meant to be POC for an evaluation platform, with the main purposes to ease the process of:

- Tuning prompts
- Evaluating LLMs
- Possible post-/pre- processing of data before generating citations

This will be a very raw implementation to simply see the methodology and if it is useful to even have such a platform.

- To date, nicegui only supports the groundtruth evaluation, unsupervised evaluation is WIP in `unsupervised` directory

## To start nicegui

- Run `pdm start`
- Make sure you have `.env` with:

```
HUGGINGFACEHUB_API_TOKEN="<hugging face token>"
HUGGINGFACEHUB_REPO_ID="<default hugging face model>"
```

## Evaluation

### Groundtruth

Given:

- Groundtruth:
  - Answer with citations
- To be evaluated:
  - List of documents
  - Answer
- Output:
  - Generated answer (by LLM) with citations

**Methodology**

- The evaluation is based off regex between ground truth and generated answer with citations, as a means to reduce human effort to eyeball and evaluate the results
