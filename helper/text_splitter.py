import re


def split_text_with_citations(text: str):
    text = text.strip(" .,;?!")
    ## Match 2 groups:
    ### 1st group (Text that has citation):
    # (i) Match any characters except line breaks
    # (ii) Match line breaks/whitespaces
    # (iii) Match only 0 or 1 times
    # ## 2nd group (Citations): Match [digit(s)]
    pattern = re.compile(r"(.+?\s*)(\[\d+\])+")
    matches = pattern.finditer(text)

    groups = []
    last_end = 0

    for match in matches:
        text_segment = match.group(1)
        citations = re.findall(r"\d+", match.group(0)[len(text_segment) :])
        groups.append((text_segment, citations))

        last_end = match.end()

    unmatched_text = text[last_end:].strip()

    return groups, unmatched_text


def find_immediate_citations(chunk_of_text, subset_text):
    # Strip unnecessary characters from subset_text
    subset_text = subset_text.strip(" .,;?!\n")

    # Find the subset text in the chunk
    match = re.search(re.escape(subset_text), chunk_of_text)
    if not match:
        return []

    # Get the remaining text after the matched text
    substring = chunk_of_text[match.end() :]

    # Get matched citations
    citations = re.findall(r"(\[[^a-zA-Z]*\d[^a-zA-Z]*\])", substring)
    if len(citations) > 0:
        matched_citations = citations[0]
        return re.findall(r"\[(\d)+\]+", matched_citations)
    return []
