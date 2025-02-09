document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("signUpButton").addEventListener('click', function() {
        const fullName = document.getElementById("fullName").value.trim();
        const username = document.getElementById("username").value.trim();
        const birthDate = document.getElementById("birthDate").value;
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (!fullName || !username || !birthDate || !email || !password) {
            alert("All fields are required!");
            return;
        }

        if (password.length < 6) {
            alert("Password must be at least 6 characters long!");
            return;
        }

        // Send data to backend (if needed)
        console.log("User Data:", { fullName, username, birthDate, email });

        alert("Sign-up successful!");
        window.location.href = "/library_manager/frontend/html/login.html";
    });
});