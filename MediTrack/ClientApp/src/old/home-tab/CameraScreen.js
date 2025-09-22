import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Dimensions,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";

const { width, height } = Dimensions.get("window");

const CameraScreen = ({ visible, onClose, onCapture }) => {
  const SCAN_HEIGHT = 500; // custom height

  return (
    <Modal visible={visible} animationType="slide" transparent={false}>
      <View style={styles.container}>
        {/* Top bar */}
        <View style={styles.topBar}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={32} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Camera preview area */}
        <View style={styles.cameraPreview}>
          {/* Full-width scan frame with corner indicators */}
          <View style={[styles.scanFrame, { height: SCAN_HEIGHT }]}>
            {/* Top Left */}
            <View style={[styles.corner, styles.topLeft]}>
              <View style={styles.cornerVertical} />
              <View style={styles.cornerHorizontal} />
            </View>

            {/* Top Right */}
            <View style={[styles.corner, styles.topRight]}>
              <View style={styles.cornerVertical} />
              <View style={styles.cornerHorizontal} />
            </View>

            {/* Bottom Left */}
            <View style={[styles.corner, styles.bottomLeft]}>
              <View style={styles.cornerVertical} />
              <View style={styles.cornerHorizontal} />
            </View>

            {/* Bottom Right */}
            <View style={[styles.corner, styles.bottomRight]}>
              <View style={styles.cornerVertical} />
              <View style={styles.cornerHorizontal} />
            </View>
          </View>

          <Text style={styles.hintText}>
            Align the prescription within the highlighted area
          </Text>
        </View>

        {/* Bottom bar */}
        <View style={styles.bottomBar}>
          {/* Album Button */}
          <TouchableOpacity style={styles.albumButton}>
            <Ionicons name="images-outline" size={50} color="#fff" />
          </TouchableOpacity>

          {/* Shutter Button */}
          <TouchableOpacity
            onPress={onCapture}
            style={styles.shutterButtonOuter}
          >
            <View style={styles.shutterButtonInner} />
          </TouchableOpacity>

          {/* Placeholder to balance layout */}
          <View style={styles.albumButton} />
        </View>
      </View>
    </Modal>
  );
};

const cornerLength = 30;
const cornerThickness = 1;
const cornerColor = "#ffff";

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  topBar: {
    position: "absolute",
    top: 40,
    left: 20,
    zIndex: 10,
  },
  closeButton: {
    padding: 10,
  },
  cameraPreview: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  scanFrame: {
    width: width,
    position: "relative",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#424242",
  },
  corner: {
    position: "absolute",
    width: cornerLength,
    height: cornerLength,
  },
  cornerVertical: {
    position: "absolute",
    width: cornerThickness,
    height: cornerLength,
    backgroundColor: cornerColor,
  },
  cornerHorizontal: {
    position: "absolute",
    width: cornerLength,
    height: cornerThickness,
    backgroundColor: cornerColor,
  },
  topLeft: {
    top: 0,
    left: 0,
  },
  topRight: {
    top: 0,
    right: 0,
    transform: [{ rotateY: "180deg" }],
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    transform: [{ rotateX: "180deg" }],
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    transform: [{ rotate: "180deg" }],
  },
  hintText: {
    color: "#ccc",
    marginTop: 20,
    fontSize: 16,
    textAlign: "center",
  },
  bottomBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingBottom: 40,
    paddingHorizontal: 40,
  },
  albumButton: {
    width: 70,
    height: 70,
    justifyContent: "center",
    alignItems: "center",
  },
  shutterButtonOuter: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 6,
    borderColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
  },
  shutterButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#fff",
  },
});

export default CameraScreen;
