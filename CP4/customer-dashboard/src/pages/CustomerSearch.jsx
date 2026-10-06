// TASK 146: Display customer profile card

import { useState } from "react";
import axios from "axios";
import { BASE_URL, API_KEY } from "../api";
import "./CustomerSearch.css";

function CustomerSearch() {

  // TASK 142: Create controlled customer ID input
  const [customerId, setCustomerId] = useState("");

  // TASK 144: Store customer API response
  const [customer, setCustomer] = useState(null);

  // TASK 145: Track API loading state
  const [loading, setLoading] = useState(false);

  // TASK 147: Create error state
  const [error, setError] = useState("");


  // =========================================================
  // TASK 144: Search for customer
  // TASK 147: Handle customer search errors
  // =========================================================

  const searchCustomer = () => {

    setLoading(true);

    // TASK 147: Clear previous search results
    setCustomer(null);
    setError("");

    axios
      .get(`${BASE_URL}/customer/${customerId}`, {
        headers: {
          "X-API-Key": API_KEY
        }
      })
      .then((response) => {

        // TASK 144: Store customer API response
        setCustomer(response.data);

      })
      .catch((error) => {

        // TASK 147: Handle 404 customer not found
        if (error.response?.status === 404) {
          setError("Customer not found");
        } else {
          setError("Something went wrong. Please try again.");
        }

        console.error(error);

      })
      .finally(() => {

        // TASK 145: Stop loading state
        setLoading(false);

      });

  };


  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {

    return (
      <div className="customer-page customer-loading-page">

        <div className="customer-loading">

          <span>
            01 / CUSTOMER INTELLIGENCE
          </span>

          <h1>
            Customer <em>Search</em>
          </h1>

          <p>
            Retrieving customer profile...
          </p>

        </div>

      </div>
    );

  }


  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="customer-page">


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="customer-header">

        <div>

          <p className="customer-eyebrow">
            01 / CUSTOMER INTELLIGENCE
          </p>

          <h1>
            Customer <em>Search</em>
          </h1>

        </div>


        <div className="customer-header-meta">

          <span>CUSTOMER RETENTION</span>

          <span>PROFILE ANALYSIS</span>

        </div>

      </header>



      {/* =====================================================
          MAIN WORKSPACE
          ===================================================== */}

      <main className="customer-workspace">


        {/* ===================================================
            LEFT — SEARCH
            =================================================== */}

        <section className="customer-search-section">

          <div className="customer-section-label">

            <span>01</span>

            <span>CUSTOMER LOOKUP</span>

          </div>


          <h2>
            Find a
            <br />
            customer.
          </h2>


          <div className="customer-search-form">

            <label htmlFor="customer-id">

              CUSTOMER ID

            </label>


            <input
              id="customer-id"
              type="text"
              placeholder="Enter customer ID"
              value={customerId}
              onChange={(event) =>
                setCustomerId(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  searchCustomer();
                }
              }}
            />


            <button
              onClick={searchCustomer}
              disabled={!customerId.trim()}
            >

              <span>
                SEARCH CUSTOMER
              </span>

              <span className="search-arrow">
                →
              </span>

            </button>

          </div>


          {/* Error */}

          {error && (

            <div className="customer-error">

              <span>
                SEARCH ERROR
              </span>

              <p>
                {error}
              </p>

            </div>

          )}


          {/* Empty state */}

          {!customer && !error && (

            <div className="customer-search-note">

              <span>
                00
              </span>

              <p>
                Enter a customer identifier to
                retrieve their retention profile.
              </p>

            </div>

          )}

        </section>



        {/* ===================================================
            RIGHT — PROFILE
            =================================================== */}

        <section className="customer-profile-section">


          {!customer ? (

            /* =================================================
               EMPTY PROFILE
               ================================================= */

            <div className="customer-profile-empty">

              <div className="profile-empty-number">
                00
              </div>


              <div>

                <span>
                  PROFILE STATUS
                </span>

                <h2>
                  Awaiting
                  <br />
                  <em>customer data.</em>
                </h2>

                <p>
                  Search for a customer to view
                  their retention profile.
                </p>

              </div>

            </div>

          ) : (

            /* =================================================
               CUSTOMER PROFILE
               ================================================= */

            <div className="customer-profile">


              {/* Profile header */}

              <div className="profile-header">

                <div>

                  <span className="profile-label">
                    CUSTOMER PROFILE
                  </span>

                  <h2>
                    {customer.customer_id}
                  </h2>

                </div>


                <span className="profile-status">
                  PROFILE FOUND
                </span>

              </div>



              {/* Customer details */}

              <div className="customer-details">


                {/* Tenure */}

                <div className="customer-detail">

                  <span>
                    01 / TENURE
                  </span>

                  <strong>
                    {customer.tenure}
                  </strong>

                  <small>
                    MONTHS
                  </small>

                </div>


                {/* Contract */}

                <div className="customer-detail">

                  <span>
                    02 / CONTRACT
                  </span>

                  <strong>
                    {customer.contract_type}
                  </strong>

                </div>


                {/* Internet Service */}

                <div className="customer-detail">

                  <span>
                    03 / INTERNET SERVICE
                  </span>

                  <strong>
                    {customer.internet_service}
                  </strong>

                </div>


                {/* Monthly Charges */}

                <div className="customer-detail">

                  <span>
                    04 / MONTHLY CHARGES
                  </span>

                  <strong>
                    ${customer.monthly_charges}
                  </strong>

                </div>

              </div>



              {/* Churn status */}

              <div className="customer-churn-status">

                <div>

                  <span>
                    RETENTION STATUS
                  </span>

                  <h3>
                    {customer.churn === 1
                      ? "Churned"
                      : "Active"}
                  </h3>

                </div>


                <div
                  className={
                    customer.churn === 1
                      ? "status-indicator churned"
                      : "status-indicator active"
                  }
                >

                  {customer.churn === 1
                    ? "CHURNED"
                    : "ACTIVE"}

                </div>

              </div>

            </div>

          )}

        </section>

      </main>



      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="customer-footer">

        <span>
          CUSTOMER RETENTION INTELLIGENCE SYSTEM
        </span>

        <span>
          CUSTOMER SEARCH / 01
        </span>

      </footer>

    </div>
  );
}

export default CustomerSearch;