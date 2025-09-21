import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Alert,
  Image,
  TouchableOpacity,
} from "react-native";
import Input from "../components/Input";
import globalStyles from "../GlobalStyles";
import { SolidButton } from "../components/Button";
import { useNavigation } from "@react-navigation/native";
import * as UtilitySet from "../utils/Set";

const LoginForm = () => {
  const navigation = useNavigation();
  const _handleForgetPassword = () => {
    //Dummy
    Alert.alert("Redirect", "You tapped on 'Forget password?'");
  };
  const _handleLogin = () => {
    navigation.navigate("MainTab");
  };
  const _handleSignUp = () => {
    navigation.navigate("SignUp");
  };

  return (
    <View style={styles.container}>
      {/* Logo */}
      <Image
        source={require("../../assets/logo.png")}
        style={styles.logo}
        resizeMode="contain"
      ></Image>
      <Image
        source={require("./welcome-to-meditrack.png")}
        style={styles.welcome}
        resizeMode="contain"
      ></Image>

      {/*Input*/}
      <View style={styles.input}>
        <Input textHolder="Email Address"></Input>
        <Input textHolder="Password"></Input>
      </View>
      <TouchableOpacity onPress={_handleForgetPassword}>
        <Text style={[globalStyles.textLink, styles.forget]}>
          Forget password?
        </Text>
      </TouchableOpacity>

      {/* Login */}
      <SolidButton
        title="Login"
        onPress={_handleLogin}
        style={styles.login}
      ></SolidButton>
      <View style={styles.line} />

      {/* SignUp  */}
      <View style={[globalStyles.row, globalStyles.alignSelfCenter]}>
        <Text style={[globalStyles.textGrey, UtilitySet.FontSize(12)]}>
          Not a member?{" "}
        </Text>
        <TouchableOpacity onPress={_handleSignUp}>
          <Text
            style={[
              globalStyles.textLink,
              styles.signUp,
              UtilitySet.FontSize(12),
            ]}
          >
            Sign Up now
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    // alignItems: "center",
    backgroundColor: "#fff",
  },

  logo: {
    height: "25%",
    marginTop: "27%",
    alignSelf: "center",
  },

  welcome: {
    height: "10%",
    marginTop: "5%",
    alignSelf: "center",
  },

  forget: {
    marginLeft: "13%",
    paddingVertical: 5,
  },

  input: {
    alignSelf: "center",
  },

  login: {
    width: 327,
    // height: "10%",
    marginTop: 24,
    backgroundColor: "#006FFD",
    alignSelf: "center",
  },

  line: {
    height: 1,
    width: "70%",
    backgroundColor: "#ccc",
    marginVertical: 16, // Optional spacing
    alignSelf: "center",
  },

  signUp: {
    paddingLeft: 3,
  },
});

export default LoginForm;
