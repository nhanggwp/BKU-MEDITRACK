import React, { useState } from "react";
import "./PrescriptionResult.css";

const dummyResults = [
  {
    id: 1,
    title: "Warfarin + Ibuprofen: High-Risk Interaction",
    timestamp: "2025-07-20 09:32 AM ",
    interactions: [
      {
        severity: "Major",
        drugs: "warfarin (anticoagulant) ↔ ibuprofen (NSAID)",
        description:
          "Concurrent use of warfarin and ibuprofen significantly increases the risk of gastrointestinal bleeding and impaired blood clotting. NSAIDs inhibit platelet function and irritate the gastric lining, compounding the anticoagulant effect of warfarin.",
        details:
          "Warfarin, a vitamin K antagonist, reduces clotting by decreasing the synthesis of clotting factors. Ibuprofen, a commonly used NSAID, can compromise platelet aggregation and damage the gastrointestinal mucosa. When used together, there's a heightened risk of internal bleeding, including life-threatening GI bleeds. If co-administration is unavoidable, patients should be closely monitored for any signs of unusual bruising, blood in urine or stool, or drop in hematocrit.",
      },
      {
        severity: "Moderate",
        drugs: "warfarin (anticoagulant) ↔ amoxicillin (antibiotic)",
        description:
          "Amoxicillin may disturb intestinal microbiota responsible for vitamin K synthesis, thereby enhancing the anticoagulant effect of warfarin and increasing bleeding tendencies.",
        details:
          "The human gut flora plays a role in producing vitamin K, which is essential for blood clotting. Amoxicillin can suppress or eliminate vitamin K-producing bacteria, especially with prolonged use, thereby enhancing warfarin's anticoagulant effect. This interaction is typically delayed and may manifest after several days of co-use. INR (International Normalized Ratio) levels may rise unexpectedly, and clinical symptoms such as easy bruising or nosebleeds can occur. Close INR monitoring is recommended during and shortly after antibiotic treatment.",
      },
      {
        severity: "Major",
        drugs: "warfarin ↔ aspirin",
        description:
          "Both warfarin and aspirin affect blood clotting, and their combination can dramatically increase the risk of serious bleeding.",
        details:
          "Aspirin inhibits platelet aggregation, while warfarin decreases production of clotting factors. When used together, this dual anticoagulant effect significantly raises the risk of internal bleeding, including cerebral and gastrointestinal hemorrhages. This combination should only be used under strict medical supervision with routine INR testing and bleeding assessments.",
      },
      {
        severity: "Moderate",
        drugs: "warfarin ↔ acetaminophen",
        description:
          "Prolonged or high-dose use of acetaminophen may enhance warfarin’s anticoagulant effects, possibly through hepatic metabolism interference.",
        details:
          "Though generally considered safer than NSAIDs, acetaminophen in large doses or over extended periods may increase INR in patients taking warfarin. The mechanism is not fully understood but may involve liver enzyme interaction or reduction in vitamin K-dependent factors. Patients using more than 2 grams daily for several days should be monitored closely for INR changes.",
      },
      {
        severity: "Minor",
        drugs: "warfarin ↔ multivitamins (with vitamin K)",
        description:
          "Multivitamins containing vitamin K may reduce the effectiveness of warfarin, potentially lowering INR.",
        details:
          "Vitamin K directly counteracts warfarin’s mechanism of action. Supplements containing vitamin K can cause warfarin’s anticoagulant effects to drop, potentially increasing the risk of clot formation. Patients should maintain consistent vitamin K intake and notify providers before starting supplements.",
      },
    ],
  },

  {
    id: 2,
    title: "Metformin + Alcohol",
    timestamp: "2025-07-18 03:45 PM",
    interactions: [
      {
        severity: "Major",
        drugs: "metformin ↔ alcohol",
        description:
          "Acute alcohol intake may potentiate the effect of metformin on lactate metabolism, leading to lactic acidosis.",
        details:
          "Avoid alcohol when using metformin. Lactic acidosis is rare but serious.",
      },
      {
        severity: "Minor",
        drugs: "metformin ↔ aspirin",
        description:
          "High-dose aspirin may slightly decrease renal clearance of metformin.",
        details: "Usually not clinically significant at low aspirin doses.",
      },
    ],
  },
  {
    id: 3,
    title: "Simvastatin + Grapefruit Juice",
    timestamp: "2025-07-17 02:15 PM",
    interactions: [
      {
        severity: "Major",
        drugs: "simvastatin ↔ grapefruit juice",
        description:
          "Grapefruit juice can increase the concentration of simvastatin in the blood, raising the risk of muscle toxicity.",
        details:
          "Inhibits CYP3A4 enzymes in the intestine, leading to significantly higher drug levels. Myopathy and rhabdomyolysis are potential risks.",
      },
    ],
  },
  {
    id: 4,
    title: "Lisinopril + Potassium Supplement",
    timestamp: "2025-07-16 10:05 AM",
    interactions: [
      {
        severity: "Moderate",
        drugs: "lisinopril ↔ potassium",
        description:
          "ACE inhibitors like lisinopril can increase potassium levels. Supplementing potassium may cause hyperkalemia.",
        details:
          "Monitor serum potassium regularly. Symptoms of hyperkalemia include weakness, confusion, and irregular heartbeat.",
      },
    ],
  },
  {
    id: 5,
    title: "Levothyroxine + Calcium Carbonate",
    timestamp: "2025-07-15 08:50 AM",
    interactions: [
      {
        severity: "Minor",
        drugs: "levothyroxine ↔ calcium carbonate",
        description:
          "Calcium can interfere with absorption of levothyroxine if taken simultaneously.",
        details:
          "Space doses at least 4 hours apart. This reduces the risk of decreased thyroid hormone efficacy.",
      },
    ],
  },
];

