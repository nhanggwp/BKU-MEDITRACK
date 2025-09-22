import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import Profile from "./Profile";
import Notification from "../profile-menu/Notification";
import Appearance from "../profile-menu/Appearance";
import PrivacySecurity from "../profile-menu/PrivacySecurity";
import Storage from "../profile-menu/Storage";
import Device from "../profile-menu/Device";
import Language from "../profile-menu/Language";

const Stack = createNativeStackNavigator();

const ProfileStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ProfileMain" component={Profile} />
      <Stack.Screen name="Notification" component={Notification} />
      <Stack.Screen name="Device" component={Device} />
      <Stack.Screen name="Storage" component={Storage} />
      <Stack.Screen name="Appearance" component={Appearance} />
      <Stack.Screen name="PrivacySecurity" component={PrivacySecurity} />
      <Stack.Screen name="Language" component={Language} />
    </Stack.Navigator>
  );
};

export default ProfileStack;
