// components/SearchBar.js
import React from "react";
import { View, TextInput, StyleSheet } from "react-native";
import Icon from "react-native-vector-icons/Ionicons";

const SearchBar = ({ value, onChangeText, placeholder = "Search", style }) => {
  return (
    <View style={[styles.container, style]}>
      <Icon name="search" size={20} color="#555" style={styles.icon} />
      <TextInput
        style={styles.input}
        placeholder={placeholder}
        placeholderTextColor="#888"
        value={value}
        onChangeText={onChangeText}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: "#F8F9FE",
    borderRadius: 15,
    paddingHorizontal: 12,
    alignItems: "center",
    height: 50,
    width: 300,
  },
  icon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: "#000",
  },
});

export default SearchBar;