const Result = () => {
  const [selectedResult, setSelectedResult] = useState(null);
  const [expandedIndexes, setExpandedIndexes] = useState([]);
  const [search, setSearch] = useState("");

  const filteredResults = dummyResults.filter((result) =>
    result.title.toLowerCase().includes(search.toLowerCase())
  );

  const toggleDetail = (index) => {
    setExpandedIndexes((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  return (
    <div className="result-page">
      <div className={`recent-results ${selectedResult ? "blur" : ""}`}>
        {/* Header  */}
        <h2>Recent Results</h2>
        {/* Search Bar  */}
        <input
          className="search-bar"
          type="text"
          placeholder="Search medicine..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {/* Results List  */}
        <ul className="result-list">
          {filteredResults.length > 0 ? (
            filteredResults.map((result) => (
              <li
                key={result.id}
                className="result-item"
                onClick={() => {
                  setSelectedResult(result);
                  setExpandedIndexes([]);
                }}
              >
                <div className="title">{result.title}</div>
                <div className="timestamp">{result.timestamp}</div>
              </li>
            ))
          ) : (
            <li className="no-results">No results found.</li>
          )}
        </ul>
      </div>

      {/* Popup for selected result */}
      {selectedResult && (
        <div className="popup-overlay">
          <div className="popup">
            {/* Close Button  */}
            <button
              className="close-btn"
              onClick={() => setSelectedResult(null)}
            >
              ✕
            </button>
            <div className="popup-content">
              {selectedResult.interactions.map((interaction, idx) => (
                <div className="interaction" key={idx}>
                  <span
                    className={`severity ${interaction.severity.toLowerCase()}`}
                  >
                    {interaction.severity}
                  </span>
                  <h3>{interaction.drugs}</h3>
                  <p>{interaction.description}</p>
                  {/* View Detail Button  */}
                  <button
                    className="view-detail"
                    onClick={() => toggleDetail(idx)}
                  >
                    {expandedIndexes.includes(idx)
                      ? "Hide details"
                      : "View details"}
                  </button>
                  {expandedIndexes.includes(idx) && (
                    <div className="extra-detail">{interaction.details}</div>
                  )}
                  {idx !== selectedResult.interactions.length - 1 && <hr />}
                </div>
              ))}
              <button className="save-btn">SAVE</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Result;
