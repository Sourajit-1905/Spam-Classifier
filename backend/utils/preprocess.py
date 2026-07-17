import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

ps = PorterStemmer()
STOPWORDS = set(stopwords.words('english'))
PUNCTUATION = set(string.punctuation)


def transform_message(text: str) -> str:
    """
    Cleans and preprocesses an SMS message for the model:
    1. Lowercase
    2. Tokenize
    3. Remove special characters (keep only alphanumeric tokens)
    4. Remove stopwords and punctuation
    5. Stem each word
    """

    # 1. Lower case
    text = text.lower()

    # 2. Tokenize
    tokens = nltk.word_tokenize(text)

    # 3. Keep only alphanumeric tokens
    words = [word for word in tokens if word.isalnum()]

    # 4. Remove stopwords and punctuation
    words = [
        word for word in words
        if word not in STOPWORDS and word not in PUNCTUATION
    ]

    # 5. Stem
    words = [ps.stem(word) for word in words]

    return " ".join(words)