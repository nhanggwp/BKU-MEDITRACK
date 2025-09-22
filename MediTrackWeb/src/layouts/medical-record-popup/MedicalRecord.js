// MedicalRecord.js
import React from "react";
import "./MedicalRecord.css";

const MedicalRecord = ({ patient, onClose }) => {
  if (!patient) return null;

  return (
    <div className="mr-popup-overlay">
      <div className="mr-popup-content">
        <button className="mr-close-button" onClick={onClose}>
          X
        </button>
        {/* Header  */}
        <h1>Medical Record</h1>
        <section className="mr-section">
          {/* General Information  */}
          <h2>General Information</h2>
          <p>
            <strong>Name:</strong> {patient.name}
          </p>
          <p>
            <strong>Gender:</strong> {patient.gender}
          </p>
          <p>
            <strong>Date of Birth:</strong> {patient.birthDate}
          </p>
          <p>
            <strong>Address:</strong> {patient.address}
          </p>
          <p>
            <strong>Phone:</strong> {patient.phone}
          </p>
          <p>
            <strong>Marital Status:</strong> {patient.maritalStatus}
          </p>
          <p>
            <strong>Email:</strong> {patient.email}
          </p>
          <p>
            <strong>Employment:</strong> {patient.employment}
          </p>
        </section>
        {/* Health Coverage  */}
        <section className="mr-section">
          <h2>Health Coverage</h2>
          <p>
            <strong>Provider:</strong> {patient.insurance?.provider}
          </p>
          <p>
            <strong>Plan:</strong> {patient.insurance?.plan}
          </p>
          <p>
            <strong>Insurance ID:</strong> {patient.insurance?.id}
          </p>
        </section>
        {/* Emergency Contact  */}
        <section className="mr-section">
          <h2>Emergency Contact</h2>
          <p>
            <strong>Name:</strong> {patient.emergencyContact?.name}
          </p>
          <p>
            <strong>Phone:</strong> {patient.emergencyContact?.phone}
          </p>
          <p>
            <strong>Relation:</strong> {patient.emergencyContact?.relation}
          </p>
        </section>
        {/* Medical History  */}
        <section className="mr-section">
          <h2>Medical History</h2>
          <table>
            <thead>
              <tr>
                <th>Condition</th>
                <th>Medication</th>
                <th>Allergy</th>
                <th>Start Date</th>
              </tr>
            </thead>
            <tbody>
              {patient.medicalHistory?.map((entry, index) => (
                <tr key={index}>
                  <td>{entry.condition}</td>
                  <td>{entry.medication}</td>
                  <td>{entry.allergy}</td>
                  <td>{entry.startDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
};

export default MedicalRecord;
