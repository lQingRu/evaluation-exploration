from helper.text_splitter import (
    split_text_with_citations,
    find_immediate_citations,
)


def test_positive_single_text_splitter():
    answer_with_citation = "Sentence 1 [1]. Sentence 2 [2]"
    groups, unmatched_texts = split_text_with_citations(answer_with_citation)
    assert groups[0] == ("Sentence 1 ", ["1"])
    assert groups[1] == (". Sentence 2 ", ["2"])
    assert unmatched_texts == ""


def test_positive_multiple_text_splitter():
    answer_with_citation = "Sentence 1 [1][2]. Sentence 2 [2]"
    groups, unmatched_texts = split_text_with_citations(answer_with_citation)
    assert groups[0] == ("Sentence 1 ", ["1", "2"])
    assert groups[1] == (". Sentence 2 ", ["2"])
    assert unmatched_texts == ""


def test_negative_text_splitter():
    answer_with_citation = "Sentence 1 [1][2]. Sentence 2 [2]."
    groups, unmatched_texts = split_text_with_citations(answer_with_citation)
    assert groups[0] == ("Sentence 1 ", ["1", "2"])
    assert groups[1] == (". Sentence 2 ", ["2"])
    assert unmatched_texts == ""


# NOTE: This demonstrates how the current text splitter, does not have very loose citation matches
## e.g.: We may want to group [1], [3][2] together for the same text
def test_dirty_data_text_splitter():
    answer_with_citation = "   \nSentence 1   \n    [1], [3][2]"
    groups, unmatched_texts = split_text_with_citations(answer_with_citation)
    print(groups)
    assert groups[0] == ("Sentence 1   \n    ", ["1"])
    assert groups[1] == (", ", ["3", "2"])
    assert unmatched_texts == ""


def test_exact_immediate_citations():
    chunk = "A healthy diet helps to maintain a balanced weight [1], improves heart health[2], and boosts the immune system[3]. It also contributes to better mental health[4] and can prevent chronic diseases[5]."
    subset_text = "A healthy diet helps to maintain a balanced weight "
    citations = find_immediate_citations(chunk, subset_text)
    assert citations == ["1"]


def test_exact_whitespaces_immediate_citations():
    chunk = "A healthy diet helps to maintain a balanced weight [1], improves heart health[2], and boosts the immune system[3]. It also contributes to better mental health[4] and can prevent chronic diseases[5]."
    subset_text = "\n   A healthy diet helps to maintain a balanced weight    \n\n"
    citations = find_immediate_citations(chunk, subset_text)
    assert citations == ["1"]


def test_subset_non_exact_immediate_citations():
    chunk = "A healthy diet helps to maintain a balanced weight [1], improves heart health[2], and boosts the immune system[3]. It also contributes to better mental health[4] and can prevent chronic diseases[5]."
    subset_text = "A healthy diet helps to maintain a balanced"
    citations = find_immediate_citations(chunk, subset_text)
    assert citations == ["1"]


# Here permutates all possible combinations (but regex itself might be not sufficient)
# def test_1():
#     answer_with_citation = "abc [2] def [3]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc ", ["2"])
#     assert groups[1] == (" def ", ["3"])
#     assert unmatched_texts == ""


# def test_2():
#     answer_with_citation = "abc [2] def"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc ", ["2"])
#     assert unmatched_texts == "def"


# def test_3():
#     answer_with_citation = "abc [2,3] def [3]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc ", ["2", "3"])
#     assert groups[1] == (" def ", ["3"])
#     assert unmatched_texts == ""


# def test_4():
#     answer_with_citation = "abc [2,3,] def [3]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc ", ["2", "3"])
#     assert groups[1] == (" def ", ["3"])
#     assert unmatched_texts == ""


# def test_5():
#     answer_with_citation = "abc [] def [3]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc [] def ", ["3"])
#     assert unmatched_texts == ""


# def test_6():
#     answer_with_citation = "abc [abc] def [3]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc [abc] def ", ["3"])
#     assert unmatched_texts == ""


# def test_7():
#     answer_with_citation = "abc [abc] def [3a]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert unmatched_texts == "abc [abc] def [3a]"


# def test_8():
#     answer_with_citation = "abc [1 def [3,]"
#     groups, unmatched_texts = split_text_with_citations(answer_with_citation)
#     print(groups)
#     assert groups[0] == ("abc [1 def ", ["3"])
#     assert unmatched_texts == ""
