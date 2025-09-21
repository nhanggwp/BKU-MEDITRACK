import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Keyboard,
  Image,
} from "react-native";

const Chat = () => {
  const [messages, setMessages] = useState([
    { id: "1", text: "Hi! How can I help you today?", from: "bot" },
  ]);
  const [inputText, setInputText] = useState("");
  const flatListRef = useRef();

  const sendMessage = () => {
    if (inputText.trim() === "") return;

    const newMessage = {
      id: Date.now().toString(),
      text: inputText,
      from: "user",
    };

    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputText("");

    // Simulate bot response
    setTimeout(() => {
      const botReply = {
        id: Date.now().toString() + "-bot",
        text: "Hi, I'm MediTrack, how are you?",
        from: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, botReply]);
    }, 500);
  };

  // Scroll to bottom when new message is added
  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const renderItem = ({ item }) => (
    <View
      style={[
        styles.messageRow,
        item.from === "user" ? styles.userRow : styles.botRow,
      ]}
    >
      {item.from === "bot" && (
        <Image
          source={require("../../assets/logo.png")}
          style={styles.botLogo}
        />
      )}
      <View
        style={[
          styles.messageContainer,
          item.from === "user" ? styles.userMessage : styles.botMessage,
        ]}
      >
        <Text style={styles.messageText}>{item.text}</Text>
      </View>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 5 : 0}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={() =>
          flatListRef.current?.scrollToEnd({ animated: true })
        }
        onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />
      {/* Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type a message..."
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={sendMessage}
          returnKeyType="send"
        />
        <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.disclaimer}>
        MediTrack may make mistakes. Please verify important information.
      </Text>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  messagesList: {
    marginTop: 30,
    padding: 20,
    paddingBottom: 80,
  },
  messageContainer: {
    marginTop: 10,
    marginVertical: 10,
    maxWidth: "80%",
    borderRadius: 15,
    padding: 10,
  },
  userMessage: {
    backgroundColor: "#DCF8C6",
    alignSelf: "flex-end",
  },
  botMessage: {
    backgroundColor: "#E4E6EB",
    alignSelf: "flex-start",
  },
  messageText: {
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: "row",
    padding: 10,
    backgroundColor: "#f0f0f0",
    borderTopWidth: 1,
    borderColor: "#ccc",
    alignItems: "center",
  },
  input: {
    flex: 1,
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 15,
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ccc",
    marginRight: 10,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: "#007AFF",
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 20,
  },
  sendText: {
    color: "#fff",
    fontWeight: "bold",
  },

  messageRow: {
    flexDirection: "row",
    marginTop: 15,
    marginBottom: 10,
    maxWidth: "80%",
  },
  userRow: {
    alignSelf: "flex-end",
    justifyContent: "flex-end",
  },
  botRow: {
    alignSelf: "flex-start",
    justifyContent: "flex-start",
  },
  disclaimer: {
    textAlign: "center",
    fontSize: 10,
    color: "#999",
    marginHorizontal: 20,
    marginBottom: 5,
  },
  botLogo: {
    width: 30,
    height: 30,
    borderRadius: 15,
    marginRight: 10,
    alignSelf: "center",
  },
});

export default Chat;
