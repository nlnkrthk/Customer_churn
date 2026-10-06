import { useState } from "react";

import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";
import LandingPage from "./pages/LandingPage";

import "./App.css";

function App() {

  // Current page
  const [page, setPage] = useState("landing");


  // Decide which page to display
  const renderPage = () => {

    switch (page) {

      case "customer-search":
        return <CustomerSearch />;

      case "churn-summary":
        return <ChurnSummary />;

      case "high-risk":
        return <HighRiskCustomers />;

      case "churn-prediction":
        return <ChurnPrediction />;

      default:
        return <LandingPage setPage={setPage} />;
    }
  };


  return (

    <div className="app">

      {/* =================================================
          NAVIGATION BAR
          ================================================= */}

      {page !== "landing" && (

        <nav className="main-navbar">

          {/* Logo / Home */}

          <button
            className="nav-logo"
            onClick={() => setPage("landing")}
          >
            RETAIN
          </button>


          {/* Navigation links */}

          <div className="nav-links">

            <button
              className={
                page === "customer-search"
                  ? "nav-link active"
                  : "nav-link"
              }
              onClick={() => setPage("customer-search")}
            >
              Customer Search
            </button>


            <button
              className={
                page === "churn-summary"
                  ? "nav-link active"
                  : "nav-link"
              }
              onClick={() => setPage("churn-summary")}
            >
              Churn Summary
            </button>


            <button
              className={
                page === "high-risk"
                  ? "nav-link active"
                  : "nav-link"
              }
              onClick={() => setPage("high-risk")}
            >
              High-Risk Customers
            </button>


            <button
              className={
                page === "churn-prediction"
                  ? "nav-link active"
                  : "nav-link"
              }
              onClick={() => setPage("churn-prediction")}
            >
              Churn Prediction
            </button>

          </div>


          {/* Back to home */}

          <button
            className="nav-home"
            onClick={() => setPage("landing")}
          >
            HOME
          </button>

        </nav>

      )}


      {/* =================================================
          CURRENT PAGE
          ================================================= */}

      <div className="page-content">

        {renderPage()}

      </div>

    </div>

  );
}

export default App;