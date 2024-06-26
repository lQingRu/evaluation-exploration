from nicegui import ui, app
from evaluation.eval import full_evaluation, content_evaluation
from typing import List, Dict
from schema.evaluation import EvaluationResult
from schema.data import RawData
from helper.state_management import get_state, StateKey, append_state

def display_configuration(ground_truth_data: RawData):
    ui.label(f"Data ID: {ground_truth_data["data_id"]}").classes("text-xl leading-normal mt-0 mb-2 text-indigo-800")
    ui.label(f"Question: {ground_truth_data["question"]}").classes("text-sm font-normal leading-normal mt-0 mb-2 text-indigo-800")
    ui.label(f"Ground truth: {ground_truth_data["answer_with_citation"]}").classes("text-sm font-normal leading-normal mt-0 mb-2 text-indigo-800")
    return ui.aggrid(
        {
        "cellStyle": {"white-space": "pre"},
        "defaultColDef": {"flex": 1, "wrapText": True, "resizable": True},
        "columnDefs": [
            {
                "headerName": "Context ID",
                "field": "id",
                "width": 15,
            },
            {"headerName": "Text", "field": "text", "width": 100},
        ],
        ":getRowHeight": "params => Math.ceil(params.data.text.length/100) * 25",
        "rowData": ground_truth_data["docs"]
        },
    ).classes("h-96")
def display_citation(citation_list: List):
    concatenated_citations = ""
    for citation in citation_list:
        concatenated_citations += f"""
        <b>Id: {citation[1]}</b>
        <br/>
        {citation[0]}
        <br/>
        --------------------------------
        <br/>
        """        
    return concatenated_citations
def get_display_evaluation_dict(evaluation_result: EvaluationResult):
    return {
        "candidate_answer_with_citation": evaluation_result.candidate_answer_with_citation,
        "wrong_invalid_citations": display_citation(evaluation_result.citation_evaluation.wrong_invalid_citations),
        "wrong_text_citations": display_citation(evaluation_result.citation_evaluation.wrong_text_citations),
        "correct_valid_citations": evaluation_result.citation_evaluation.correct_valid_citations,
        "correct_skipped_docs": display_citation(evaluation_result.citation_evaluation.correct_skipped_docs),
        "missing_citations": display_citation(evaluation_result.citation_evaluation.missing_citations),
        "unmatched_text": evaluation_result.citation_evaluation.unmatched_text
    }
    
def display_evaluation_results(evaluation_dict):
    evaluation_grid = ui.aggrid(
    {
        "defaultColDef": {"flex": 1,  "autoHeight": True,"wrapText": True, "resizable": True},
        "columnDefs": [
            {
                "headerName": "Prompt",
                "field": "prompt",
            },
            {"headerName": "Generated answer", "field": "candidate_answer_with_citation"},
            {"headerName": "Invalid citations", "field": "wrong_invalid_citations" },
            {"headerName": "Wrong text-citations", "field": "wrong_text_citations" },
            {"headerName": "Correct valid citations", "field": "correct_valid_citations" },
            {"headerName": "Correct skipped citations", "field": "correct_skipped_docs"},
            {"headerName": "Missed citations", "field": "missing_citations" },
            {"headerName": "Unmatched text in generated answer", "field": "unmatched_text" },
        ],
        "rowData": evaluation_dict
    },html_columns=[3,4,5,6],
    ).classes("h-96")
    return evaluation_grid

async def evaluate_and_display_evaluation_results(data, selected_prompts, model):
    prompt_evaluation_dicts = []
    for prompt in selected_prompts:
        data_obj = RawData(**data)
        evaluation_result =  await full_evaluation(data_obj, prompt["prompt"], model)
        display_evaluation_dict = get_display_evaluation_dict( evaluation_result)
        display_evaluation_dict["prompt"]= prompt["prompt"]
        prompt_evaluation_dicts.append(display_evaluation_dict)
    display_evaluation_results(prompt_evaluation_dicts)

@ui.page("/eval")
async def eval():
    ui.label("Evaluation Results").style(
        "color: #6E93D6; font-size: 200%; font-weight: 300"
    )
    selected_prompts = get_state(StateKey.SELECTED_PROMPTS)
    selected_data = get_state(StateKey.SELECTED_DATA)
    model = get_state(StateKey.SELECTED_MODEL)

    ui.label("Evaluating model: %s" % model)
    for data in selected_data:
        display_configuration(data)
        await evaluate_and_display_evaluation_results(data, selected_prompts, model)

@ui.page("/eval-without-model")
def eval_without_model():
    import pandas as pd
    ui.label("Evaluation Results").style(
        "color: #6E93D6; font-size: 200%; font-weight: 300"
    )
    def display_evaluation_results(evaluation_dict):
        evaluation_grid = ui.aggrid(
        {
            "defaultColDef": {"flex": 1, "autoHeight": True, "wrapText": True, "resizable": True},
            "columnDefs": [
                {"headerName": "Generated answer", "field": "candidate_answer_with_citation"},
                {"headerName": "Invalid citations", "field": "wrong_invalid_citations" },
                {"headerName": "Wrong text-citations", "field": "wrong_text_citations" },
                {"headerName": "Correct valid citations", "field": "correct_valid_citations" },
                {"headerName": "Correct skipped citations", "field": "correct_skipped_docs", "hide": True },
                {"headerName": "Missed citations", "field": "missing_citations" },
                {"headerName": "Unmatched text in generated answer", "field": "unmatched_text" },
            ],
            "rowData": evaluation_dict,
            "alwaysShowHorizontalScroll": True
        },html_columns=[2,3,4,5],
        ).classes("max-h-60")
        return evaluation_grid

    data_to_citations = get_state(StateKey.CUSTOM_DATA_TO_CITATION)
    for data_citation in data_to_citations:
       display_configuration(data_citation["data"])
       data_obj = RawData(**data_citation["data"])
       evaluation_result = content_evaluation(data_obj, data_citation["citation_to_eval"])
       evaluation_dict = get_display_evaluation_dict(evaluation_result)
       display_evaluation_results([evaluation_dict])
