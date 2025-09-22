import React from "react";
import { StyleSheet, View, Text, Image } from "react-native";
import globalStyles from "../GlobalStyles";
import { GradientButton } from "../components/Button";
import { useNavigation } from "@react-navigation/native";

const LandingPage2 = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <Text style={[globalStyles.headingThree, styles.keyFeatures]}>
        Key Features{" "}
      </Text>
      <Image
        source={require("./decoration2.png")}
        resizeMode="contain"
        style={styles.decoration2}
      ></Image>
      <Image
        source={require("./decoration3.png")}
        resizeMode="contain"
        style={[styles.decoration2, styles.decoration3]}
      ></Image>
      <View style={styles.nextButton}>
        <GradientButton
          title="Next"
          onPress={() => navigation.navigate("LoginForm")}
          style={styles.nextButtonSize}
        ></GradientButton>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    backgroundColor: "#ffffff",
  },

  decoration2: {
    // width: 0.7 * screenWidth,
    marginTop: "19%",
    height: "27%",
  },

  decoration3: {
    marginTop: "5%",
  },

  keyFeatures: {
    marginTop: "15%",
  },
  nextButton: {
    marginTop: "15%",
  },

  nextButtonSize: {
    width: 140,
    height: 45,
  },
});

export default LandingPage2;
