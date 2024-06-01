from nicegui import ui, app, events
from helper.data_loader import *
import json


def display_truncated_data_docs(data_list):
    truncated_data_docs = []
    for data in data_list:
        new_object = {**data}
        max_docs = min(len(data["docs"]), 3)
        new_object["docs"] = ""
        for doc in data["docs"][:max_docs]:
            new_object[
                "docs"
            ] += f"""
                <b>Id: {doc["id"]}</b>
                <br/>
                {doc["text"]}
                <br/>
                """
        truncated_data_docs.append(new_object)
    return truncated_data_docs


def display_data_grid(data_list_dict):
    return ui.aggrid(
        {
            "defaultColDef": {"flex": 1, "wrapText": True, "resizable": True},
            "columnDefs": [
                {
                    "headerName": "Data ID",
                    "field": "data_id",
                    "width": 8,
                    "checkboxSelection": True,
                },
                {"headerName": "Question", "field": "question", "width": 15},
                {
                    "headerName": "Answer with citation",
                    "field": "answer_with_citation",
                    "width": 15,
                },
                {"headerName": "Docs", "field": "docs", "width": 100},
            ],
            ":getRowHeight": "params => params.data.docs.length > 3? 200: 120",
            "rowData": display_truncated_data_docs(data_list_dict),
        },
        html_columns=[3],
    ).classes("h-96")


def add_custom_data(e: events.UploadEventArguments, data_list_dict, grid):
    try:
        data_json = json.loads(e.content.read())
        app.storage.user["dataset"].append(data_json)
        data_list_dict.append(data_json)
        display_truncated_raw_data = display_truncated_data_docs([data_json])
        grid.options["rowData"] += display_truncated_raw_data
        grid.update()
    except Exception as e:
        ui.notify(f"Error uploading file: {str(e)}")


def display_custom_data_upload(data_list_dict, grid):
    ui.upload(
        label="Custom dataset",
        on_upload=lambda e: add_custom_data(e, data_list_dict, grid),
    ).classes("max-w-full").props("accept=.json")
    ui.markdown(
        f"""
             Dataset needs to be in `.json` with the following fields:
             
             | Field | Data Type | Remarks|
             | --- | --- | --- |
             | `data_id` | int | Unique number including the sample dataset|
             | `question` | str | Question to answer |
             | `answer` | str | Without citation |
             | `answer_with_citation` | str | Same content as `answer` but includes in-text citation of format [1] where 1 is the docs.id |
             | `docs` | list of embedded object | See embedded field data type|
             | `docs.id` | str | e.g.: "1" | 
             | `docs.text` | str | Text of context |
             | `has_answer` | bool |  Whether the text is part of the citations in `answer_with_citation` | 
        """
    )
    return data_list_dict, grid


