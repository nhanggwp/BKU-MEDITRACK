import React from "react";
import { TouchableOpacity, View, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";

const Checkbox = ({ checked, onToggle, boxStyle = {} }) => {
  return (
    <TouchableOpacity style={styles.checkboxContainer} onPress={onToggle}>
      <View style={[styles.checkbox, checked && styles.checked, boxStyle]}>
        {checked && <Ionicons name="checkmark" size={18} color="white" />}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  checkboxContainer: {
    padding: 4,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 1,
    borderColor: "#C5C6CC",
    borderRadius: 4,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "white",
  },
  checked: {
    backgroundColor: "#006FFD",
  },
});

export default Checkbox;
