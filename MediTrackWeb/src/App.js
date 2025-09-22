import logo from "./logo.svg";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./layouts/login/Login";
import PrescriptionChecker from "./layouts/prescription/PreScriptionChecker";
import PrescriptionLayout from "./layouts/prescription/PrescriptionLayout";
import SideBarLayout from "./layouts/sidebar/SideBarLayout";
import PrescriptionScanner from "./layouts/prescription-scan/PrescriptionScanner";
import Result from "./layouts/prescription-result/PrescriptionResult";
import PatientsPage from "./layouts/patients/PatientsPage";
import HomePage from "./layouts/home/HomePage";
import NotificationsPage from "./layouts/notifications/NotificationsPage";
import SettingsPage from "./layouts/settings/SettingsPage";
import ChatbotPage from "./layouts/chatbot/ChatbotPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
const patientData = {
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
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={
            <ProtectedRoute>
              <SideBarLayout />
            </ProtectedRoute>
          }>
            {/* SideBar nested */}
            <Route index element={<HomePage />} />
            <Route path="patients" element={<PatientsPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="chatbot" element={<ChatbotPage />} />
            {/* <Route path="medical-record" element={<MedicalRecord />} /> */}
            <Route path="prescription" element={<PrescriptionLayout />}>
              {/* Prescription nested  */}
              <Route index element={<PrescriptionChecker />} />
              <Route
                path="prescription-check"
                element={<PrescriptionChecker />}
              />
              <Route path="prescription-scan" element={<PrescriptionScanner />} />
              <Route path="result" element={<Result />} />
            </Route>{" "}
            {/* Add more subpages later */}
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
