import React from "react";
import { useParams } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import SearchResult from "../components/SearchResult";
import { useQuery } from "@tanstack/react-query";
import { searchWikipedia } from "../api/searchApi";
import { AnimatePresence } from "framer-motion";

const ResultsPage: React.FC = () => {
  const { query } = useParams<{ query: string }>();
  const decodedQuery = query ? decodeURIComponent(query) : "";

  const { data: results = [], isLoading } = useQuery({
    queryKey: ["search", decodedQuery],
    queryFn: () => searchWikipedia(decodedQuery),
    enabled: !!decodedQuery,
  });

  return (
    <div className="search-results-container">
      <SearchBar initialQuery={decodedQuery} />
      {isLoading && <p style={{ textAlign: "center" }}>Searching...</p>}
      <AnimatePresence>
        {results.map((res) => (
          <SearchResult key={res.page_id} result={res} />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ResultsPage;
