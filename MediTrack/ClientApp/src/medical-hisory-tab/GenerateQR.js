import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Modal,
} from "react-native";
import QRCode from "react-native-qrcode-svg";

const { width, height } = Dimensions.get("window");

const QRCodeScreen = ({ visible, onClose, data }) => {
  return (
    <Modal visible={visible} transparent={true} animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.modalContainer}>
          <Text style={styles.title}>Your Medical QR Code</Text>
          <QRCode value={data} size={220} />
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeText}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContainer: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 30,
    alignItems: "center",
    width: width * 0.8,
  },
  title: {
    fontSize: 20,
    fontWeight: "600",
    marginBottom: 20,
    color: "#333",
  },
  closeButton: {
    marginTop: 20,
    backgroundColor: "#347CFF",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  closeText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
  },
});

export default QRCodeScreen;
