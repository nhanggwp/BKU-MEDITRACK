import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  Image,
} from "react-native";
import globalStyles from "../GlobalStyles";
import { useNavigation } from "@react-navigation/native";
import { CircleButton } from "../components/Button";
import Icon from "react-native-vector-icons/MaterialIcons";
import Iconicon from "react-native-vector-icons/Ionicons";

const { width, height } = Dimensions.get("window");

const _profileAvatar = ({ name, email, imageSource, onEditPress }) => {
  return (
    <View style={styles.profileAvatarSection}>
      <View style={styles.avatarContainer}>
        <Image source={imageSource} style={styles.profileAvatar} />
        <TouchableOpacity style={styles.editIcon} onPress={onEditPress}>
          <Icon name="edit" size={20} color="#fff" />
        </TouchableOpacity>
      </View>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.email}>{email}</Text>
    </View>
  );
};

// Profile Menu Helpers
const profileMenuList = [
  { label: "Notification", screen: "Notification" },
  { label: "Device", screen: "Device" },
  { label: "Appearance", screen: "Appearance" },
  { label: "Privacy & Security", screen: "PrivacySecurity" },
  { label: "Storage", screen: "Storage" },
  { label: "Language", screen: "Language" },
];

const _profileMenuItem = ({ label, onPress }) => (
  <TouchableOpacity style={styles.itemContainer} onPress={onPress}>
    <Text style={styles.menuText}>{label}</Text>
    <Iconicon name="chevron-forward" size={20} color="#999" />
  </TouchableOpacity>
);

const _profileMenu = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      {profileMenuList.map((item, index) => (
        <View key={index}>
          <_profileMenuItem
            label={item.label}
            onPress={() => navigation.navigate(item.screen)}
          />
          <View style={styles.line} />
        </View>
      ))}
    </View>
  );
};

const Profile = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      {/* Top Right Avatar  */}
      <CircleButton style={styles.avatar}></CircleButton>

      {/* Header  */}
      <Text style={styles.header}>Profile</Text>

      {/* Profile Avatar  */}
      <_profileAvatar
        name="MediTrack"
        email="meditrack@hcmut.edu.vn"
        imageSource={require("../../assets/logo.png")}
      ></_profileAvatar>

      {/* Profile Menu  */}
      <_profileMenu></_profileMenu>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },

  avatar: {
    position: "absolute",
    top: 60,
    right: 20,
  },

  header: {
    ...globalStyles.headingTwo,
    alignSelf: "center",
    marginTop: 0.1 * height,
    padding: 2,
  },

  profileAvatarSection: {
    marginTop: 10,
    alignItems: "center",
    alignSelf: "center",
    marginBottom: 40,
  },

  avatarContainer: {
    position: "relative",
  },
  profileAvatar: {
    width: 70,
    height: 70,
    borderRadius: 50,
  },
  editIcon: {
    position: "absolute",
    bottom: 0,
    right: 0,
    backgroundColor: "#347CFF",
    borderRadius: 16,
    padding: 4,
  },
  name: {
    marginTop: 12,
    fontSize: 20,
    fontWeight: "bold",
  },
  email: {
    fontSize: 16,
    color: "gray",
  },

  itemContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 18,
    paddingHorizontal: 16,
    alignItems: "center",
    backgroundColor: "#fff",
  },

  menuText: {
    ...globalStyles.textBased,
    marginLeft: 18,
  },

  line: {
    height: 1,
    backgroundColor: "#eee",
    marginLeft: 16,
  },
});
export default Profile;
