import React, { useState } from "react";
import { View, Text, StyleSheet, Dimensions, Image } from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import { ImageButton, CircleButton } from "../components/Button";
import Checkbox from "../components/CheckBox";
const { width, height } = Dimensions.get("window");

const Language = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.header}>Language</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },

  header: {
    ...globalStyles.headingTwo,
    alignSelf: "center",
    marginTop: 0.1 * height,
    padding: 2,
  },
});

export default Language;
