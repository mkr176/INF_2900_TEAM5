import React, { useState } from "react";
import { motion } from "framer-motion";
import "./SignUpPage.css";

const SignUpPage = () => {
  const [formData, setFormData] = useState({
    fullName: "",
    username: "",
    birthDate: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const calculateAge = (birthDate) => {
    const birthDateObj = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birthDateObj.getFullYear();
    const monthDiff = today.getMonth() - birthDateObj.getMonth();
    const dayDiff = today.getDate() - birthDateObj.getDate();

    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
      age--;
    }

    return age;
  };

  const handleSignUp = () => {
    const { fullName, username, birthDate, email, password } = formData;

    if (!fullName || !username || !birthDate || !email || !password) {
      alert("All fields are required!");
      return;
    }

    if (password.length < 6) {
      alert("Password must be at least 6 characters long!");
      return;
    }

    if (calculateAge(birthDate) < 16) {
      alert("You must be at least 16 years old to register.");
      return;
    }

    alert("Sign-up successful!");
    window.location.href = "/login";
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-r from-teal-500 to-cyan-500">
      <motion.div
        className="bg-white p-8 rounded-2xl shadow-xl w-96 text-center"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-teal-900 mb-6">Create Account</h1>
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="text"
          name="fullName"
          placeholder="Full Name"
          value={formData.fullName}
          onChange={handleChange}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all"
        />
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all"
        />
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="date"
          name="birthDate"
          value={formData.birthDate}
          onChange={handleChange}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all"
        />
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all"
        />
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSignUp}
          className="w-full bg-teal-700 text-white py-3 rounded-lg font-semibold hover:bg-teal-800 transition-all"
        >
          Sign Up
        </motion.button>
      </motion.div>
    </div>
  );
};

export default SignUpPage;
