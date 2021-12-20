import datetime
import re
import string

from nltk.tokenize import word_tokenize
import unicodedata
from greek_stemmer import GreekStemmer
from .stopwords import STOPWORDS
from ..backend.speech import Speech


def stem(tokens: list[str]) -> list:
    # Keep the stemmer object between calls
    stem.stemmer = GreekStemmer()
    return [stem.stemmer.stem(token) for token in tokens]


def remove_accents(tokens: list) -> list:
    # https://stackoverflow.com/questions/33328645/how-to-remove-accent-in-python-3-5-and-get-a-string-with-unicodedata-or-other-so
    nfkd_forms = [unicodedata.normalize('NFKD', token) for token in tokens]
    tokens = [u"".join([c for c in nfkd_form if not unicodedata.combining(c)]) for nfkd_form in nfkd_forms]
    return tokens


def remove_stopwords(tokens: list, stopwords: set) -> list:
    return [token for token in tokens if token.lower() not in stopwords]


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation)).removesuffix("\n")


def capitalize(tokens: list[str]) -> list[str]:
    return [token.upper() for token in tokens]


def process_raw_speech_text(speech_text: str, word_limit=0, perform_stemming=True, delete_stopwords=True) -> list:
    """
    Process a speech string. Tokenizes, removes punctuation, stopwords, accents and optionally stems the words. Returns
    the tokenized speech. Stemming considerably increases the processing time required.
    :param speech_text: The string of the speech
    :param word_limit: Speeches with fewer than word_limit words are not processed. An empty list is returned. No limit
        by default.
    :param perform_stemming Whether to stem the words
    :param delete_stopwords Whether to remove stopwords from the text
    :return:
    """
    speech_text = remove_punctuation(speech_text)
    tokens = word_tokenize(speech_text, language="greek")
    if len(tokens) >= word_limit:
        if delete_stopwords:
            tokens = remove_stopwords(tokens, STOPWORDS)
        tokens = remove_accents(tokens)
        tokens = capitalize(tokens)
        if perform_stemming:
            tokens = stem(tokens)
        return tokens
    else:
        return []


def process_csv_line(line_text: str) -> Speech:
    """
    Get a line from the CSV file and extract the information in it.
    :param line_text: String of a line in the CSV file
    :return: Speech object with the speech text and metadata.
    """
    # Some csv lines contain comma-separated arrays, so a simple split() is not enough.
    # Keep this as a static variable to avoid recompiling it between calls
    # Regex to find an array in the line. Includes the surrounding brackets
    process_csv_line.array_regex = re.compile(r',["]?(\[[^\[]*])["]?,')
    numbers_only_regex = re.compile(r'[^0-9]')
    # Find all arrays in the line
    results = process_csv_line.array_regex.findall(line_text)
    # Remove the arrays and replace them with empty text
    new_line_text = process_csv_line.array_regex.sub(",,", line_text).split(",")
    # Every line has a government field
    government = results[0].removeprefix("['").removesuffix("']")
    # Not all lines have a member or role associated with them.
    if len(results) > 1:
        roles = results[1].removeprefix("[").removesuffix("]").replace("'", "").split(",")
    else:
        roles = ""
    # Get the rest of the data
    member_name = new_line_text[0]
    date_string = new_line_text[1]
    sitting_date = datetime.date(int(date_string[6:10]), int(date_string[3:5]), int(date_string[0:2]))
    parliamentary_period = int(numbers_only_regex.sub('', new_line_text[2]) or -1)
    parliamentary_session = int(numbers_only_regex.sub('', new_line_text[3]) or -1)
    parliamentary_sitting = int(numbers_only_regex.sub('', new_line_text[4]) or -1)
    party = new_line_text[5]
    # Skip roles and government
    region = new_line_text[7]
    gender = new_line_text[9]
    speech = ""
    speech = speech.join(new_line_text[10:])
    return Speech(member_name, sitting_date, parliamentary_period, parliamentary_session, parliamentary_sitting, party,
                  government, region, roles, gender, speech)
