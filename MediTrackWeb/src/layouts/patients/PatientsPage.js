import React, { useState } from "react";
import { FaFileAlt, FaEdit, FaPlus } from "react-icons/fa";
import "./PatientsPage.css";
import MedicalRecord from "../medical-record-popup/MedicalRecord";

const initialPatients = [
  {
    name: "Ho Minh Nhat",
    age: 20,
    status: "Stable",
    record: {
      birthDate: "2004-01-15",
      gender: "Male",
      address: "123 Ly Thuong Kiet, Ha Noi",
      phone: "0123-456-789",
      maritalStatus: "Single",
      email: "nhat.ho@example.com",
      employment: "Student",
      insurance: {
        provider: "Bao Viet",
        plan: "Standard",
        id: "BV001",
      },
      emergencyContact: {
        name: "Ho Minh Tam",
        phone: "0987-654-321",
        relation: "Father",
      },
      medicalHistory: [
        {
          condition: "Myopia",
          medication: "None",
          allergy: "None",
          startDate: "2012-09-01",
        },
      ],
    },
  },
  {
    name: "Pham Nam An",
    age: 20,
    status: "Stable",
    record: {
      birthDate: "2004-03-22",
      gender: "Male",
      address: "456 Quang Trung, HCM",
      phone: "0934-555-222",
      maritalStatus: "Single",
      email: "nam.an@example.com",
      employment: "Intern",
      insurance: {
        provider: "PVI",
        plan: "Gold",
        id: "PVI1001",
      },
      emergencyContact: {
        name: "Pham Thi Hoa",
        phone: "0968-223-123",
        relation: "Mother",
      },
      medicalHistory: [
        {
          condition: "Asthma",
          medication: "Albuterol",
          allergy: "Dust",
          startDate: "2016-05-10",
        },
      ],
    },
  },
  {
    name: "Pham Thanh Bao Ngan",
    age: 20,
    status: "Stable",
    record: {
      birthDate: "2004-08-10",
      gender: "Female",
      address: "12 Tran Hung Dao, Da Nang",
      phone: "0901-222-333",
      maritalStatus: "Single",
      email: "bao.ngan@example.com",
      employment: "Cashier",
      insurance: {
        provider: "PTI",
        plan: "Silver",
        id: "PTI2020",
      },
      emergencyContact: {
        name: "Pham Van Phuc",
        phone: "0988-100-100",
        relation: "Brother",
      },
      medicalHistory: [
        {
          condition: "Anemia",
          medication: "Iron supplements",
          allergy: "None",
          startDate: "2022-01-15",
        },
      ],
    },
  },
  {
    name: "Phan Thi Anh Hong",
    age: 20,
    status: "Stable",
    record: {
      birthDate: "2004-12-05",
      gender: "Female",
      address: "789 CMT8, Can Tho",
      phone: "0943-321-876",
      maritalStatus: "Single",
      email: "anh.hong@example.com",
      employment: "Freelancer",
      insurance: {
        provider: "VBI",
        plan: "Bronze",
        id: "VBI7890",
      },
      emergencyContact: {
        name: "Phan Van Huy",
        phone: "0976-887-111",
        relation: "Uncle",
      },
      medicalHistory: [
        {
          condition: "Migraines",
          medication: "Ibuprofen",
          allergy: "None",
          startDate: "2020-03-03",
        },
      ],
    },
  },
  {
    name: "Le Pham Tien Long",
    age: 20,
    status: "Stable",
    record: {
      birthDate: "2004-07-18",
      gender: "Male",
      address: "101 Pham Van Đong, Hai Phong",
      phone: "0911-888-999",
      maritalStatus: "Single",
      email: "tien.long@example.com",
      employment: "Developer",
      insurance: {
        provider: "Bao Minh",
        plan: "Premium",
        id: "BM1000",
      },
      emergencyContact: {
        name: "Le Van Tien",
        phone: "0983-776-544",
        relation: "Father",
      },
      medicalHistory: [
        {
          condition: "Allergic Rhinitis",
          medication: "Cetirizine",
          allergy: "Pollen",
          startDate: "2021-04-01",
        },
      ],
    },
  },
  {
    name: "Nguyen Trung Nhan",
    age: 20,
    status: "Recovering",
    record: {
      birthDate: "2004-06-30",
      gender: "Male",
      address: "159 Vo Van Tan, HCM",
      phone: "0922-456-789",
      maritalStatus: "Single",
      email: "trung.nhan@example.com",
      employment: "Student",
      insurance: {
        provider: "VinaHealth",
        plan: "Standard",
        id: "VH3002",
      },
      emergencyContact: {
        name: "Nguyen Thi Hong",
        phone: "0900-123-987",
        relation: "Mother",
      },
      medicalHistory: [
        {
          condition: "Appendicitis",
          medication: "Post-op antibiotics",
          allergy: "None",
          startDate: "2023-11-01",
        },
      ],
    },
  },
  {
    name: "Ngo Hai Giang",
    age: 29,
    status: "Stable",
    record: {
      birthDate: "1995-02-28",
      gender: "Female",
      address: "204 Nguyen Van Cu, Ha Long",
      phone: "0977-444-666",
      maritalStatus: "Married",
      email: "hai.giang@example.com",
      employment: "Teacher",
      insurance: {
        provider: "AIA",
        plan: "Gold+",
        id: "AIA8899",
      },
      emergencyContact: {
        name: "Tran Hai Anh",
        phone: "0912-334-556",
        relation: "Husband",
      },
      medicalHistory: [
        {
          condition: "Back pain",
          medication: "Pain relievers",
          allergy: "None",
          startDate: "2021-09-10",
        },
      ],
    },
  },
  {
    name: "Vu Ngọc Ha",
    age: 50,
    status: "Critical",
    record: {
      birthDate: "1974-05-04",
      gender: "Female",
      address: "88 Truong Chinh, HN",
      phone: "0905-443-332",
      maritalStatus: "Widowed",
      email: "ngoc.ha@example.com",
      employment: "Retired",
      insurance: {
        provider: "EVN Health",
        plan: "Senior",
        id: "EVN54321",
      },
      emergencyContact: {
        name: "Nguyen Đuc Hoa",
        phone: "0938-777-888",
        relation: "Son",
      },
      medicalHistory: [
        {
          condition: "Heart Disease",
          medication: "Beta-blockers",
          allergy: "Seafood",
          startDate: "2019-07-12",
        },
        {
          condition: "Arthritis",
          medication: "NSAIDs",
          allergy: "None",
          startDate: "2020-02-20",
        },
      ],
    },
  },
  {
    name: "Bui Thị Iu",
    age: 47,
    status: "Stable",
    record: {
      birthDate: "1977-08-16",
      gender: "Female",
      address: "132 Quoc lo 1A, Bien Hoa",
      phone: "0987-654-321",
      maritalStatus: "Married",
      email: "thi.iu@example.com",
      employment: "Clerk",
      insurance: {
        provider: "Prudential",
        plan: "Essential",
        id: "PR456789",
      },
      emergencyContact: {
        name: "Bui Van An",
        phone: "0900-121-212",
        relation: "Husband",
      },
      medicalHistory: [
        {
          condition: "Thyroid issue",
          medication: "Levothyroxine",
          allergy: "None",
          startDate: "2018-10-05",
        },
      ],
    },
  },
  {
    name: "Lam Quang Kha",
    age: 35,
    status: "Recovering",
    record: {
      birthDate: "1989-12-12",
      gender: "Male",
      address: "10/5 Le Duan, Buon Ma Thuot",
      phone: "0969-888-123",
      maritalStatus: "Married",
      email: "quang.kha@example.com",
      employment: "Engineer",
      insurance: {
        provider: "Manulife",
        plan: "Family Plus",
        id: "ML987654",
      },
      emergencyContact: {
        name: "Lam Thi Hong",
        phone: "0932-222-444",
        relation: "Wife",
      },
      medicalHistory: [
        {
          condition: "Fractured arm",
          medication: "Pain relievers",
          allergy: "None",
          startDate: "2024-01-30",
        },
      ],
    },
  },
];

