import React, { useState } from "react";
import { View, TextInput, StyleSheet } from "react-native";

const InputExample = ({ textHolder }) => {
  const [text, setText] = useState("");

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder={textHolder}
        placeholderTextColor="#aaa"
        value={text}
        onChangeText={setText}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 7,
    // alignItems: "center",
    justifyContent: "center",
  },
  input: {
    width: 300,
    height: 50,
    borderColor: "#ccc",
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 15,
    fontSize: 16,
    backgroundColor: "#fff",
  },
});

export default InputExample;
