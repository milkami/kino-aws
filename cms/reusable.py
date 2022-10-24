import re


def create_rss_title(string):
    string = string.lower()
    string = re.sub(
        r'\(|\)|\[|\]|_|;|\+|\*|"|/|=|:|\.|-|,|\?|!|`|\|', " ", string
    ).strip()
    string = re.sub(
        r"\u201C|\u201D|\u201E|\u201F|\u00B7|\u2013|\u00AB|\u00BB", " ", string
    ).strip()
    string = re.sub(r"\u00B4", "'", string).strip()
    string = re.sub(r" und | and ", " & ", string).strip()
    string = re.sub(r"\s+", " ", string)

    return string
