import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import SearchBar from "../components/SearchBar";
import Icon from "react-native-vector-icons/Ionicons";
import { CircleButton } from "../components/Button";
const { width, height } = Dimensions.get("window");

const _QrButton = ({ onPress }) => {
  return (
    <TouchableOpacity style={styles.QrButton} onPress={onPress}>
      <Icon
        name="qr-code-outline"
        size={50}
        color="#fff"
        style={styles.QrIcon}
      />
      <View style={styles.QrTextContainer}>
        <Text style={styles.QrTitle}>Generate QR Code</Text>
        <Text style={styles.QrSubtitle}>Include Side Effect log</Text>
      </View>
    </TouchableOpacity>
  );
};

const _sortButton = ({ currentSort, onSelect }) => {
  const [showOptions, setShowOptions] = useState(false);

  const options = [
    { label: "Importance", value: "importance" },
    { label: "Start Date", value: "date" },
  ];

  const toggleOptions = () => setShowOptions(!showOptions);

  const selectOption = (value) => {
    onSelect(value);
    setShowOptions(false);
  };

  return (
    <View style={styles.sortWrapper}>
      <TouchableOpacity style={styles.sortButton} onPress={toggleOptions}>
        <Text style={styles.sortButtonText}>Sort by: {currentSort}</Text>
      </TouchableOpacity>

      {showOptions && (
        <View style={styles.optionsContainer}>
          {options.map(({ label, value }) => (
            <TouchableOpacity
              key={value}
              style={styles.option}
              onPress={() => selectOption(value)}
            >
              <Text style={styles.optionText}>{label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
};

const _importanceTag = ({ level }) => {
  const colors = {
    high: "#EF4444", // Red
    medium: "#F59E0B", // Orange
    low: "#3B82F6", // Blue
  };

  return (
    <View style={[styles.tag, { backgroundColor: colors[level] || "#ccc" }]}>
      <Text style={styles.tagText}>{level.toUpperCase()}</Text>
    </View>
  );
};

const _medicalRecordCard = ({
  name,
  medications,
  startDate,
  endDate,
  importance,
}) => {
  return (
    <View style={styles.medicalRecord}>
      {/* Card Header  */}
      <View style={styles.cardHeader}>
        <Text style={globalStyles.headingThree}>{name}</Text>
        <_importanceTag level={importance} />
      </View>

      {/* Medications  */}
      <View style={styles.row}>
        <Text style={styles.cardLabel}>Medications:</Text>
        <Text style={styles.cardValue}>{medications}</Text>
      </View>

      {/* Treament Period  */}
      <View style={styles.row}>
        <Text style={styles.cardLabel}>Treatment Period:</Text>
        <Text style={styles.cardValue}>
          {startDate} - {endDate}
        </Text>
      </View>

      {/* Separator  */}
      <View style={styles.line} />
    </View>
  );
};

const MedicalHistory = () => {
  const navigation = useNavigation();
  const [medicalRecords, setRecord] = useState([
    {
      id: 1,
      name: "Ung thư máu",
      medications: [
        "Aspirin",
        "Paracetamol",
        "Ibuprofen",
        "Amoxicillin",
        "Metformin",
        "Lisinopril",
        "Simvastatin",
        "Omeprazole",
        "Azithromycin",
        "Hydrochlorothiazide",
        "Gabapentin",
        "Levothyroxine",
        "Atorvastatin",
        "Clopidogrel",
        "Losartan Potassium",
      ],
      startDate: "27 May 2025",
      endDate: "1 June 2025",
      importance: "high",
    },
    {
      id: 2,
      name: "Ung thư xương",
      medications: ["Aspirin", "Panadol", "Canxi"],
      startDate: "28 May 2025",
      endDate: "2 June 2025",
      importance: "high",
    },
    {
      id: 3,
      name: "Sốt rét",
      medications: ["Panadol"],
      startDate: "28 May 2025",
      endDate: "2 June 2025",
      importance: "low",
    },

    {
      id: 4,
      name: "Viêm gan B",
      medications: [
        "Amoxicillin",
        "Metformin",
        "Lisinopril",
        "Simvastatin",
        "Omeprazole",
        "Azithromycin",
      ],
      startDate: "28 May 2025",
      endDate: "2 June 2025",
      importance: "medium",
    },

    {
      id: 5,
      name: "Sốt xuất huyết",
      medications: ["Metformin"],
      startDate: "28 May 2025",
      endDate: "2 June 2025",
      importance: "low",
    },
  ]);
  const [sortMode, setSortMode] = useState("importance");

  const _sortRecords = (mode) => {
    let sortedRecords = [...medicalRecords];
    if (mode === "importance") {
      const order = { high: 1, medium: 2, low: 3 };
      sortedRecords.sort((a, b) => order[a.importance] - order[b.importance]);
    } else if (mode === "date") {
      sortedRecords.sort(
        (a, b) => new Date(a.startDate) - new Date(b.startDate)
      );
    }
    setRecord(sortedRecords);
    setSortMode(mode);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Avatar  */}
      <CircleButton
        style={styles.avatar}
        onPress={() => {
          navigation.navigate("Profile");
        }}
      ></CircleButton>

      {/* Header  */}
      <Text style={styles.header}>Medical History</Text>

      {/* Search Bar  */}
      <SearchBar style={styles.searchBar}></SearchBar>

      {/* QR Generate  */}
      <_QrButton></_QrButton>

      {/* Sorting */}
      <_sortButton currentSort={sortMode} onSelect={_sortRecords} />

      {/* Medical Records  */}
      {medicalRecords.map((medicalRecord) => (
        <_medicalRecordCard
          key={medicalRecord.id}
          name={medicalRecord.name}
          medications={medicalRecord.medications.join(", ")}
          startDate={medicalRecord.startDate}
          endDate={medicalRecord.endDate}
          importance={medicalRecord.importance}
        ></_medicalRecordCard>
      ))}
    </ScrollView>
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
    paddingVertical: 2,
  },
  searchBar: {
    width: "80%",
    marginTop: 15,
    marginBottom: 15,
    alignSelf: "center",
  },

  QrButton: {
    flexDirection: "row",
    backgroundColor: "#347CFF",
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: "center",
    width: "75%",
    height: "7%",
    alignSelf: "center",
  },
  QrIcon: {
    marginRight: 12,
  },
  QrTextContainer: {
    flexDirection: "column",
  },
  QrTitle: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "600",
  },
  QrSubtitle: {
    color: "#e0e7ff",
    fontSize: 15,
  },

  medicalRecord: {
    marginTop: "5%",
    marginLeft: "11%",
  },

  line: {
    height: 1,
    width: width * 0.75,
    backgroundColor: "#ccc",
    marginVertical: 8,
    alignSelf: "center",
    marginLeft: -0.11 * width, // equal leftMargin of medicalRecord
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginTop: 4,
    marginRight: 35,
    // backgroundColor: "red",
    gap: 10,
  },

  cardHeader: {
    flexDirection: "row",
    gap: 10,
    alignItems: "center",
    marginRight: 20,
  },

  tag: {
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 8,
  },

  tagText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 12,
  },

  cardLabel: {
    ...globalStyles.textBased,
    fontWeight: "bold",
  },

  cardValue: {
    flex: 1,
    color: "#333",
  },

  sortWrapper: {
    marginTop: 20,
    width: "40%",
    marginLeft: "11%",
  },
  sortButton: {
    backgroundColor: "#e5e7eb",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  sortButtonText: {
    ...globalStyles.textBased,
    fontSize: 12,
  },
  optionsContainer: {
    marginTop: 6,
    backgroundColor: "#f0f0f0",
    borderRadius: 8,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "#ccc",
  },
  option: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
  },
  optionText: {
    fontSize: 15,
    color: "#333",
  },
});
export default MedicalHistory;
