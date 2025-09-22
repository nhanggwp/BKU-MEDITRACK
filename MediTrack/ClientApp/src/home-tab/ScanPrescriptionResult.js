import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  Modal,
  TouchableOpacity,
  Image,
  TextInput,
} from "react-native";
import { CircleButton } from "../components/Button";

const { width } = Dimensions.get("window");

const ScanPrescriptionResult = ({
  visible,
  onConfirm,
  onClose,
  medications = [],
}) => {
  const [editableMeds, setEditableMeds] = useState([]);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    if (visible) {
      setEditMode(false);
      setEditableMeds(
        medications.map((m) => ({
          name: m.name || "",
          dosage: m.dosage || "",
          frequency: m.frequency || "",
        }))
      );
    }
  }, [visible, medications]);

  const addEmptyMedicine = () => {
    setEditableMeds((prev) => [
      ...prev,
      { name: "", dosage: "", frequency: "" },
    ]);
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
    >
      <View style={styles.container}>
        {/* Top bar */}
        <View style={styles.topBar}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.closeText}>←</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Confirm Medications</Text>
          <CircleButton />
        </View>

        {/* Checkmark */}
        <Image
          source={require("./assets/checkmark.png")}
          style={styles.checkmark}
        />

        {/* Detected meds box */}
        <View style={styles.detectedBox}>
          <Text style={styles.detectedTitle}>We detected:</Text>
          {editableMeds.map((med, index) => {
            const name = med.name || "Unknown";
            const dosage = med.dosage ? ` • ${med.dosage}` : "";
            const frequency = med.frequency ? ` • ${med.frequency}` : "";
            return (
              <View key={index} style={styles.medRow}>
                <Image
                  source={require("./assets/pill-icon.png")}
                  style={styles.pillIcon}
                />
                {editMode ? (
                  <View style={{ flex: 1 }}>
                    <TextInput
                      style={styles.input}
                      value={med.name}
                      onChangeText={(text) => {
                        const updated = [...editableMeds];
                        updated[index].name = text;
                        setEditableMeds(updated);
                      }}
                      placeholder="Medicine name"
                    />
                    <TextInput
                      style={styles.input}
                      value={med.dosage}
                      onChangeText={(text) => {
                        const updated = [...editableMeds];
                        updated[index].dosage = text;
                        setEditableMeds(updated);
                      }}
                      placeholder="Dosage"
                    />
                    <TextInput
                      style={styles.input}
                      value={med.frequency}
                      onChangeText={(text) => {
                        const updated = [...editableMeds];
                        updated[index].frequency = text;
                        setEditableMeds(updated);
                      }}
                      placeholder="Frequency"
                    />
                  </View>
                ) : (
                  <Text style={styles.medText}>
                    {name}
                    {dosage}
                    {frequency}
                  </Text>
                )}

                {editMode && (
                  <TouchableOpacity
                    onPress={() => {
                      const updated = [...editableMeds];
                      updated.splice(index, 1);
                      setEditableMeds(updated);
                    }}
                  >
                    <Text style={styles.deleteIcon}>➖</Text>
                  </TouchableOpacity>
                )}
              </View>
            );
          })}
        </View>

        {/* ➕ Add Medicine */}
        {editMode && (
          <TouchableOpacity onPress={addEmptyMedicine} style={styles.addButton}>
            <Text style={styles.addButtonText}>➕ Add Medicine</Text>
          </TouchableOpacity>
        )}

        {/* Action buttons */}
        <View style={styles.actionRow}>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => setEditMode((prev) => !prev)}
          >
            <Text style={styles.secondaryText}>
              {editMode ? "Done" : "Edit"}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.secondaryButton}>
            <Text style={styles.secondaryText}>Other Action</Text>
          </TouchableOpacity>
        </View>

        {/* Confirm button */}
        <TouchableOpacity
          style={styles.confirmButton}
          onPress={() => onConfirm(editableMeds.map((m) => m.name))}
        >
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
  input: {
    borderBottomWidth: 1,
    borderColor: "#ccc",
    paddingVertical: 4,
    marginBottom: 6,
    fontSize: 14,
  },
  deleteIcon: {
    fontSize: 20,
    color: "#d9534f",
    marginLeft: 8,
  },
  addButton: {
    marginTop: 12,
    alignSelf: "center",
    paddingVertical: 6,
    paddingHorizontal: 16,
    borderRadius: 10,
    backgroundColor: "#e9efff",
  },
  addButtonText: {
    color: "#3763f4",
    fontWeight: "600",
    fontSize: 14,
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

export default ScanPrescriptionResult;
