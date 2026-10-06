// TASK 151: Fetch churn summary when the page loads

import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL, API_KEY } from "../api";
import "./ChurnSummary.css";

function ChurnSummary() {

  // TASK 151: Store churn summary API response
  const [data, setData] = useState(null);

  // TASK 156: Create loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // TASK 151: Fetch churn summary when component mounts

  useEffect(() => {

    axios
      .get(`${BASE_URL}/churn/summary`, {
        headers: {
          "X-API-Key": API_KEY
        }
      })
      .then((response) => {

        // TASK 151: Store API response in state
        setData(response.data);

        // TASK 156: Stop loading after successful API response
        setLoading(false);

        console.log(response.data);
      })
      .catch((error) => {

        // TASK 151: Log API error
        console.error(error);

        // TASK 156: Handle API error
        setError("Failed to load churn summary.");
        setLoading(false);
      });

  }, []);


  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {
    return (
      <div className="summary-page summary-loading-page">

        <div className="summary-loading">
          <span>02 / RETENTION OVERVIEW</span>

          <h1>
            Churn
            <em>Summary</em>
          </h1>

          <p>Loading retention intelligence...</p>
        </div>

      </div>
    );
  }


  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="summary-page">


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="summary-header">

        <div>

          <p className="summary-eyebrow">
            02 / RETENTION OVERVIEW
          </p>

          <h1>
            Churn <em>Summary</em>
          </h1>

        </div>


        <div className="summary-header-meta">

          <span>CUSTOMER RETENTION</span>
          <span>RETENTION ANALYSIS</span>

        </div>

      </header>


      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <main className="summary-workspace">


        {/* ===================================================
            LEFT SIDE — KEY METRICS
            =================================================== */}

        <section className="summary-metrics-section">

          <div className="summary-section-label">
            <span>01</span>
            <span>RETENTION METRICS</span>
          </div>


          <h2>
            Customer
            <br />
            overview.
          </h2>


          {/* Error */}

          {error && (
            <div className="summary-error">

              <span>ERROR</span>

              <p>{error}</p>

            </div>
          )}


          {/* Metrics */}

          {data && (

            <div className="summary-metrics">


              {/* Total Customers */}

              <div className="summary-metric">

                <div className="metric-number">
                  01
                </div>

                <div className="metric-content">

                  <span className="metric-label">
                    TOTAL CUSTOMERS
                  </span>

                  <strong>
                    {data.total_customers}
                  </strong>

                </div>

              </div>


              {/* Total Churned */}

              <div className="summary-metric">

                <div className="metric-number">
                  02
                </div>

                <div className="metric-content">

                  <span className="metric-label">
                    TOTAL CHURNED
                  </span>

                  <strong>
                    {data.churned}
                  </strong>

                </div>

              </div>


              {/* Churn Rate */}

              <div className="summary-metric">

                <div className="metric-number">
                  03
                </div>

                <div className="metric-content">

                  <span className="metric-label">
                    OVERALL CHURN RATE
                  </span>

                  <strong>
                    {data.churn_rate}
                  </strong>

                </div>

              </div>

            </div>

          )}

        </section>



        {/* ===================================================
            RIGHT SIDE — CONTRACT ANALYSIS
            =================================================== */}

        <section className="summary-contract-section">


          <div className="contract-header">

            <div>

              <span className="summary-section-label">
                CONTRACT ANALYSIS
              </span>

              <h2>
                Churn rate
                <br />
                by contract.
              </h2>

            </div>


            <span className="analysis-status">
              {data ? "ANALYSIS COMPLETE" : "ANALYSIS ERROR"}
            </span>

          </div>


          {/* Contract table */}

          {data && (

            <div className="contract-analysis">

              {/* Table heading */}

              <div className="contract-table-heading">

                <span>CONTRACT TYPE</span>

                <span>CHURN RATE</span>

              </div>


              {/* Contract rows */}

              {data.by_contract.map((contract, index) => (

                <div
                  className="contract-row"
                  key={contract.contract_type}
                >

                  <div className="contract-name">

                    <span className="contract-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    <strong>
                      {contract.contract_type}
                    </strong>

                  </div>


                  <div className="contract-rate">

                    <div className="contract-rate-value">

                      {(contract.churn_rate * 100).toFixed(1)}%

                    </div>


                    <div className="contract-bar">

                      <div
                        className="contract-bar-fill"
                        style={{
                          width: `${contract.churn_rate * 100}%`
                        }}
                      />

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

        </section>

      </main>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="summary-footer">

        <span>
          CUSTOMER RETENTION INTELLIGENCE SYSTEM
        </span>

        <span>
          CHURN SUMMARY / 02
        </span>

      </footer>

    </div>
  );
}

export default ChurnSummary;