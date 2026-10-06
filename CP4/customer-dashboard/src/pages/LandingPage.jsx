import React from "react";
import "./LandingPage.css";

const modules = [
  {
    number: "01",
    title: "Customer Search",
    description:
      "Search individual customers and examine their retention information.",
    page: "customer-search",
  },
  {
    number: "02",
    title: "Churn Summary",
    description:
      "Understand overall churn patterns and identify important retention trends.",
    page: "churn-summary",
  },
  {
    number: "03",
    title: "High-Risk Customers",
    description:
      "Identify customers requiring immediate attention through risk-based analysis.",
    page: "high-risk",
  },
  {
    number: "04",
    title: "Churn Prediction",
    description:
      "Evaluate customer churn risk using the predictive intelligence system.",
    page: "churn-prediction",
  },
];

function LandingPage({ setPage }) {
  return (
    <main className="landing-page">

      {/* Header */}
      <header className="landing-header">
        <div className="landing-brand">
          CUSTOMER
          <span>RETENTION</span>
        </div>

        <div className="landing-header-meta">
          <span>TELECOM INTELLIGENCE</span>
          <span>2026</span>
        </div>
      </header>


      {/* Hero */}
      <section className="landing-hero">

        <div className="hero-label">
          <span className="hero-line"></span>
          CUSTOMER RETENTION INTELLIGENCE SYSTEM
        </div>

        <h1>
          Retain
          <br />
          <em>what matters.</em>
        </h1>

        <div className="hero-bottom">

          <p>
            A centralized intelligence platform for understanding customer
            behavior, identifying churn risk, and making informed retention
            decisions.
          </p>

          <div className="hero-mark">
            <span>01</span>
            <div></div>
            <span>04</span>
          </div>

        </div>

      </section>


      {/* Section Divider */}
      <div className="section-rule"></div>


      {/* Platform Modules */}
      <section className="modules-section">

        <div className="section-heading">
          <span>01 / PLATFORM</span>

          <h2>
            Explore the system
          </h2>
        </div>


        <div className="modules-grid">

          {modules.map((module) => (

            <button
              key={module.number}
              className="module-card"
              onClick={() => setPage(module.page)}
            >

              <div className="module-top">

                <span className="module-number">
                  {module.number}
                </span>

                <span className="module-arrow">
                  ↗
                </span>

              </div>


              <div className="module-content">

                <h3>
                  {module.title}
                </h3>

                <p>
                  {module.description}
                </p>

              </div>


              <div className="module-footer">
                OPEN MODULE
              </div>

            </button>

          ))}

        </div>

      </section>


      {/* Footer */}
      <footer className="landing-footer">

        <div>
          CUSTOMER RETENTION
        </div>

        <div>
          INTELLIGENCE SYSTEM
        </div>

        <div>
          © 2026
        </div>

      </footer>

    </main>
  );
}

export default LandingPage;