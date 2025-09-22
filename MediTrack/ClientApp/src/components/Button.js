import React from "react";
import { TouchableOpacity, Text, Image, StyleSheet, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient"; // or from 'react-native-linear-gradient'

export const GradientButton = ({ title, onPress, style }) => {
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
      <LinearGradient
        colors={["#A4C4FF", "#3876FF"]}
        style={[styles.rectangleButton, style]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <Text style={styles.buttonText}>{title}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );
};
export const SolidButton = ({ title, onPress, style }) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[styles.rectangleButton, style]}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </TouchableOpacity>
  );
};
export const ImageButton = ({
  imageSource = require("../../assets/logo.png"), // default icon
  text = "Scan Prescription",
  style = {},
  imageStyle = {},
  textStyle = {},
  onPress = () => {},
}) => {
  return (
    <TouchableOpacity style={[styles.rectangleButton, style]} onPress={onPress}>
      <Image source={imageSource} style={[styles.image, imageStyle]} />
      <Text style={[styles.buttonText, textStyle]}>{text}</Text>
    </TouchableOpacity>
  );
};
export const CircleButton = ({
  imageSource = require("../../assets/logo.png"), //default
  style = {},
  imageStyle = {},
  onPress = () => {},
}) => {
  return (
    <TouchableOpacity style={[styles.circleButton, style]} onPress={onPress}>
      <Image
        source={imageSource}
        style={[styles.buttonImage, imageStyle]}
      ></Image>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  rectangleButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 9,
    alignItems: "center",
    backgroundColor: "#006FFD",
  },
  circleButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden",
  },

  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },

  buttonImage: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
});
