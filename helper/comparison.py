from rapidfuzz import fuzz


def is_similiar_text(text_1: str, text_2: str, threshold: float = 90):
    score = fuzz.partial_ratio(text_1, text_2)
    if score >= threshold:
        return True
    else:
        return False
