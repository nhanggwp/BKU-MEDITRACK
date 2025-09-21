import React, { useState } from "react";
import { View, Text, StyleSheet, Dimensions, Image } from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import { ImageButton, CircleButton } from "../components/Button";
import Checkbox from "../components/CheckBox";
import { BASE_URL } from "../../config";

// Modals / subviews
import CameraScreen from "./CameraScreen";
import ScanPrescriptionResult from "./ScanPrescriptionResult";
import ScanQRResult from "./ScanQrResult";
import ConfirmPrescriptionResult from "./ConfirmPrescriptionResult";
import WaitingScreen from "./WaitingScreen";
import AddManually from "./AddManually";
import { useRoute } from "@react-navigation/native";
const { width, height } = Dimensions.get("window");

// 💊 Component that renders a single medicine reminder card
const _reminderCard = ({ icon, name, time, takenTime, onCheck, isTaken }) => {
  return (
    <View style={styles.card}>
      {/* Top section: icon + name + time + checkbox */}
      <View style={styles.topRow}>
        <CircleButton
          imageSource={icon}
          style={styles.reminderIconButton}
          imageStyle={styles.reminderIcon}
        />
        <View style={styles.textGroup}>
          <Text style={styles.timeText}>{time}</Text>
          <Text style={styles.nameText}>{name}</Text>
        </View>
        <Checkbox
          onToggle={onCheck}
          boxStyle={styles.checkBox}
          checked={isTaken}
        />
      </View>

      {/* If medicine is marked as taken, show additional info */}
      {isTaken && (
        <View style={styles.takenMissGroup}>
          <Text style={styles.statusText}>
            <Text style={styles.greenText}>Taken at {takenTime}</Text>
          </Text>
          <Text style={styles.missedText}>Missed reminder?</Text>
        </View>
      )}
    </View>
  );
};

// hàm chuẩn hóa, loại bỏ tên thuốc trùng
const normalizeNames = (arr) => [
  ...new Map(
    (Array.isArray(arr) ? arr : [])
      .map((x) => (typeof x === "string" ? x : x?.name || ""))
      .map((s) => (s || "").trim())
      .filter(Boolean)
      .map((v) => [v.toLowerCase(), v]) // unique by lowercase, keep original casing
  ).values(),
];