export default function PatientsPage() {
  const [patients, setPatients] = useState(initialPatients);
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPatient, setNewPatient] = useState({
    name: "",
    age: "",
    status: "Stable",
  });
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [editPatient, setEditPatient] = useState(null);

  const filteredPatients = patients.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddPatient = () => {
    if (!newPatient.name || !newPatient.age) return;
    setPatients([
      ...patients,
      { ...newPatient, age: parseInt(newPatient.age), record: {} },
    ]);
    setNewPatient({ name: "", age: "", status: "Stable" });
    setShowAddForm(false);
  };

  return (
    <div className="patients-container">
      <div className="patients-header">
        {/* Header  */}
        <h2>Patients</h2>
        <button
          className="add-patient-btn"
          onClick={() => setShowAddForm(true)}
        >
          <FaPlus /> Add Patient
        </button>
      </div>
      <input
        type="text"
        placeholder="Search patient..."
        className="search-input"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {/* Patient List */}
      <div className="patients-list">
        {filteredPatients.map((p, idx) => (
          <div className="patient-card" key={idx}>
            <div
              className={`patient-avatar ${p.status.toLowerCase()}`}
              onClick={() => setSelectedPatient(p)}
            >
              {p.name.charAt(0).toUpperCase()}
            </div>
            <div className="patient-info">
              <strong>{p.name}</strong>
              <div>Age: {p.age}</div>
              <span className={`status ${p.status.toLowerCase()}`}>
                {p.status}
              </span>
            </div>
            <div className="card-buttons">
              <button onClick={() => setSelectedPatient(p)}>
                <FaFileAlt /> View Record
              </button>
              <button
                onClick={() =>
                  setEditPatient({
                    ...p,
                    original: p,
                  })
                }
              >
                <FaEdit /> Edit
              </button>
            </div>
          </div>
        ))}
      </div>
      {/* Add Patient Form */}
      {showAddForm && (
        <div className="modal-overlay" onClick={() => setShowAddForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add New Patient</h3>
            <input
              type="text"
              placeholder="Name"
              value={newPatient.name}
              onChange={(e) =>
                setNewPatient({ ...newPatient, name: e.target.value })
              }
            />
            <input
              type="number"
              placeholder="Age"
              value={newPatient.age}
              onChange={(e) =>
                setNewPatient({ ...newPatient, age: e.target.value })
              }
            />
            <select
              value={newPatient.status}
              onChange={(e) =>
                setNewPatient({ ...newPatient, status: e.target.value })
              }
            >
              <option value="Stable">Stable</option>
              <option value="Critical">Critical</option>
              <option value="Recovering">Recovering</option>
            </select>
            <div className="form-buttons">
              <button className="add-btn" onClick={handleAddPatient}>
                Add
              </button>
              <button
                className="cancel-btn"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Pop up for viewing medical record */}
      {selectedPatient && (
        <div className="modal-overlay">
          <MedicalRecord
            patient={{
              name: selectedPatient.name,
              age: selectedPatient.age,
              status: selectedPatient.status,
              ...selectedPatient.record,
            }}
            onClose={() => setSelectedPatient(null)}
          />
        </div>
      )}

      {editPatient && (
        <div className="modal-overlay" onClick={() => setEditPatient(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Patient</h3>
            <input
              type="text"
              value={editPatient.name}
              onChange={(e) =>
                setEditPatient({ ...editPatient, name: e.target.value })
              }
            />
            <input
              type="number"
              value={editPatient.age}
              onChange={(e) =>
                setEditPatient({ ...editPatient, age: e.target.value })
              }
            />
            <select
              value={editPatient.status}
              onChange={(e) =>
                setEditPatient({ ...editPatient, status: e.target.value })
              }
            >
              <option value="Stable">Stable</option>
              <option value="Critical">Critical</option>
              <option value="Recovering">Recovering</option>
            </select>

            <div className="form-buttons center">
              <button
                className="add-btn"
                onClick={() => {
                  setPatients(
                    patients.map((p) =>
                      p === editPatient.original
                        ? { ...editPatient, age: parseInt(editPatient.age) }
                        : p
                    )
                  );
                  setEditPatient(null);
                }}
              >
                Save
              </button>
              <button
                className="cancel-btn"
                onClick={() => setEditPatient(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
