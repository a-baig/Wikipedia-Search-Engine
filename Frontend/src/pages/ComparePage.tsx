import { Link, Navigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { compareSearchWikipedia } from "../api/searchApi";
import type { SearchResultType } from "../api/searchApi";
import SearchBar from "../components/SearchBar";

// --- SKELETON COMPONENTS ---
const SkeletonCard = () => (
  <div className="result-card skeleton">
    <div className="skeleton-header">
      <div className="skeleton-icon" />
      <div className="skeleton-text-group">
        <div className="skeleton-line short" />
        <div className="skeleton-line medium" />
      </div>
    </div>
    <div className="skeleton-line" style={{ width: "80%" }} />
    <div className="skeleton-line" />
    <div className="skeleton-line" />
  </div>
);

const SkeletonColumn = ({ title }: { title: string }) => (
  <div className="results-column">
    <div className="column-header-box">
      <p style={{ fontWeight: "bold" }}>{title}</p>
      <div className="skeleton-line-micro" />
    </div>
    {[1, 2, 3].map((i) => (
      <SkeletonCard key={i} />
    ))}
  </div>
);

// --- ACTUAL COMPONENTS ---
const ResultCard = ({ item }: { item: SearchResultType }) => {
  return (
    <motion.div
      className="result-card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="card-header">
        <img src="/Wikipedia-logo.svg" alt="" width={32} />
        <div>
          <h4>Wikipedia</h4>
          <a href={item.url} target="_blank" rel="noreferrer">
            {item.url}
          </a>
        </div>
      </div>
      <h3>
        <a href={item.url} target="_blank" rel="noreferrer">
          {item.title}
        </a>
      </h3>
      <p>{item.snippet}</p>
    </motion.div>
  );
};

const ResultsColumn = ({
  title,
  count,
  results,
}: {
  title: string;
  count: number;
  results: SearchResultType[];
}) => {
  return (
    <div className="results-column">
      <div className="column-header-box">
        <p style={{ fontWeight: "bold" }}>{title}</p>
        <p style={{ fontSize: "0.8rem", opacity: 0.6 }}>{count} results</p>
      </div>
      {results.length > 0 ? (
        results.map((r) => <ResultCard key={r.page_id} item={r} />)
      ) : (
        <p className="no-results">No matches found.</p>
      )}
    </div>
  );
};

// --- MAIN PAGE ---
export default function ComparePage() {
  const [params] = useSearchParams();
  const query = params.get("q") || "";

  const { data, isLoading } = useQuery({
    queryKey: ["compare", query],
    queryFn: () => compareSearchWikipedia(query),
    enabled: !!query,
    staleTime: 3 * 60 * 1000,
  });

  if (query === "") {
    return <Navigate to={"/"} />;
  }

  // Prevent flash of empty screen before loading starts
  if (!data && !isLoading) return null;

  return (
    <div className="compare-container">
      <div className="compare-container-header">
        <Link to={"/"}>
          <img src="/Wikipedia-logo.svg" alt="Wikipedia" />
        </Link>
        <div className="search-wrapper">
          <SearchBar initialQuery={query} />
        </div>
      </div>

      <div className="columns-wrapper">
        {isLoading ? (
          <>
            <SkeletonColumn title="BM25" />
            <SkeletonColumn title="TF-IDF" />
          </>
        ) : (
          <>
            <ResultsColumn
              title="BM25"
              count={data?.bm25_count || 0}
              results={data?.bm25_results || []}
            />
            <ResultsColumn
              title="TF-IDF"
              count={data?.tfidf_count || 0}
              results={data?.tfidf_results || []}
            />
          </>
        )}
      </div>
    </div>
  );
}
