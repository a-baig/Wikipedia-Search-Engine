from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn

from bm25 import search_with_bm25
from tfidf import search_with_tfidf

app = FastAPI(title="Wikipedia SimpleWiki Semantic Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- must be a list of origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def warmup():
    try:
        search_with_bm25("warmup")
        search_with_tfidf("warmup")
    except:
        pass


@app.get("/search")
async def search(query: str = Query(..., min_length=1)):
    try:
        results = await run_in_threadpool(search_with_bm25, query)
    except Exception as e:
        return {"error": str(e)}

    return {
        "query": query,
        "count": len(results),
        "results": [
            {
                "page_id": page_id,
                "title": title,
                "snippet": snippet,
                "url": url
            }
            for page_id, title, snippet, url in results
        ]
    }


@app.get("/compare/search")
async def compare_search(query: str = Query(..., min_length=1)):
    try:
        bm25_results = await run_in_threadpool(search_with_bm25, query)
        tfidf_results = await run_in_threadpool(search_with_tfidf, query)
    except Exception as e:
        return {"error": str(e)}

    return {
        "query": query,
        "bm25_count": len(bm25_results),
        "tfidf_count": len(tfidf_results),
        "bm25_results": [
            {
                "page_id": page_id,
                "title": title,
                "snippet": snippet,
                "url": url
            }
            for page_id, title, snippet, url in bm25_results
        ],
        "tfidf_results": [
            {
                "page_id": page_id,
                "title": title,
                "snippet": snippet,
                "url": url
            }
            for page_id, title, snippet, url in tfidf_results
        ]
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
