import sqlite3
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

from constants import (
    SQL_DATABASE_FILENAME
)
from utils import (
    inverted_index,
    idf,
    preprocess_text
)


def rank_and_retrieve_pages_with_tfidf(query, top_k=20):

    query = query.lower()
    processed_tokens = preprocess_text(query)

    scores = defaultdict(float)

    for term in processed_tokens:
        if term not in inverted_index:
            continue

        postings = inverted_index[term] # -> {pageId: tf}
        term_idf = idf.get(term, 0.0)

        for page_id, tf in postings.items():
            scores[page_id] += tf * term_idf

    ranked_docs = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [page_id for page_id, score in ranked_docs[:top_k]]

def search_with_tfidf(query):
    # Step 1: Get ranked pageIds from TF–IDF
    pageIds = rank_and_retrieve_pages_with_tfidf(query, top_k=200)
    if not pageIds:
        return []

    # Step 2: Preprocess query tokens for matching
    
    query_tokens = preprocess_text(query)

    # Step 3: Connect to DB and fetch metadata
    with sqlite3.connect(SQL_DATABASE_FILENAME) as conn:
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(pageIds))
        sql = f"SELECT PageId, Title, Snippet, URL FROM articles WHERE PageId IN ({placeholders})"
        cursor.execute(sql, pageIds)
        results = cursor.fetchall()

    # Step 4: Build lookup dict for ordering
    results_dict = {row[0]: row for row in results}
    docs = [results_dict[pid] for pid in pageIds if pid in results_dict]

   
    return docs
