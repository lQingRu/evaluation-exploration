from pydantic import BaseModel
from typing import List, Optional, Dict
from helper.text_splitter import split_text_with_citations


class GroundTruthContext(BaseModel):
    has_answer: bool
    text: str


class GroundTruthData(BaseModel):
    answer_with_citation: str
    docs: List[GroundTruthContext]

    def get_split_text_citation(self):
        return split_text_with_citations(self.answer_with_citation)[0]

    def get_valid_citations_map(self) -> Dict[str, List[GroundTruthContext]]:
        citations_map: Dict[str, List[GroundTruthContext]] = dict()
        for doc in self.docs:
            if doc.has_answer:
                citations_map.setdefault(doc.id, []).append(doc)
        return citations_map

    def get_docs_has_answer_map(self) -> Dict[str, bool]:
        has_answer_map: Dict[str, bool] = dict()
        for doc in self.docs:
            has_answer_map[doc.id] = doc.has_answer
        return has_answer_map

    def get_docs_no_answer(self) -> List[GroundTruthContext]:
        docs_no_answer: List[GroundTruthContext] = []
        for doc in self.docs:
            if doc.has_answer == False:
                docs_no_answer.append(doc)
        return docs_no_answer


class RawDataContext(GroundTruthContext):
    id: str
    title: Optional[str] = ""


class RawData(GroundTruthData):
    data_id: int
    question: str
    answer: str
    docs: List[RawDataContext]
