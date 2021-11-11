import re
import sys

from adoc_check import ast


# from settings at https://titlecase.com/
TITLE_CASE_EXCEPTIONS = set(
    [
        "a",
        "abaft",
        "about",
        "above",
        "afore",
        "after",
        "along",
        "amid",
        "among",
        "an",
        "apud",
        "as",
        "aside",
        "at",
        "atop",
        "below",
        "but",
        "by",
        "circa",
        "down",
        "for",
        "from",
        "given",
        "in",
        "into",
        "lest",
        "like",
        "mid",
        "midst",
        "minus",
        "near",
        "next",
        "of",
        "off",
        "on",
        "onto",
        "out",
        "over",
        "pace",
        "past",
        "per",
        "plus",
        "pro",
        "qua",
        "round",
        "sans",
        "save",
        "since",
        "than",
        "thru",
        "till",
        "times",
        "to",
        "under",
        "until",
        "unto",
        "up",
        "upon",
        "via",
        "vice",
        "with",
        "worth",
        "the",
        "and",
        "nor",
        "or",
        "yet",
        "so",
    ]
)


def is_titlecase(s):
    """
    >>> is_titlecase("This Is a Test")
    (True, [])
    >>> is_titlecase("This is a test")
    (False, ['is', 'test'])
    """
    # remove things in backticks, which should be ignored for title case
    s = re.sub("`[^`]*`", "", s)

    words = s.split()
    bad_words = []
    for i, word in enumerate(words):
        first_or_last = i == 0 or i == len(words) - 1
        if first_or_last or not word.lower() in TITLE_CASE_EXCEPTIONS:
            if word[0].isalpha() and word[0].islower():
                bad_words.append(word)
        if not first_or_last and word.lower() in TITLE_CASE_EXCEPTIONS:
            if word.lower() != word:
                bad_words.append(word)
    return len(bad_words) == 0, bad_words


def get_headers(path):
    document = ast.parse(path)

    header_nodes = []

    def _get_headers(node):
        if node["type"] == "AsciiDoc:HEADING":
            header_nodes.append(node)
            return False
        return True

    ast.walk(document, _get_headers)
    return header_nodes


def parse_header(file, node):
    header = {
        "file": file,
        "startOffset": node["startOffset"],
        "endOffset": node["endOffset"],
    }

    text = ""
    text += re.sub("^=+ ", "", node["children"][0]["text"])

    for child in node["children"][1:]:
        if child["type"] == "AsciiDoc:HEADING_TOKEN":
            text += child["text"]
            continue
        if child["type"] == "AsciiDoc:ATTRIBUTE_REF":
            assert (
                child["children"][1]["text"] == "nbsp"
            ), f"unexpected attribute ref {child}"
            text += " "
            continue
        assert False, f"unexpected child {child}"

    header["text"] = text
    return header


def get_bad_headers(files):
    bad_headers = []
    for file in files:
        file_headers = get_headers(file)
        parsed_headers = [parse_header(file, header) for header in file_headers]
        for parsed_header in parsed_headers:
            good, bad_words = is_titlecase(parsed_header["text"])
            if not good:
                parsed_header["badWords"] = bad_words
                bad_headers.append(parsed_header)
    return bad_headers


def main():
    files = sys.argv[1:]

    bad_headers = get_bad_headers(files)
    if len(bad_headers) == 0:
        sys.exit(0)
    for bad_header in bad_headers:
        file = bad_header["file"]
        start_offset = bad_header["startOffset"]
        end_offset = bad_header["endOffset"]
        text = bad_header["text"]
        bad_words = ", ".join(bad_header["badWords"])
        print(
            f"In file {file} {start_offset}..{end_offset} '{text}', the following words are not in correct case: {bad_words}"
        )
    sys.exit(1)


if __name__ == "__main__":
    main()
