import React from "react";
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";

const ScanQRResult = ({ visible, data, onClose }) => {
  if (!data) return null;

  // Mock fields if not present in scanned data
  const {
    userId,
    name = "NemEn",
    age = 20,
    sex = "Male",
    photo = "https://scontent.fsgn5-13.fna.fbcdn.net/v/t39.30808-6/439849626_122156624732078010_4711036864441551806_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=yFrxhUUjm2MQ7kNvwEzNRGp&_nc_oc=AdnklDb5UTv-CJZ782TArrd3zMkfk52ZY5oQZvHDRcPf2K7PTdlmEH2gd-smIRgXqsg&_nc_zt=23&_nc_ht=scontent.fsgn5-13.fna&_nc_gid=73F2-3qYIIJDeu5CZBV9tA&oh=00_AfOcLZ4ZSKJM2hm9SSw8TASJVhTRExmzeR8inniS3AbBHQ&oe=6869EE92",
    address = "123 Đường ABC, TP.HCM",
    phone = "0901 234 567",
    summary = [],
  } = data;

  return (
    <Modal visible={visible} animationType="slide" transparent={true}>
      <View style={styles.overlay}>
        <View style={styles.modalContent}>
          <TouchableOpacity style={styles.closeIcon} onPress={onClose}>
            <Ionicons name="close" size={28} color="#333" />
          </TouchableOpacity>

          <ScrollView>
            {/* Patient Info */}
            <View style={styles.patientInfo}>
              <Image source={{ uri: photo }} style={styles.avatar} />
              <View style={styles.infoText}>
                <Text style={styles.name}>{name}</Text>
                <Text style={styles.detail}>Age: {age}</Text>
                <Text style={styles.detail}>Sex: {sex}</Text>
                <Text style={styles.detail}>Phone: {phone}</Text>
                <Text style={styles.detail}>Address: {address}</Text>
              </View>
            </View>

            {/* Illness List */}
            <Text style={styles.sectionTitle}>Medical Conditions</Text>
            {summary.length > 0 ? (
              summary.map((item, index) => (
                <View key={index} style={styles.illnessItem}>
                  <Text style={styles.illnessName}>{item.disease}</Text>
                  <Text style={styles.importance}>
                    Importance: {item.importance}
                  </Text>
                  {item.medications && (
                    <Text style={styles.detail}>
                      Medications: {item.medications.join(", ")}
                    </Text>
                  )}
                  {item.startDate && item.endDate && (
                    <Text style={styles.detail}>
                      Treatment: {item.startDate} - {item.endDate}
                    </Text>
                  )}
                </View>
              ))
            ) : (
              <Text>No known illnesses.</Text>
            )}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "#fff", // Use white instead of semi-transparent
  },
  modalContent: {
    flex: 1,
    backgroundColor: "#fff",
    paddingTop: 40,
    paddingHorizontal: 20,
  },
  closeIcon: {
    alignSelf: "flex-end",
  },
  patientInfo: {
    flexDirection: "row",
    marginBottom: 16,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginRight: 16,
  },
  infoText: {
    flex: 1,
    justifyContent: "center",
  },
  name: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 4,
  },
  detail: {
    fontSize: 14,
    color: "#555",
    marginBottom: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 8,
  },
  illnessItem: {
    marginBottom: 10,
    backgroundColor: "#f2f2f2",
    padding: 10,
    borderRadius: 8,
  },
  illnessName: {
    fontSize: 16,
    fontWeight: "600",
  },
  importance: {
    fontSize: 14,
    color: "#777",
  },
  illnessItem: {
    marginBottom: 14,
    backgroundColor: "#f2f2f2",
    padding: 12,
    borderRadius: 8,
  },
});

export default ScanQRResult;
