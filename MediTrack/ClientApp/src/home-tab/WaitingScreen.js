// WaitingScreen.js
import React from "react";
import { Modal, View, ActivityIndicator, Text, StyleSheet } from "react-native";

const WaitingScreen = ({ visible }) => {
  return (
    <Modal
      transparent
      animationType="fade"
      visible={visible}
      statusBarTranslucent
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          <ActivityIndicator size="large" color="#007bff" />
          <Text style={styles.text}>Processing...</Text>
        </View>
      </View>
    </Modal>
  );
};

export default WaitingScreen;

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.3)",
    justifyContent: "center",
    alignItems: "center",
  },
  container: {
    padding: 30,
    borderRadius: 10,
    backgroundColor: "#fff",
    alignItems: "center",
  },
  text: {
    marginTop: 10,
    fontSize: 16,
    color: "#333",
  },
});
