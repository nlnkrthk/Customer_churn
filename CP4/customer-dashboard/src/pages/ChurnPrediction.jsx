// TASK 166: Create Churn Prediction page

import { useState } from "react";
import axios from "axios";
import { BASE_URL, API_KEY } from "../api";
import "./ChurnPrediction.css";

function ChurnPrediction() {

  // TASK 167: Create controlled form state
  const [formData, setFormData] = useState({
    tenure: "",
    monthly_charges: "",
    contract_type: "Month-to-month",
    service_count: ""
  });

  // TASK 171: Create loading state for prediction request
  const [loading, setLoading] = useState(false);

  // TASK 172: Create error state for validation and API errors
  const [error, setError] = useState("");

  // TASK 169: Store prediction result
  const [result, setResult] = useState(null);

  // TASK 167: Handle changes to controlled form inputs
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value
    });
  };

  // TASK 168: Submit form and call prediction API
  const handleSubmit = async (event) => {
    event.preventDefault();

    // TASK 172: Clear previous error
    setError("");

    // TASK 169: Clear previous prediction result
    setResult(null);

    // TASK 171: Start loading state
    setLoading(true);

    try {

      // TASK 168: Send prediction request to FastAPI
      const response = await axios.post(
        `${BASE_URL}/predict-churn`,
        {
          tenure: Number(formData.tenure),
          monthly_charges: Number(formData.monthly_charges),
          contract_type: formData.contract_type,
          service_count: Number(formData.service_count)
        },
        {
          headers: {
            "X-API-Key": API_KEY
          }
        }
      );

      // TASK 169: Store prediction response
      setResult(response.data);

      console.log(response.data);

    } catch (error) {

      // TASK 172: Handle Pydantic validation errors
      if (error.response?.status === 422) {

        const detail = error.response.data.detail;

        if (Array.isArray(detail)) {
          setError(detail.map((item) => item.msg).join(", "));
        } else {
          setError(String(detail));
        }

      } else {

        // TASK 172: Handle other API errors
        setError("Failed to get churn prediction.");

      }

    } finally {

      // TASK 171: Stop loading after request completes
      setLoading(false);

    }
  };

  // TASK 170: Determine risk indicator
  const getRiskLevel = (riskScore) => {

    if (riskScore < 0.3) {
      return "LOW";
    }

    if (riskScore <= 0.6) {
      return "MEDIUM";
    }

    return "HIGH";
  };

  // TASK 169: Calculate risk score percentage
  const riskPercentage = result
    ? (result.risk_score * 100).toFixed(1)
    : null;

  const riskLevel = result
    ? getRiskLevel(result.risk_score)
    : null;

  return (
    <main className="prediction-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <header className="prediction-header">

        <div>
          <p className="prediction-eyebrow">
            04 / PREDICTIVE INTELLIGENCE
          </p>

          <h1>
            Churn
            <em>Prediction</em>
          </h1>
        </div>

        <div className="prediction-header-meta">
          <span>CUSTOMER RETENTION</span>
          <span>RISK ANALYSIS</span>
        </div>

      </header>


      {/* =====================================================
          INTRO
          ===================================================== */}


      <div className="prediction-rule"></div>


      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <section className="prediction-workspace">

        {/* ===================================================
            FORM
            =================================================== */}

        <div className="prediction-form-section">

          <div className="section-label">
            CUSTOMER PROFILE
          </div>

          <h2>
            Customer
            <br />
            details
          </h2>

          <form
            className="prediction-form"
            onSubmit={handleSubmit}
          >

            {/* Tenure */}

            <div className="form-field">

              <label htmlFor="tenure">
                <span>01</span>
                TENURE
              </label>

              <input
                id="tenure"
                type="number"
                name="tenure"
                min="0"
                value={formData.tenure}
                onChange={handleChange}
                placeholder="Months"
                required
              />

            </div>


            {/* Monthly Charges */}

            <div className="form-field">

              <label htmlFor="monthly_charges">
                <span>02</span>
                MONTHLY CHARGES
              </label>

              <input
                id="monthly_charges"
                type="number"
                name="monthly_charges"
                step="0.01"
                min="0"
                value={formData.monthly_charges}
                onChange={handleChange}
                placeholder="Amount"
                required
              />

            </div>


            {/* Contract */}

            <div className="form-field">

              <label htmlFor="contract_type">
                <span>03</span>
                CONTRACT TYPE
              </label>

              <select
                id="contract_type"
                name="contract_type"
                value={formData.contract_type}
                onChange={handleChange}
              >

                <option value="Month-to-month">
                  Month-to-month
                </option>

                <option value="One year">
                  One year
                </option>

                <option value="Two year">
                  Two year
                </option>

              </select>

            </div>


            {/* Service Count */}

            <div className="form-field">

              <label htmlFor="service_count">
                <span>04</span>
                SERVICE COUNT
              </label>

              <input
                id="service_count"
                type="number"
                name="service_count"
                min="0"
                max="6"
                value={formData.service_count}
                onChange={handleChange}
                placeholder="0 — 6"
                required
              />

            </div>


            {/* Error */}

            {error && (
              <div
                className="prediction-error"
                role="alert"
              >
                <span>ERROR</span>
                {error}
              </div>
            )}


            {/* Submit */}

            <button
              type="submit"
              className="prediction-submit"
              disabled={loading}
            >
              <span>
                {loading
                  ? "ANALYSING..."
                  : "PREDICT CHURN"}
              </span>

              <span className="submit-arrow">
                →
              </span>

            </button>

          </form>

        </div>


        {/* ===================================================
            RESULT
            =================================================== */}

        <div className="prediction-result-section">

          {!result && !loading && (

            <div className="result-empty">

              <div className="result-empty-number">
                00
              </div>

              <div>
                <p className="section-label">
                  ANALYSIS STATUS
                </p>

                <h2>
                  Awaiting
                  <br />
                  <em>customer data.</em>
                </h2>

                <p className="result-empty-text">
                  Submit the customer profile to generate
                  a churn-risk assessment.
                </p>
              </div>

            </div>

          )}


          {/* Loading */}

          {loading && (

            <div className="result-loading">

              <div className="loading-number">
                ...
              </div>

              <p className="section-label">
                ANALYSING CUSTOMER
              </p>

              <h2>
                Calculating
                <br />
                <em>risk.</em>
              </h2>

            </div>

          )}


          {/* Result */}

          {result && !loading && (

            <div className="result-content">

              <div className="result-heading">

                <p className="section-label">
                  PREDICTION RESULT
                </p>

                <span className="result-status">
                  ANALYSIS COMPLETE
                </span>

              </div>


              {/* Risk Score */}

              <div className="risk-score-block">

                <span className="risk-score-label">
                  RISK SCORE
                </span>

                <div className="risk-score">
                  {riskPercentage}
                  <span>%</span>
                </div>

                <div className="risk-bar">

                  <div
                    className="risk-bar-fill"
                    style={{
                      width: `${riskPercentage}%`
                    }}
                  ></div>

                </div>

                <div className="risk-scale">
                  <span>LOW</span>
                  <span>MEDIUM</span>
                  <span>HIGH</span>
                </div>

              </div>


              {/* Risk Classification */}

              <div className="risk-classification">

                <span className="classification-label">
                  RISK CLASSIFICATION
                </span>

                <strong>
                  {riskLevel}
                </strong>

              </div>


              {/* Details */}

              <div className="result-details">

                <div className="result-detail">

                  <span>
                    PREDICTION
                  </span>

                  <strong>
                    {result.prediction}
                  </strong>

                </div>


                <div className="result-detail">

                  <span>
                    CONFIDENCE
                  </span>

                  <strong>
                    {result.confidence || "Not provided"}
                  </strong>

                </div>

              </div>

            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="prediction-footer">

        <span>
          CUSTOMER RETENTION INTELLIGENCE SYSTEM
        </span>

        <span>
          CHURN PREDICTION / 04
        </span>

      </footer>

    </main>
  );
}

export default ChurnPrediction;