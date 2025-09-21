import React, { useEffect, useRef, useState } from "react";
import {
  View,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Dimensions,
  Text,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { CameraView, useCameraPermissions, CameraType } from "expo-camera";

const CameraScreen = ({ visible, onClose, onCapture, onScanComplete }) => {
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState("back");
  const [flash, setFlash] = useState("off");
  const [scanned, setScanned] = useState(false);
  const cameraRef = useRef(null);

  useEffect(() => {
    if (!permission) requestPermission();
  }, [permission]);

  useEffect(() => {
    if (!visible) setScanned(false);
  }, [visible]);

  const _handleBarCodeScanned = (result) => {
    if (!scanned) {
      setScanned(true);
      try {
        const data = JSON.parse(result.data);
        onScanComplete && onScanComplete(data);
        onClose();
      } catch (e) {
        console.warn("Invalid QR code data");
      }
    }
  };

  const handleTakePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
      });
      onCapture && onCapture(photo);
      onClose();
    }
  };

  if (!permission?.granted) return <View style={styles.container} />;

  return (
    <Modal visible={visible} animationType="slide">
      <View style={styles.container}>
        {/* Camera View */}
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          facing={facing}
          flash={flash}
          onBarcodeScanned={_handleBarCodeScanned}
          ratio="16:9"
        />

        {/* Controls */}
        <View style={styles.topBar}>
          <TouchableOpacity onPress={onClose} style={styles.iconButton}>
            <Ionicons name="close" size={30} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setFlash((prev) => (prev === "off" ? "torch" : "off"));
            }}
            style={styles.iconButton}
          >
            <Ionicons name="flashlight" size={28} color="#fff" />
          </TouchableOpacity>
        </View>

        <View style={styles.bottomBar}>
          <TouchableOpacity onPress={handleTakePicture} style={styles.shutter}>
            <View style={styles.shutterInner} />
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  camera: { flex: 1 },
  topBar: {
    position: "absolute",
    top: 40,
    left: 20,
    right: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    zIndex: 1,
  },
  iconButton: {
    padding: 10,
  },
  bottomBar: {
    position: "absolute",
    bottom: 40,
    alignSelf: "center",
  },
  shutter: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 6,
    borderColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
  },
  shutterInner: {
    width: 60,
    height: 60,
    backgroundColor: "#fff",
    borderRadius: 30,
  },
});

export default CameraScreen;
