import React, { useState } from "react";
import { StyleSheet, View, Image, Dimensions, Text } from "react-native";
import globalStyles from "../GlobalStyles";
import { GradientButton } from "../components/Button";
import { useNavigation } from "@react-navigation/native"; //
const { width: screenWidth, height: screenHeight } = Dimensions.get("window");

const LandingPage = () => {
  const navigation = useNavigation();
  return (
    <View style={styles.container}>
      <Image
        source={require("../../assets/logo-name.png")}
        style={styles.logo}
        resizeMode="contain"
      ></Image>
      <Image
        source={require("./decoration.png")}
        style={styles.decoration}
        resizeMode="contain"
      ></Image>
      <Text style={[globalStyles.headingThree, styles.slogan]}>
        Know What You Take,{"\n"}Trust What You Share.
      </Text>
      <Text style={[globalStyles.textBased, styles.description]}>
        Track your medical interaction usage, set reminders and stay healthy
        with ease.
      </Text>
      <View style={styles.startButton}>
        <GradientButton
          title="Get Started"
          onPress={() => navigation.navigate("LandingPage2")}
        ></GradientButton>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff", // white background
    alignItems: "center",
  },
  logo: {
    height: screenHeight * 0.2,
    alignSelf: "center",
    marginTop: "17%",
  },

  decoration: {
    height: screenHeight * 0.3,
    alignSelf: "center",
  },

  slogan: {
    marginTop: screenHeight * 0.02,
    display: "flex",
  },

  description: {
    textAlign: "center",
    marginTop: screenHeight * 0.05,
    width: screenWidth * 0.9,
  },

  startButton: {
    marginTop: screenHeight * 0.05,
  },
});

export default LandingPage;
