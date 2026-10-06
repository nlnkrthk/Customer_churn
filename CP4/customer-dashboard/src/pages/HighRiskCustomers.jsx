// TASK 159: Fetch high-risk customers on page load

import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL, API_KEY } from "../api";
import "./HighRiskCustomers.css";

function HighRiskCustomers() {

  // TASK 159: Store high-risk customer results
  const [customers, setCustomers] = useState([]);

  // Number of customers to request from API
  const [limit, setLimit] = useState(50);

  // Temporary input value
  const [limitInput, setLimitInput] = useState(50);

  // TASK 163: Create tenure sort toggle state
  const [sortAsc, setSortAsc] = useState(true);

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // =========================================================
  // FETCH HIGH-RISK CUSTOMERS
  // =========================================================

  useEffect(() => {

    setLoading(true);
    setError("");

    axios
      .get(`${BASE_URL}/customers/high-risk`, {
        params: {
          limit: limit
        },
        headers: {
          "X-API-Key": API_KEY
        }
      })
      .then((response) => {

        // TASK 159: Store API response
        setCustomers(response.data);

        console.log(response.data);

      })
      .catch((error) => {

        console.error(error);

        setError(
          error.response?.data?.detail ||
          "Failed to load high-risk customers."
        );

        setCustomers([]);

      })
      .finally(() => {

        setLoading(false);

      });

  }, [limit]);


  // =========================================================
  // HANDLE CUSTOMER COUNT
  // =========================================================

  const handleLimitChange = (event) => {

    setLimitInput(event.target.value);

  };


  const applyLimit = () => {

    const number = Number(limitInput);

    // Make sure the value is valid
    if (!number || number < 1) {

      setError("Please enter a number greater than 0.");

      return;

    }

    setError("");

    setLimit(number);

  };


  // Allow Enter key to apply the number
  const handleLimitKeyDown = (event) => {

    if (event.key === "Enter") {
      applyLimit();
    }

  };


  // =========================================================
  // SORT CUSTOMERS BY TENURE
  // =========================================================

  const sortedCustomers = [...customers].sort((a, b) => {

    if (sortAsc) {
      return a.tenure - b.tenure;
    }

    return b.tenure - a.tenure;

  });


  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading && customers.length === 0) {

    return (
      <div className="risk-page">

        <div className="risk-loading">

          <span>
            HIGH-RISK ANALYSIS
          </span>

          <h1>
            Loading
            <br />
            customer data.
          </h1>

        </div>

      </div>
    );

  }


  return (

    <div className="risk-page">


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="risk-header">

        <div className="risk-header-left">

          <span className="eyebrow">
            03 / RETENTION INTELLIGENCE
          </span>

          <h1>
            High-Risk
            <em>Customers</em>
          </h1>

        </div>


        <div className="risk-header-right">

          <span>
            CUSTOMER RETENTION
          </span>

          <span>
            RISK ANALYSIS
          </span>

        </div>

      </header>



      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <main className="risk-main">


        {/* ===================================================
            LEFT SECTION
            =================================================== */}

        <section className="risk-intro">

          <div className="section-number">
            03
          </div>

          <div>

            <span className="section-label">
              PRIORITY CUSTOMER LIST
            </span>

            <h2>
              Customers requiring
              <em>retention attention.</em>
            </h2>

            <p>
              Customers identified as high-risk based on
              the current retention rules and customer
              characteristics.
            </p>

          </div>

        </section>



        {/* ===================================================
            RIGHT SUMMARY
            =================================================== */}

        <section className="risk-summary">

          <span className="section-label">
            ANALYSIS STATUS
          </span>

          <div className="risk-count">
            {customers.length}
          </div>

          <span className="count-label">
            HIGH-RISK CUSTOMERS
          </span>

        </section>



        {/* ===================================================
            TABLE SECTION
            =================================================== */}

        <section className="risk-table-section">


          {/* =================================================
              TABLE HEADING
              ================================================= */}

          <div className="table-heading">

            <div>

              <span className="section-label">
                CUSTOMER DIRECTORY
              </span>

              <h3>
                Risk <em>Overview</em>
              </h3>

            </div>


            <div className="table-controls">

              <span>
                SORT BY TENURE
              </span>

              <button
                onClick={() => setSortAsc(!sortAsc)}
                className="sort-button"
              >

                {sortAsc
                  ? "LOW → HIGH"
                  : "HIGH → LOW"}

              </button>

            </div>

          </div>



          {/* =================================================
              CUSTOMER COUNT CONTROL
              ================================================= */}

          <div className="customer-limit">

            <div className="customer-limit-label">

              <span className="section-label">
                DISPLAY CUSTOMERS
              </span>

              <span className="customer-limit-help">
                Enter the number of customers to display
              </span>

            </div>


            <div className="customer-limit-control">

              <input
                type="number"
                min="1"
                value={limitInput}
                onChange={handleLimitChange}
                onKeyDown={handleLimitKeyDown}
              />


              <button
                onClick={applyLimit}
                disabled={loading}
              >

                {loading
                  ? "LOADING..."
                  : "APPLY"}

              </button>

            </div>

          </div>



          {/* =================================================
              ERROR
              ================================================= */}

          {error && (

            <div className="risk-error">
              {error}
            </div>

          )}



          {/* =================================================
              ZERO RESULTS
              ================================================= */}

          {customers.length === 0 && !loading && !error && (

            <div className="empty-state">

              <span className="section-label">
                ANALYSIS STATUS
              </span>

              <h3>
                No high-risk
                <em>customers found.</em>
              </h3>

            </div>

          )}



          {/* =================================================
              CUSTOMER TABLE
              ================================================= */}

          {customers.length > 0 && (

            <div className="risk-table-wrapper">

              <table className="risk-table">

                <thead>

                  <tr>

                    <th>
                      CUSTOMER ID
                    </th>


                    <th
                      className="sortable"
                      onClick={() => setSortAsc(!sortAsc)}
                    >

                      TENURE

                      <span>
                        {sortAsc ? " ↑" : " ↓"}
                      </span>

                    </th>


                    <th>
                      MONTHLY CHARGES
                    </th>


                    <th>
                      CONTRACT
                    </th>


                    <th>
                      RISK REASON
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {sortedCustomers.map((customer) => (

                    <tr key={customer.customer_id}>

                      <td className="customer-id">
                        {customer.customer_id}
                      </td>


                      <td>

                        {customer.tenure}

                        <span className="unit">
                          months
                        </span>

                      </td>


                      <td className="charges">

                        $
                        {Number(
                          customer.monthly_charges
                        ).toFixed(2)}

                      </td>


                      <td>
                        {customer.contract_type}
                      </td>


                      <td>

                        <span className="risk-reason">
                          {customer.risk_reason}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}



          {/* =================================================
              RESULT INFORMATION
              ================================================= */}

          {customers.length > 0 && (

            <div className="load-more-container">

              <span className="limit-info">
                DISPLAYING {customers.length} OF REQUESTED {limit}
              </span>

            </div>

          )}

        </section>

      </main>



      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="risk-footer">

        <span>
          CUSTOMER RETENTION INTELLIGENCE SYSTEM
        </span>

        <span>
          HIGH-RISK CUSTOMERS / 03
        </span>

      </footer>

    </div>

  );

}

export default HighRiskCustomers;