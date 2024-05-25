from pydantic import BaseModel
from schema.data import RawData
from typing import Dict, List


class CitationEvaluation(BaseModel):
    wrong_invalid_citations: List = []
    wrong_text_citations: List = []
    correct_valid_citations: List = []
    correct_skipped_docs: List = []
    missing_citations: List = []
    all_citations: Dict[str, List[str]] = dict()
    unmatched_text: str = ""


class GroundTruthScore(BaseModel):
    accuracy_score: float = 0.0
    precision_score: float = 0.0
    recall_score: float = 0.0
    f1_score: float = 0.0


class EvaluationResult(BaseModel):
    citation_evaluation: CitationEvaluation
    ground_truth_score: GroundTruthScore
    ground_truth_data: RawData
    candidate_answer_with_citation: str
