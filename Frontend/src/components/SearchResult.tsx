import React from "react";
import { motion } from "framer-motion";
import type { SearchResultType } from "../api/searchApi";

interface Props {
  result: SearchResultType;
}

const SearchResult: React.FC<Props> = ({ result }) => {
  return (
    <motion.div
      className="search-result"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <a href={result.url} target="_blank" rel="noopener noreferrer">
        <h3>{result.title}</h3>
        <p>{result.snippet}</p>
      </a>
    </motion.div>
  );
};

export default SearchResult;