// 🏠 Main Home screen component
const Home = () => {
  const navigation = useNavigation();

  //Token
  const route = useRoute();
  const { token } = route.params || {};

  // 🧠 Local state for reminder list
  const [reminders, setReminders] = useState([
    {
      id: 1,
      name: "Cảm cúm",
      time: "8:00 AM",
      takenTime: "8:03 AM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },
    {
      id: 2,
      name: "Viêm mũi dị ứng",
      time: "5:00 PM",
      takenTime: "5:30 PM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },
    {
      id: 3,
      name: "Rối loạn tiêu hóa",
      time: "8:00 PM",
      takenTime: "8:00 PM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },
  ]);

  // 📸 State for camera, modals, results
  const [cameraVisible, setCameraVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  //Prescription
  const [showPrescriptionResult, setShowPrescriptionResult] = useState(false); //data is dummy for now
  const [showConfirmResult, setShowConfirmResult] = useState(false); //

  //QR Code
  const [qrData, setQrData] = useState(null);
  const [showQRResult, setShowQRResult] = useState(false);
  const [medications, setMedications] = useState([]); // Stores OCR analysis result

  // Add Manually
  const [showAddModal, setShowAddModal] = useState(false);

  //
  const _handleAddManually = async (manualMeds) => {
    try {
      setLoading(true);

      // 1) Chuẩn hoá danh sách nhập tay
      const manualList = normalizeNames(manualMeds);
      console.log("📝 AddManually normalized:", manualList);

      // 2) Lấy danh sách thuốc tiền sử từ server
      const historyList = await fetchSavedMedicationNames();
      console.log("📚 History list from server:", historyList);

      // 3) Gộp + loại trùng
      const merged = normalizeNames([...manualList, ...historyList]);
      console.log("🔗 Merged Manual + History (deduped):", merged);

      // 4) Mở modal Confirm để check interaction với list đã gộp
      setMedications(merged);
      setShowConfirmResult(true);
    } catch (e) {
      console.error("❌ AddManually merge error:", e);
      // fallback: chỉ dùng danh sách nhập tay
      setMedications(normalizeNames(manualMeds));
      setShowConfirmResult(true);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Toggle taken checkbox
  const _handleTaken = (id) => {
    setReminders((prev) =>
      prev.map((reminder) =>
        reminder.id === id ? { ...reminder, taken: !reminder.taken } : reminder
      )
    );
  };

  // 📤 Handle photo result from CameraScreen (prescription mode)
  const _handleScanPrescription = async (photo) => {
    setCameraVisible(false);
    setShowQRResult(false);
    setLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/api/ocr/recognize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: photo.base64 }),
      });

      const data = await response.json();

      setMedications(data.analysis?.medications || []);
      setShowPrescriptionResult(true);
    } catch (err) {
      console.error("❌ OCR failed", err);
    } finally {
      setLoading(false);
    }
  };

  // ✅ After confirming result
  const _handleComfirmResult = async (updatedMeds) => {
    try {
      setShowPrescriptionResult(false);
      setLoading(true);

      const ocrList = normalizeNames(updatedMeds);
      console.log("🔎 Normalized OCR list:", ocrList);

      // 2) Lấy danh sách thuốc tiền sử từ server
      const historyList = await fetchSavedMedicationNames();
      console.log("📚 History list from server:", historyList);
      const merged = normalizeNames([...ocrList, ...historyList]);
      console.log("Merged OCR + History (deduped):", merged);
      setMedications(merged);
      setShowConfirmResult(true);
    } catch (e) {
      console.error("❌ merge confirm meds error:", e);
      setMedications(normalizeNames(updatedMeds));
      setShowConfirmResult(true);
    } finally {
      setLoading(false);
    }
  };

  // 📥 Handle QR scan result from CameraScreen
  const _handleScanQR = (QrData) => {
    console.log("📦 QR Data received in Home:", QrData);
    setCameraVisible(false);
    setShowPrescriptionResult(false);
    setQrData(QrData);
    setShowQRResult(true);
  };

  const fetchSavedMedicationNames = async () => {
    try {
      if (!token) return [];
      const res = await fetch(`${BASE_URL}/api/prescriptions/list`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      // API có thể trả {"items": ["Paracetamol", ...]} hoặc [{"medication_name": "Paracetamol"}, ...]
      console.log("📥 Response from /prescriptions/list:", data);

      const items = Array.isArray(data?.items) ? data.items : [];
      const names = items.map((it) =>
        typeof it === "string" ? it : it?.medication_name || ""
      );
      console.log("📋 Extracted names from history:", names);
      return normalizeNames(names);
    } catch (e) {
      console.error("❌ fetchSavedMedicationNames error:", e);
      return [];
    }
  };

  return (
    <View style={styles.container}>
      {/* Avatar (top right corner) */}
      <View style={styles.avatar}>
        <CircleButton onPress={() => navigation.navigate("Profile")} />
      </View>

      {/* Main title */}
      <Text style={styles.header}>Home</Text>

      {/* Main action buttons: scan & add */}
      <View style={styles.action}>
        <ImageButton
          text={"Scan\nPrescription"}
          textStyle={styles.actionName}
          style={styles.button}
          imageSource={require("./assets/scan-icon.png")}
          imageStyle={styles.image}
          onPress={() => setCameraVisible(true)}
        />
        <ImageButton
          text={"Add\nManually"}
          textStyle={styles.actionName}
          style={styles.button}
          imageSource={require("./assets/add-icon.png")}
          imageStyle={styles.image}
          onPress={() => setShowAddModal(true)}
        />
      </View>

      {/* Reminders list */}
      <View style={styles.reminderSection}>
        <Text style={[globalStyles.headingTwo, styles.greenText]}>
          Reminders
        </Text>
        {reminders.map((reminder) => (
          <_reminderCard
            key={reminder.id}
            icon={reminder.icon}
            name={reminder.name}
            time={reminder.time}
            takenTime={reminder.takenTime}
            onCheck={() => _handleTaken(reminder.id)}
            isTaken={reminder.taken}
          />
        ))}
      </View>

      {/* CameraScreen Modal */}
      <CameraScreen
        visible={cameraVisible}
        onClose={() => setCameraVisible(false)}
        onCapture={_handleScanPrescription}
        onScanComplete={_handleScanQR}
      />

      {/* Waiting Screen Modal*/}
      <WaitingScreen visible={loading} />

      {/* Prescription Result Modal */}
      <ScanPrescriptionResult
        visible={showPrescriptionResult}
        onConfirm={_handleComfirmResult}
        onClose={() => setShowPrescriptionResult(false)}
        medications={medications}
      />

      {/* Confirm Prescription Result Modal */}
      <ConfirmPrescriptionResult
        visible={showConfirmResult}
        onClose={() => setShowConfirmResult(false)}
        medications={medications}
        token={token}
      />

      {/* Add Manually Modal */}
      <AddManually
        visible={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={_handleAddManually}
      />
    </View>
  );
};

// 🎨 UI Styles
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },

  avatar: {
    position: "absolute",
    top: 60,
    right: 20,
  },

  header: {
    ...globalStyles.headingTwo,
    alignSelf: "center",
    marginTop: 0.1 * height,
  },

  action: {
    alignSelf: "center",
    marginTop: 0.05 * height,
    flexDirection: "row",
    gap: width * 0.2,
  },

  actionName: {
    ...globalStyles.headingThree,
    color: "#fff",
    fontSize: 18,
    textAlign: "center",
  },

  image: {
    width: width * 0.25,
    height: height * 0.1,
    marginBottom: -width * 0.03,
    resizeMode: "contain",
  },

  button: {
    width: 0.33 * width,
    resizeMode: "contain",
    paddingVertical: 0,
    paddingHorizontal: 0,
  },

  reminderSection: {
    marginTop: height * 0.05,
    marginLeft: width * 0.07,
  },

  greenText: {
    color: "#007F00",
    fontWeight: "700",
  },

  reminderIconButton: {
    width: 0.12 * width,
    height: 0.05 * height,
    marginRight: 8,
  },

  reminderIcon: {
    width: 0.1 * width,
    height: 0.05 * height,
    resizeMode: "contain",
  },

  card: {
    paddingVertical: 16,
    marginBottom: 6,
  },

  topRow: {
    flexDirection: "row",
    marginBottom: 8,
  },

  textGroup: {
    width: 0.4 * width,
    marginRight: 15,
  },

  takenMissGroup: {
    marginLeft: 0.12 * width + 8,
  },

  checkBox: {
    width: 40,
    height: 40,
  },

  timeText: {
    fontSize: 20,
    fontWeight: "bold",
  },

  nameText: {
    ...globalStyles.textBased,
    fontSize: 16,
  },

  statusText: {
    fontSize: 16,
    marginBottom: 4,
  },

  missedText: {
    color: "#3763f4",
    fontWeight: "600",
    fontSize: 16,
  },
});

export default Home;
