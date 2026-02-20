import React from "react";
import SearchBar from "../components/SearchBar";

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page-container">
      <img src="/Wikipedia-logo.svg" alt="" />
      <h1>Wikipedia Search</h1>
      <SearchBar />
    </div>
  );
};

export default LandingPage;
