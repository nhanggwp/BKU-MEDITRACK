import React, { useState } from "react";
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Dimensions,
} from "react-native";
import globalStyles from "../GlobalStyles";
import InputExample from "../components/Input";
import { SolidButton } from "../components/Button";
import Checkbox from "../components/CheckBox";
import { useNavigation } from "@react-navigation/native";

const { width, height } = Dimensions.get("window");

export const SignUp = () => {
  const [checked, setChecked] = useState(false);
  const navigation = useNavigation();

  const _handleSignUp = () => {
    navigation.navigate("SignUp");
  };
  const _handleLogin = () => {
    navigation.navigate("LoginForm");
  };
  return (
    <View style={styles.container}>
      <View style={styles.innerLeftMarginContent}>
        {/* Header  */}
        <Text style={styles.header}>Sign Up</Text>
        <Text style={styles.headerDescription}>
          Create an account to get started
        </Text>

        {/* Input  */}
        <View style={styles.inputSection}>
          <Text style={styles.textBold}>Name</Text>
          <InputExample textHolder="Your Name"></InputExample>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.textBold}>Email</Text>
          <InputExample textHolder="meditrack@gmail.com"></InputExample>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.textBold}>Password</Text>
          <InputExample textHolder="Password"></InputExample>
          <InputExample textHolder="Confirm your password"></InputExample>
        </View>

        {/* Term & Agreement */}
        <View style={globalStyles.row}>
          <Checkbox
            checked={checked}
            onToggle={() => setChecked(!checked)}
          ></Checkbox>
          <Text style={styles.textAgreement}>
            I've read and agree with the{" "}
            <Text style={globalStyles.textLink}>
              Terms and {"\n"}Conditions{" "}
            </Text>
            and the <Text style={globalStyles.textLink}>Privacy Policy</Text>.
          </Text>
        </View>
      </View>

      <View style={styles.innerCenterContent}>
        {/* Sign Up Button */}
        <SolidButton
          title="Sign Up"
          onPress={_handleSignUp}
          style={styles.signUpButton}
        ></SolidButton>

        <View style={styles.line} />

        {/*Already registered? Login*/}
        <View style={[globalStyles.row, globalStyles.alignSelfCenter]}>
          <Text style={[styles.textGrey]}>Already registered? </Text>
          <TouchableOpacity onPress={_handleLogin}>
            <Text style={[globalStyles.textLink]}>Login now</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },

  innerLeftMarginContent: {
    marginLeft: 0.15 * width,
    // backgroundColor: "#000",
  },

  innerCenterContent: {
    alignSelf: "center",
    // backgroundColor: "red",
  },

  header: {
    ...globalStyles.headingThree,
    paddingVertical: "1%",
    marginTop: "25%",
    fontSize: 32,
    lineHeight: 35,
  },
  headerDescription: {
    ...globalStyles.textGrey,
    fontSize: 16,
    marginBottom: "10%",
  },

  textBold: {
    ...globalStyles.textBased,
    fontWeight: "700",
  },

  inputSection: {
    marginBottom: "3%",
  },

  textAgreement: {
    width: 282,
    height: 32,
    ...globalStyles.textGrey,
    fontSize: 12,
    marginLeft: "4%",
    marginTop: "-1%",
  },

  line: {
    height: 1,
    width: 0.45 * width,
    backgroundColor: "#ccc",
    marginVertical: 5, // Optional spacing
    alignSelf: "center",
  },

  signUpButton: {
    width: 0.72 * width,
    marginVertical: "5%",
  },

  textGrey: {
    ...globalStyles.textGrey,
    fontSize: 12,
  },
});
export default SignUp;
