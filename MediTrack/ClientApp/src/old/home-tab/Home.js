import React, { useState } from "react";
import { View, Text, StyleSheet, Dimensions, Image } from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import { ImageButton, CircleButton } from "../components/Button";
import Checkbox from "../components/CheckBox";
import CameraScreen from "./CameraScreen";
import ScanResult from "./ScanResult";
import { openCamera } from "./CameraHelper";

const { width, height } = Dimensions.get("window");
const _reminderCard = ({ icon, name, time, takenTime, onCheck, isTaken }) => {
  return (
    <View style={styles.card}>
      {/* Row 1: Icon, Texts, Checkbox */}
      <View style={styles.topRow}>
        <CircleButton
          imageSource={icon}
          style={styles.reminderIconButton}
          imageStyle={styles.reminderIcon}
        ></CircleButton>
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

      {/* Row 2 & 3: Taken & Missed */}
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

const Home = () => {
  const navigation = useNavigation();
  const [reminders, setReminders] = useState([
    {
      id: 1,
      name: "Ung thư xương",
      time: "8:00 AM",
      takenTime: "8:03 AM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },
    {
      id: 2,
      name: "Ung thư máu",
      time: "5:00 PM",
      takenTime: "5:30 PM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },

    {
      id: 3,
      name: "Ung thư gan",
      time: "8:00 PM",
      takenTime: "8:00 PM",
      icon: require("./assets/medicine-reminder.png"),
      taken: false,
    },
  ]);
  const [cameraVisible, setCameraVisible] = useState(false);
  const [showScanResult, setShowScanResult] = useState(false);

  const _handleTaken = (id) => {
    setReminders((prev) =>
      prev.map((reminder) =>
        reminder.id === id ? { ...reminder, taken: !reminder.taken } : reminder
      )
    );
  };

  const _handlScan = () => {
    setCameraVisible(false);
    setShowScanResult(true);
  };

  return (
    <View style={styles.container}>
      {/* Avatar */}
      <View style={styles.avatar}>
        <CircleButton
          onPress={() => {
            navigation.navigate("Profile");
          }}
        ></CircleButton>
      </View>

      {/* Header  */}
      <Text style={styles.header}>Home</Text>

      {/* Action  */}
      <View style={styles.action}>
        {/* Scan Prescription  */}
        <ImageButton
          text={"Scan\nPrescription"}
          textStyle={styles.actionName}
          style={styles.button}
          imageSource={require("./assets/scan-icon.png")}
          imageStyle={styles.image}
          onPress={() => setCameraVisible(true)}
        ></ImageButton>
        <CameraScreen
          visible={cameraVisible}
          onClose={() => setCameraVisible(false)}
          onCapture={_handlScan}
        />

        <ScanResult
          visible={showScanResult}
          onClose={() => setShowScanResult(false)}
        />

        {/* Add Manually  */}
        <ImageButton
          text={"Add\nManually"}
          textStyle={styles.actionName}
          style={styles.button}
          imageSource={require("./assets/add-icon.png")}
          imageStyle={styles.image}
        ></ImageButton>
      </View>

      {/* Reminder Section */}
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
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },

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
    marginLeft: 0.12 * width + 8, // = total padding of reminderIconButton
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
