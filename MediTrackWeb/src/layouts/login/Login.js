import React, { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { useAuth } from "../../context/AuthContext";
import { LoadingSpinner, Toast } from "../../components/CommonComponents";

function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [signUpData, setSignUpData] = useState({
    fullName: "",
    phone: "",
    dateOfBirth: "",
    emergencyContact: ""
  });
  const [toast, setToast] = useState(null);
  
  const navigate = useNavigate();
  const { login, register, isLoading, error, clearError } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setToast({ message: "Please fill in all fields", type: "error" });
      return;
    }

    try {
      await login(email, password);
      setToast({ message: "Login successful!", type: "success" });
      navigate("/home");
    } catch (error) {
      setToast({ message: error.message, type: "error" });
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    if (!email || !password || !signUpData.fullName) {
      setToast({ message: "Please fill in all required fields", type: "error" });
      return;
    }

    try {
      await register({
        email,
        password,
        full_name: signUpData.fullName,
        phone: signUpData.phone,
        date_of_birth: signUpData.dateOfBirth,
        emergency_contact: signUpData.emergencyContact
      });
      setToast({ message: "Registration successful! Please check your email for verification.", type: "success" });
      setIsSignUp(false);
    } catch (error) {
      setToast({ message: error.message, type: "error" });
    }
  };

  const toggleForm = () => {
    setIsSignUp(!isSignUp);
    clearError();
    setEmail("");
    setPassword("");
    setSignUpData({
      fullName: "",
      phone: "",
      dateOfBirth: "",
      emergencyContact: ""
    });
  };

  return (
    <div className="login-wrapper">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      
      <div className="login-box">
        <img src="/logo.png" alt="Logo" className="logo" />
        <h1>
          Welcome to <span className="highlight-blue">MEDI</span>
          <span className="highlight-green">TRACK</span>
        </h1>
        <p className="subtitle">
          Your personal health companion — scan, track,
          <br />
          and stay safe with your medications.
        </p>

        <form onSubmit={isSignUp ? handleSignUp : handleLogin}>
          <div className="form-group">
            {isSignUp && (
              <>
                <input
                  type="text"
                  placeholder="Full Name *"
                  value={signUpData.fullName}
                  onChange={(e) => setSignUpData(prev => ({ ...prev, fullName: e.target.value }))}
                  required
                />
                <input
                  type="tel"
                  placeholder="Phone Number"
                  value={signUpData.phone}
                  onChange={(e) => setSignUpData(prev => ({ ...prev, phone: e.target.value }))}
                />
                <input
                  type="date"
                  placeholder="Date of Birth"
                  value={signUpData.dateOfBirth}
                  onChange={(e) => setSignUpData(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                />
                <input
                  type="text"
                  placeholder="Emergency Contact"
                  value={signUpData.emergencyContact}
                  onChange={(e) => setSignUpData(prev => ({ ...prev, emergencyContact: e.target.value }))}
                />
              </>
            )}
            
            <input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <div className="password-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <span
                className="toggle-password"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </span>
            </div>
          </div>

          {!isSignUp && (
            <a href="#" className="forgot">
              Forgot password?
            </a>
          )}

          <button 
            className="login-btn" 
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <LoadingSpinner size="small" color="white" />
            ) : (
              isSignUp ? "Sign Up" : "Log In"
            )}
          </button>

          <div className="bottom-text">
            {isSignUp ? "Already have an account?" : "Not a member?"}{" "}
            <a href="#" onClick={(e) => { e.preventDefault(); toggleForm(); }}>
              {isSignUp ? "Sign In" : "Sign Up now"}
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
