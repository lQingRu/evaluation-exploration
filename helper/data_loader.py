import json
from schema.prompt import Prompt
from schema.data import RawData, RawDataContext
from typing import Dict, List
import os


def get_sample_prompts(path: str) -> Dict[int, Prompt]:
    prompt_dict: Dict[int, Prompt] = dict()
    with open(path, "r") as f:
        data = json.load(f)
    for d in data:
        prompt_dict[d["id"]] = Prompt.model_validate(d)
    return prompt_dict


def get_sample_data(path: str) -> RawData:
    with open(path, "r") as f:
        data = json.load(f)
    return RawData.model_validate(
        {
            "data_id": data["data_id"],
            "question": data["question"],
            "answer": data["answer"],
            "answer_with_citation": data["answer_with_citation"],
            "docs": [
                RawDataContext.model_validate(
                    {
                        "id": doc["id"],
                        "text": doc["text"],
                        "has_answer": doc["has_answer"],
                    }
                )
                for doc in data["docs"]
            ],
        }
    )


def get_all_sample_data(dir: str) -> List[RawData]:
    data_list: List[RawData] = []
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        data_list.append(get_sample_data(file_path))
    return data_list
