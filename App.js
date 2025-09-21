import LandingPage from "./ClientApp/src/login/LandingPage";
import LandingPage2 from "./ClientApp/src/login/LandingPage2";
import LoginForm from "./ClientApp/src/login/LoginForm";
import SignUp from "./ClientApp/src/sign-up/SignUp";
import MainTab from "./ClientApp/src/main/MainTab";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="LandingPage">
        <Stack.Screen
          name="LandingPage"
          component={LandingPage}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="LandingPage2"
          component={LandingPage2}
          options={{ headerShown: false }}
        />

        <Stack.Screen
          name="LoginForm"
          component={LoginForm}
          options={{ headerShown: false }}
        />

        <Stack.Screen
          name="SignUp"
          component={SignUp}
          options={{ headerShown: false }}
        />

        <Stack.Screen
          name="MainTab"
          component={MainTab}
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
