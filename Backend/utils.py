import re
import nltk
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer

from constants import (
    INVERTED_INDEX_FILE,
    INVERSE_DOCUMENT_FREQUENCY_FILE
)

print("Downloading nltk resources...")
nltk.download('punkt')
nltk.download('stopwords')

print("Loading Embedding Model, Stemmer, and Stopwords...")
STEMMER = PorterStemmer()
STOP_WORDS = set(stopwords.words('english'))
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')


print("Loading Inverted Index file...")
with open(INVERTED_INDEX_FILE, "rb") as f:
    inverted_index = pickle.load(f)

print("Loading Inverse Document Frequency file...")
with open(INVERSE_DOCUMENT_FREQUENCY_FILE, "rb") as f:
    idf_data = pickle.load(f)

idf = idf_data['idf']
total_doc_count = idf_data['total_documents']
doc_lengths = idf_data["doc_lengths"]
avg_doc_length = idf_data["avg_doc_length"]


def preprocess_text(text) -> list[str]:

    # Step 1: Normalize the text to keep only alphanumeric text and single space instead of multiple spaces.
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Tokenize the entire text
    tokens = word_tokenize(text)

    # Step 3: For each token -> filter out stopwords and tokens with only 1 character, lowercase, and stem to base form
    processed_tokens = [
        STEMMER.stem(token)
        for token in tokens
        if (token not in STOP_WORDS and len(token) > 1)
    ]

    # Step 4: Return the processed tokens
    return processed_tokens
