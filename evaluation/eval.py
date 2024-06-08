from langchain_community.llms import HuggingFaceEndpoint
from helper.data_loader import *
from langchain_core.prompts import PromptTemplate
from evaluation.groundtruth import compare_ground_truth, calculate_ground_truth_scores
from schema.evaluation import *
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.environ["HUGGINGFACEHUB_API_TOKEN"]
HUGGINGFACEHUB_REPO_ID = os.environ["HUGGINGFACEHUB_REPO_ID"]


def generate_citations(answer: str, context: List[Dict], prompt: str, model: str):
    """Generate citations with response & context"""
    llm = HuggingFaceEndpoint(
        repo_id=HUGGINGFACEHUB_REPO_ID if model == None else model,
        temperature=0.01,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    )
    prompt_template = PromptTemplate.from_template(prompt)
    llm_chain = prompt_template | llm
    response = llm_chain.invoke({"answer": answer, "context": context})
    return response


async def full_evaluation(data: RawData, prompt: str, model: str):
    contexts = [{"id": d.id, "text": d.text} for d in data.docs]
    generated_answer_with_citations = generate_citations(
        data.answer, contexts, prompt, model
    )
    return content_evaluation(data, generated_answer_with_citations)


def content_evaluation(data: RawData, answer: str):
    citation_evaluation = compare_ground_truth(answer, data)
    ground_truth_score = calculate_ground_truth_scores(citation_evaluation)
    evaluation_result = EvaluationResult(
        citation_evaluation=citation_evaluation,
        ground_truth_score=ground_truth_score,
        ground_truth_data=data,
        candidate_answer_with_citation=answer,
    )
    return evaluation_result
