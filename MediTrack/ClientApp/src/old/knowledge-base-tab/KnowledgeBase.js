import React, { useState } from "react";
import { View, Text, StyleSheet, Dimensions, Image } from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import { ImageButton, CircleButton } from "../components/Button";
import Checkbox from "../components/CheckBox";
const { width, height } = Dimensions.get("window");

const KnowledgeBase = () => {
  const navigation = useNavigation();
  return (
    <View style={styles.container}>
      {/* Avatar  */}
      <View style={styles.avatar}>
        <CircleButton
          onPress={() => {
            navigation.navigate("Profile");
          }}
        ></CircleButton>
      </View>

      {/* Header  */}
      <Text style={styles.header}>Knowledge Base</Text>
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
    padding: 2,
  },
});

export default KnowledgeBase;