@ui.page("/")
def main():
    # Show different inputs
    data_list = get_all_sample_data(dir="./sample/data")
    data_list_dict = [data.model_dump() for data in data_list]

    prompts = get_sample_prompts(path="./sample/prompts/prompts.json")
    huggingface_models = ["mistralai/mixtral-8x7b-instruct-v0.1"]
    app.storage.user["dataset"] = data_list_dict

    ui.label("Welcome to LLM custom evaluation platform").style(
        "color: #6E93D6; font-size: 200%; font-weight: 300"
    )

    with ui.grid(columns=2):

        ui.label("1. Select a model to evaluate:")
        model = ui.select(
            options=huggingface_models,
        )
    ui.label("2. Select a prompt to evaluate:")
    prompt_data = []
    for id, prompt in prompts.items():
        prompt_data.append({"id": id, "prompt": prompt.get_concatenated_prompt()})

    prompt_grid = ui.aggrid(
        {
            "defaultColDef": {
                "flex": 1,
                "wrapText": True,
                "resizable": True,
            },
            "columnDefs": [
                {
                    "headerName": "Prompt ID",
                    "field": "id",
                    "width": 8,
                    "checkboxSelection": True,
                },
                {"headerName": "Prompt", "field": "prompt", "width": 200},
            ],
            ":getRowHeight": "params => params.data.prompt.length > 50? 150: 100",
            "rowData": app.storage.user.get("prompt_data", prompt_data),
            "rowSelection": "multiple",
        },
    ).classes("max-h-72")

    custom_prompt_data = []

    def add_custom_prompt(value):
        custom_prompt_id = len(prompt_data) + 1
        prompt = {"id": custom_prompt_id, "prompt": value}
        prompt_data.append(prompt)
        custom_prompt_data.append(prompt)
        app.storage.user["prompt_data"] = custom_prompt_data
        prompt_grid.options["rowData"].append(prompt)
        prompt_grid.update()

    with ui.grid(columns=2).classes("w-full items-end"):
        custom_prompt = ui.textarea(label="Custom Prompt").classes(
            "text-sm leading-normal mt-0 mb-2 text-indigo-800"
        )
        ui.button(
            "Add Prompt", on_click=lambda: add_custom_prompt(custom_prompt.value)
        ).classes("w-2/6 h-1/6 text-xs")
    ui.label("3. Select a dataset to evaluate:")

    app.storage.user["prompt_data"] = prompt_data
    data_grid = display_data_grid(app.storage.user["dataset"])
    data_grid.options["rowSelection"] = "multiple"
    data_list_dict, data_grid = display_custom_data_upload(data_list_dict, data_grid)

    async def prepare_evaluation():
        prompt_rows = await prompt_grid.get_selected_rows()
        data_rows = await data_grid.get_selected_rows()
        if prompt_rows and data_rows:
            full_data = []
            for data in data_rows:
                full_data.append(data_list_dict[data["data_id"] - 1])
        elif prompt_rows is None and data_rows is None:
            ui.notify("No prompts and No data selected.")
            return
        elif prompt_rows is None:
            ui.notify("No prompts selected.")
            return
        elif data_rows is None:
            ui.notify("No data selected.")
            return
        app.storage.user["selected_prompts"] = prompt_rows
        app.storage.user["selected_data"] = full_data
        app.storage.user["model"] = model.value
        ui.navigate.to("/eval")

    ui.button(
        "Evaluate",
        on_click=prepare_evaluation,
    )


@ui.page("/custom")
def custom():
    data_list = get_all_sample_data(dir="./sample/data")
    data_list_dict = []
    data_id_dict = dict()
    for data in data_list:
        data_list_dict.append(data.model_dump())
        data_id_dict[data.data_id] = data

    ui.label("Welcome to citations custom evaluation platform").style(
        "color: #6E93D6; font-size: 200%; font-weight: 300"
    )

    data_grid = display_data_grid(data_list_dict)
    data_list_dict, data_grid = display_custom_data_upload(data_list_dict, data_grid)
    gt_citations_to_evaluate = []
    container = ui.row()
    with container:
        with ui.grid(columns=2).classes("w-auto items-end"):
            ui.label("Choose a Data ID").classes("text-sm text-indigo-800")
            gt_id = ui.select(
                options=[data["data_id"] for data in data_list_dict],
            )
            ui.label("Input text to evaluate citation").classes(
                "text-sm leading-normal mt-0 mb-2 text-indigo-800"
            )
            to_eval = ui.textarea().classes("w-96")

    def add_gt_eval():
        new = {
            "data": data_id_dict[gt_id.value].model_dump(),
            "citation_to_eval": to_eval.value,
        }
        gt_citations_to_evaluate.append(new)
        grid.options["rowData"] = gt_citations_to_evaluate
        grid.update()

    ui.button("ADD", on_click=lambda: add_gt_eval())

    grid = ui.aggrid(
        {
            "defaultColDef": {
                "flex": 1,
                "wrapText": True,
                "resizable": True,
            },
            "columnDefs": [
                {
                    "headerName": "Groundtruth",
                    "field": "data.answer_with_citation",
                    "width": 8,
                    "checkboxSelection": True,
                },
                {
                    "headerName": "Citation to evaluate",
                    "field": "citation_to_eval",
                    "width": 200,
                },
            ],
            ":getRowHeight": "params => params.data.citation_to_eval.length > 50? 150: 100",
            "rowData": gt_citations_to_evaluate,
        },
    ).classes("h-60")

    async def prepare_evaluation():
        app.storage.user["data_to_citation"] = gt_citations_to_evaluate
        ui.navigate.to("/eval-without-model")

    ui.button(
        "Evaluate",
        on_click=prepare_evaluation,
    )
