import React, { useState } from "react";
import "./PrescriptionScanner.css";
import MedicalRecord from "../medical-record-popup/MedicalRecord";

// const patientData = {
//   name: "Ho Minh Nhat",
//   age: 20,
//   status: "Stable",
//   record: {
//     birthDate: "2004-01-15",
//     gender: "Male",
//     address: "123 Ly Thuong Kiet, Ha Noi",
//     phone: "0123-456-789",
//     maritalStatus: "Single",
//     email: "nhat.ho@example.com",
//     employment: "Student",
//     insurance: {
//       provider: "Bao Viet",
//       plan: "Standard",
//       id: "BV001",
//     },
//     emergencyContact: {
//       name: "Ho Minh Tam",
//       phone: "0987-654-321",
//       relation: "Father",
//     },
//     medicalHistory: [
//       {
//         condition: "Myopia",
//         medication: "None",
//         allergy: "None",
//         startDate: "2012-09-01",
//       },
//     ],
//   },
// };

// // Encode to Base64
// const json = JSON.stringify(patientData);
// const base64 = btoa(json);
// console.log(base64);

const PrescriptionScanner = () => {
  const [manualMode, setManualMode] = useState(false);
  const [manualText, setManualText] = useState("");
  const [decodedPatient, setDecodedPatient] = useState(null);
  const toggleMode = () => {
    setManualMode(!manualMode);
    setManualText("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // prevent newline on Enter without Shift
      try {
        // Decode Base64 string and parse the JSON
        const jsonString = atob(manualText); // decode base64 to string
        const parsed = JSON.parse(jsonString); // parse to object
        setDecodedPatient(parsed); // Show popup
        setManualText(""); // Clear input after decoding
      } catch (err) {
        console.error("Failed to decode or parse input:", err);
      }
    }
  };

  return (
    <div className="scanner-page">
      <h2>Scanner</h2>

      <div className="scanner-card">
        <div className="manual-input">
          <label htmlFor="prescription">Code Input:</label>
          <textarea
            id="prescription"
            rows="6"
            value={manualText}
            onChange={(e) => setManualText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Click here and scan..."
          />
        </div>
      </div>

      {decodedPatient && (
        <MedicalRecord
          patient={{
            name: decodedPatient.name,
            age: decodedPatient.age,
            status: decodedPatient.status,
            ...decodedPatient.record,
          }}
          onClose={() => setDecodedPatient(null)}
        />
      )}
    </div>
  );
};

export default PrescriptionScanner;
