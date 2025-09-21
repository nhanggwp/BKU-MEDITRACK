import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Modal,
  TouchableOpacity,
  Image,
} from "react-native";
import { CircleButton } from "../components/Button";
const { width, height } = Dimensions.get("window");

const ScanResult = ({ visible, onClose }) => {
  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
    >
      <View style={styles.container}>
        {/* Top bar with close icon */}
        <View style={styles.topBar}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.closeText}>←</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Confirm Medications</Text>
          <CircleButton></CircleButton>
        </View>

        {/* Checkmark */}
        <Image
          source={require("./assets/checkmark.png")}
          style={styles.checkmark}
        />

        {/* Detected meds box */}
        <View style={styles.detectedBox}>
          <Text style={styles.detectedTitle}>We detected:</Text>
          {["Metophim", "Lisinopril", "Aspirin"].map((med, index) => (
            <View key={index} style={styles.medRow}>
              <Image
                source={require("./assets/pill-icon.png")}
                style={styles.pillIcon}
              />
              <Text style={styles.medText}>{med}</Text>
            </View>
          ))}
        </View>

        {/* Action buttons */}
        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.secondaryButton}>
            <Text style={styles.secondaryText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryButton}>
            <Text style={styles.secondaryText}>Add Manually</Text>
          </TouchableOpacity>
        </View>

        {/* Confirm button */}
        <TouchableOpacity style={styles.confirmButton}>
          <Text style={styles.confirmText}>CONFIRM</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
  },

  topBar: {
    width: "100%",
    paddingTop: 60,
    paddingHorizontal: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  closeText: {
    fontSize: 24,
    color: "#3763f4",
  },
  title: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#000",
  },
  avatar: {
    position: "absolute",
    top: 60,
    right: 20,
  },

  checkmark: {
    width: 120,
    height: 120,
    marginTop: 20,
    resizeMode: "contain",
  },

  detectedBox: {
    marginTop: 30,
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    width: width * 0.8,
    borderWidth: 1.5,
    borderColor: "#6e9dfc",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 3,
  },

  detectedTitle: {
    fontWeight: "bold",
    color: "#3763f4",
    marginBottom: 12,
    fontSize: 16,
  },

  medRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },

  pillIcon: {
    width: 18,
    height: 18,
    marginRight: 10,
    resizeMode: "contain",
  },

  medText: {
    fontWeight: "bold",
    fontSize: 15,
  },

  actionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: width * 0.8,
    marginTop: 20,
  },

  secondaryButton: {
    flex: 1,
    paddingVertical: 10,
    marginHorizontal: 5,
    backgroundColor: "#f9f9f9",
    borderRadius: 12,
    alignItems: "center",
    elevation: 2,
  },

  secondaryText: {
    color: "#3763f4",
    fontWeight: "600",
  },

  confirmButton: {
    marginTop: 25,
    backgroundColor: "#3763f4",
    paddingVertical: 15,
    paddingHorizontal: 80,
    borderRadius: 14,
    shadowOpacity: 0.3,
    elevation: 3,
  },

  confirmText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
});

export default ScanResult;
