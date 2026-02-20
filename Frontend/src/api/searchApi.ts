import axios from "axios";

export interface SearchResultType {
  page_id: string;
  title: string;
  snippet: string;
  url: string;
}

export interface ComparisonSearchResponse {
  query: string;
  bm25_count: number;
  tfidf_count: number;
  bm25_results: SearchResultType[];
  tfidf_results: SearchResultType[];
}

const BASE_URL =
  import.meta.env.REACT_APP_API_URL || "http://localhost:8000";

export const compareSearchWikipedia = async (
  query: string
): Promise<ComparisonSearchResponse> => {
  const res = await axios.get(`${BASE_URL}/compare/search`, {
    params: { query },
  });

  return res.data;
};
