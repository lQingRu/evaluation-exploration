from schema.data import GroundTruthData
from helper.text_splitter import split_text_with_citations, find_immediate_citations
from typing import Dict, List
from schema.evaluation import *
from helper.comparison import is_similiar_text


def compare_ground_truth(
    answer_with_citation: str, ground_truth: GroundTruthData
) -> CitationEvaluation:
    """Compare generated response and ground truth"""
    split_answer = split_text_with_citations(answer_with_citation)
    text_citations_list = split_answer[0]
    unmatched_text = split_answer[1]

    ## 1. Sanity check (Based off docs ids)
    wrong_invalid_citations = []  # Invalid citation
    wrong_text_citations = []  # Wrong text-citation pair
    correct_valid_citations = []
    correct_skipped_docs = []
    missing_citations = []
    all_citations: Dict[str, List[str]] = dict()

    ## 2. Generated citation content check
    ground_truth_split_citations = ground_truth.get_split_text_citation()
    ground_truth_docs_has_answer_map = ground_truth.get_docs_has_answer_map()

    for text, citations in text_citations_list:
        ground_truth_citations = find_immediate_citations(
            ground_truth.answer_with_citation, text
        )
        for citation in citations:
            # if len(ground_truth_citations) == 0
            #     wrong_text_citations.append((text, citation))
            #     break
            has_answer = ground_truth_docs_has_answer_map.get(citation)
            ### A. Is citation valid?
            if has_answer is None:
                wrong_invalid_citations.append((text, citation))
            else:
                if has_answer is False:
                    wrong_text_citations.append((text, citation))
                else:
                    ### B. Is text tagged to the correct doc?
                    if citation in ground_truth_citations:
                        correct_valid_citations.append((text, citation))
                    else:
                        similar_citation = False
                        for gt_citation in ground_truth_split_citations:
                            if (
                                is_similiar_text(text, gt_citation[0])
                                and citation == gt_citation[1]
                            ):
                                similar_citation = True
                                break
                        if similar_citation is True:
                            correct_valid_citations.append((text, citation))
                        else:
                            wrong_text_citations.append((text, citation))
            all_citations.setdefault(citation, []).append(text)

    ## 3. Generated citation absence check
    for text, citations in ground_truth_split_citations:
        generated_answer_citations = find_immediate_citations(
            answer_with_citation, text
        )

        ### C. Is there missing citation in generated answer?
        if generated_answer_citations is None:
            for citation in citations:
                missing_citations.append((text, citation))
        else:
            for citation in citations:
                if citation not in generated_answer_citations:
                    missing_citations.append((text, citation))

    ## 4. Generated citation skipped check
    ground_truth_docs_no_answer = ground_truth.get_docs_no_answer()

    for ground_truth_doc in ground_truth_docs_no_answer:
        if all_citations.get(ground_truth_doc.id) is None:
            correct_skipped_docs.append((ground_truth_doc.id, ground_truth_doc.text))
    return CitationEvaluation(
        wrong_invalid_citations=wrong_invalid_citations,
        wrong_text_citations=wrong_text_citations,
        correct_valid_citations=correct_valid_citations,
        correct_skipped_docs=correct_skipped_docs,
        missing_citations=missing_citations,
        all_citations=all_citations,
        unmatched_text=unmatched_text,
    )


def calculate_ground_truth_scores(
    citation_evaluation: CitationEvaluation,
) -> GroundTruthScore:
    true_negatives = len(citation_evaluation.correct_skipped_docs)
    # False positives here include:
    ## 1. Wrong text_citation pair (citation is tagged to wrong text)
    ## 2. Invalid citation (citation does not exist in context)
    ## 3. Wrong citation (citation does not contain in ground truth answer with citation)
    false_positives = len(citation_evaluation.wrong_invalid_citations) + len(
        citation_evaluation.wrong_text_citations
    )
    true_positives = len(citation_evaluation.correct_valid_citations)
    false_negatives = len(citation_evaluation.missing_citations)
    try:
        accuracy_score = (true_positives + true_negatives) / (
            true_positives + true_negatives + false_positives + false_negatives
        )
    except:
        accuracy_score = 0

    try:
        precision_score = true_positives / (true_positives + false_positives)
    except:
        precision_score = 0

    try:
        recall_score = true_positives / (true_positives + false_negatives)
    except:
        recall_score = 0

    try:
        f1_score = (2 * precision_score * recall_score) / (
            precision_score + recall_score
        )
    except:
        f1_score = 0
    return GroundTruthScore(
        accuracy_score=accuracy_score,
        precision_score=precision_score,
        recall_score=recall_score,
        f1_score=f1_score,
    )
