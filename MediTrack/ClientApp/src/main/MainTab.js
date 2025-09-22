import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Image } from "react-native";
import Home from "../home-tab/Home";
import MedicalHistory from "../medical-hisory-tab/MedicalHistory";
import KnowledgeBase from "../knowledge-base-tab/KnowledgeBase";
import ProfileStack from "../profile-tab/ProfileStack";
import Chat from "../chat-tab/Chat";
import Ionicons from "react-native-vector-icons/Ionicons";
import { useRoute } from "@react-navigation/native";

const Tab = createBottomTabNavigator();

const MainTab = () => {
  const route = useRoute();
  const { token } = route.params || {};

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          if (route.name === "Chat") {
            const iconName = focused ? "chatbubble" : "chatbubble-outline";
            return <Ionicons name={iconName} size={size} color={color} />;
          }

          let iconSource;
          if (route.name === "Home") {
            iconSource = focused
              ? require("./tab-icons/home-active.png")
              : require("./tab-icons/home.png");
          } else if (route.name === "Medical History") {
            iconSource = focused
              ? require("./tab-icons/history-active.png")
              : require("./tab-icons/history.png");
          } else if (route.name === "Knowledge Base") {
            iconSource = focused
              ? require("./tab-icons/knowledge-active.png")
              : require("./tab-icons/knowledge.png");
          } else if (route.name === "Profile") {
            iconSource = focused
              ? require("./tab-icons/profile-active.png")
              : require("./tab-icons/profile.png");
          }

          return (
            <Image source={iconSource} style={{ width: size, height: size }} />
          );
        },
      })}
    >
      <Tab.Screen name="Home" component={Home} initialParams={{ token }} />
      <Tab.Screen name="Medical History" component={MedicalHistory} />
      {/* <Tab.Screen name="Knowledge Base" component={KnowledgeBase} /> */}
      <Tab.Screen name="Chat" component={Chat} />
      <Tab.Screen name="Profile" component={ProfileStack} />
    </Tab.Navigator>
  );
};

export default MainTab;
