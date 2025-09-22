import React, { useState } from "react";
import "./MedicalRecord.css";

function MedicalRecord() {
  const patients = [
    {
      patient_id: 1,
      name: "John Doe",
      gender: "Male",
      birthDate: "1989-05-12",
      address: "123 Main St, Springfield",
      phone: "(123) 456-7890",
      maritalStatus: "Married",
      email: "john.doe@example.com",
      employment: "Software Engineer",
      insurance: {
        provider: "HealthFirst",
        plan: "Gold PPO",
        id: "HF1234567",
      },
      emergencyContact: {
        name: "Jane Doe",
        phone: "(123) 555-7890",
        relation: "Wife",
      },
      medicalHistory: [
        {
          condition: "Hypertension",
          medication: "Lisinopril",
          allergy: "None",
          startDate: "2020-02-10",
        },
        {
          condition: "Asthma",
          medication: "Albuterol",
          allergy: "Penicillin",
          startDate: "2018-11-20",
        },
      ],
    },
    // You can add more patients here
  ];

  const [inputId, setInputId] = useState("");

  const patient = patients[0]; //

  return (
    <div className="record-container">
      <h1>Medical Record</h1>

      {/* Existing patient rendering */}
      <section className="section">
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

      <section className="section">
        <h2>Health Coverage</h2>
        <p>
          <strong>Provider:</strong> {patient.insurance.provider}
        </p>
        <p>
          <strong>Plan:</strong> {patient.insurance.plan}
        </p>
        <p>
          <strong>Insurance ID:</strong> {patient.insurance.id}
        </p>
      </section>

      <section className="section">
        <h2>Emergency Contact</h2>
        <p>
          <strong>Name:</strong> {patient.emergencyContact.name}
        </p>
        <p>
          <strong>Phone:</strong> {patient.emergencyContact.phone}
        </p>
        <p>
          <strong>Relation:</strong> {patient.emergencyContact.relation}
        </p>
      </section>

      <section className="section">
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
            {patient.medicalHistory.map((entry, index) => (
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

      {/* <section className="section">
        <h2>Doctor & Signature</h2>
        <p>
          <strong>Doctor:</strong> {patient.doctor}
        </p>
        <p>
          <strong>Signature:</strong> {patient.signature}
        </p>
      </section> */}
    </div>
  );
}

export default MedicalRecord;
