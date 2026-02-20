import sqlite3
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

from constants import (
    SQL_DATABASE_FILENAME
)
from utils import (
    EMBEDDING_MODEL,
    inverted_index,
    idf,
    doc_lengths,
    avg_doc_length,
    preprocess_text
)


def rank_and_retrieve_pages_with_bm25(query, top_k=20, k1=1.5, b=0.75):

    query = query.lower()
    processed_tokens = preprocess_text(query)

    scores = defaultdict(float)

    for term in processed_tokens:
        if term not in inverted_index:
            continue

        postings = inverted_index[term]     # {page_id: tf}
        term_idf = idf.get(term, 0.0)

        for page_id, tf in postings.items():
            dl = doc_lengths.get(page_id, 0)

            denom = tf + k1 * (1 - b + b * (dl / avg_doc_length))
            bm25_tf = (tf * (k1 + 1)) / denom if denom != 0 else 0

            scores[page_id] += term_idf * bm25_tf

    ranked_docs = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [page_id for page_id, _ in ranked_docs[:top_k]]


def search_with_bm25(query):

    # Step 1: First Stage Ranking: Get the BM25 Ranked Candidate document IDs from inverted index.
    pageIds = rank_and_retrieve_pages_with_bm25(query, top_k=200)
    if not pageIds:
        return []

    # Step 2: Fetch Candidate Document Data from Database
    with sqlite3.connect(SQL_DATABASE_FILENAME) as conn:
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(pageIds))
        sql = f"SELECT PageId, Title, Snippet, URL FROM articles WHERE PageId IN ({placeholders})"
        cursor.execute(sql, pageIds)
        results = cursor.fetchall()

    # Step 3: Re-arrange the fetched documents in order of the BM25 ranked PageIds. Because SQLite returns data in random order
    results_dict = {}
    docs = []

    for page_data in results:
        results_dict[page_data[0]] = page_data  # -> {"PageId" : Page Data}

    for pageId in pageIds:
        if pageId in results_dict:
            # Append the page data in order of the BM25 ranked pageIds
            docs.append(results_dict.get(pageId))

    if not docs:
        return []

    # Step 4: Second Stage Re-Ranking: Match the semantic similarity of the title with query.
    doc_texts = []
    for page_data in docs:
        # page_data[1] is Title and page_data[2] is snippet.
        doc_texts.append(f"{page_data[1]}. {page_data[2]}")

    query_vector = EMBEDDING_MODEL.encode([query])
    doc_vectors = EMBEDDING_MODEL.encode(doc_texts)

    semantic_scores = cosine_similarity(query_vector, doc_vectors)[0]

    # Step 5: Rerank by semantic similarity
    reranked = sorted(
        zip(docs, semantic_scores),
        # -> Rank by semantic score which will be at index 1
        key=lambda doc: doc[1],
        reverse=True  # High score to Low score
    )

    return [doc for doc, score in reranked]
