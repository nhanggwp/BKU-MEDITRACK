import React, { useState } from "react";
import { View, TextInput, StyleSheet } from "react-native";

const Input = ({
  textHolder,
  value,
  onChangeText,
  secureTextEntry = false,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <View style={styles.container}>
      <TextInput
        style={[
          styles.input,
          { borderColor: isFocused ? "#007AFF" : "#ccc" }, // Xanh khi focus
        ]}
        placeholder={textHolder}
        placeholderTextColor="#aaa"
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={secureTextEntry}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 7,
    justifyContent: "center",
  },
  input: {
    width: 300,
    height: 50,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 15,
    fontSize: 16,
    backgroundColor: "#fff",
  },
});

export default Input;
