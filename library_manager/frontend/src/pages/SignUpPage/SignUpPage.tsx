import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { useAuth } from "../../context/AuthContext"; // Import useAuth for CSRF
import "./SignUpPage.css"; // Keep existing styles

// Define minimum password length (should match backend if possible)
const MIN_PASSWORD_LENGTH = 8; // Example, adjust if backend has different rules

const SignUpPage = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
        password2: "", // For password confirmation
        first_name: "", // Optional
        last_name: "", // Optional
        age: "", // Optional, will be sent as number if provided
  });
    const navigate = useNavigate(); // Hook for navigation
    const { getCSRFToken } = useAuth(); // Hook to get CSRF token method

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { // Add type for event
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };



    const handleSignUp = async () => {
        const { username, email, password, password2, first_name, last_name, age } = formData;

        // --- Client-side Validation ---
        if (!username || !email || !password || !password2) {
            alert("Username, Email, Password, and Password Confirmation are required!");
      return;
    }

        if (password !== password2) {
            alert("Passwords do not match!");
      return;
    }

        if (password.length < MIN_PASSWORD_LENGTH) {
            alert(`Password must be at least ${MIN_PASSWORD_LENGTH} characters long!`);
      return;
    }

        // Optional: Validate age if entered
        let ageValue: number | null = null;
        if (age) {
            const parsedAge = parseInt(age, 10);
            if (isNaN(parsedAge) || parsedAge <= 0) {
                alert("Please enter a valid age.");
                return;
            }
            // <<< REMOVED: Client-side age restriction (backend should handle if needed) >>>
            // if (parsedAge < 16) { ... }
            ageValue = parsedAge;
        }
        // --- End Validation ---

        // --- Get CSRF Token ---
        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Sign-up failed: Could not verify security token. Please refresh and try again.");
            return;
        }
        // --- End CSRF Token ---

        // --- Construct Payload ---
        const payload: any = { // Use 'any' for simplicity or define a specific type
            username,
            email,
            password,
            password2, // Send confirmation password to backend validator
        };
        if (first_name) payload.first_name = first_name;
        if (last_name) payload.last_name = last_name;
        if (ageValue !== null) payload.age = ageValue;
        // NOTE: We are NOT sending 'type'. Backend defaults to 'US'.
        // --- End Payload ---


        try {
            // <<< CHANGE: Update API endpoint and include CSRF token >>>
            const response = await fetch("/api/auth/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken, // Include CSRF token
      },
                body: JSON.stringify(payload),
                // credentials: "include", // Usually not needed for public registration
            });

    if (response.ok) {
                alert("Sign-up successful! Please log in.");
                navigate("/login"); // Redirect to login page on success
    } else {
                // <<< CHANGE: Improved error handling >>>
                let errorMsg = "Sign-up failed!";
                try {
      const data = await response.json();
                    // Flatten potential nested errors (DRF validation errors can be complex)
                    if (typeof data === 'object' && data !== null) {
                        errorMsg = Object.entries(data)
                            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('\n');
                    } else if (data.error) {
                         errorMsg = data.error;
                    }
                } catch(e) {
                    // Ignore if response is not JSON or parsing fails
                    errorMsg = `Sign-up failed with status: ${response.status}`;
                }
                alert(errorMsg);
    }
  } catch (error) {
    console.error("Error during sign-up:", error);
            alert("An error occurred during sign-up. Please check your network connection and try again.");
  }
  
  };

  return (
        // Using previous CSS classes assuming they style a centered card
        <div className="flex items-center justify-center h-screen bg-gradient-to-r from-teal-500 to-cyan-500"> {/* Example Tailwind classes */}
      <motion.div
                className="bg-white p-8 rounded-2xl shadow-xl w-96 text-center" // Example Tailwind classes
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
                <h1 className="text-3xl font-bold text-teal-900 mb-6">Create Account</h1> {/* Example Tailwind classes */}
      
                {/* Username (Required) */}
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="text"
          name="username"
                    placeholder="Username *"
          value={formData.username}
          onChange={handleChange}
                    required // HTML5 required attribute
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
                />

                {/* Email (Required) */}
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="email"
          name="email"
                    placeholder="Email *"
          value={formData.email}
          onChange={handleChange}
                    required
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
        />

                {/* Password (Required) */}
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="password"
          name="password"
                    placeholder="Password *"
          value={formData.password}
          onChange={handleChange}
                    required
                    minLength={MIN_PASSWORD_LENGTH} // HTML5 minLength attribute
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
        />

                {/* Confirm Password (Required) */}
                <motion.input
                    whileFocus={{ scale: 1.05 }}
                    type="password"
                    name="password2"
                    placeholder="Confirm Password *"
                    value={formData.password2}
                    onChange={handleChange}
                    required
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
                />

                {/* First Name (Optional) */}
                <motion.input
                    whileFocus={{ scale: 1.05 }}
                    type="text"
                    name="first_name"
                    placeholder="First Name (Optional)"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
                />

                {/* Last Name (Optional) */}
                <motion.input
                    whileFocus={{ scale: 1.05 }}
                    type="text"
                    name="last_name"
                    placeholder="Last Name (Optional)"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
                />

                {/* Age (Optional) */}
                <motion.input
                    whileFocus={{ scale: 1.05 }}
                    type="number" // Use type="number" for age
                    name="age"
                    placeholder="Age (Optional)"
                    value={formData.age}
                    onChange={handleChange}
                    min="1" // Optional: HTML5 validation for positive number
                    className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition-all" // Example Tailwind classes
                />

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSignUp}
                    className="w-full bg-teal-700 text-white py-3 rounded-lg font-semibold hover:bg-teal-800 transition-all" // Example Tailwind classes
        >
          Sign Up
        </motion.button>

                 {/* Link to Login Page */}
                 <div className="login-link mt-4"> {/* Added margin-top */}
                    <p className="text-sm text-gray-600">Already have an account?</p> {/* Example Tailwind classes */}
                    <button onClick={() => navigate("/login")} className="text-teal-600 hover:text-teal-800 font-semibold text-sm"> {/* Example Tailwind classes */}
                        Log In
                    </button>
                </div>
      </motion.div>
    </div>
  );
};

export default SignUpPage;
