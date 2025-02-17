document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("signButton").addEventListener('click', function() {
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

        const birthDateObj = new Date(birthDate);
        const today = new Date();
        const age = today.getFullYear() - birthDateObj.getFullYear();
        const month = today.getMonth() - birthDateObj.getMonth();
        const day = today.getDate() - birthDateObj.getDate();

        if(month < 0 || (month === 0 && day < 0)){
            age--;
        }
        
        if (age < 16) {
            alert("You must be at least 16 years old to sign up!");
            return;
        }

        // Send data to backend (if needed)
        console.log("User Data:", { fullName, username, birthDate, email });

        //add here some code to send the data to the backend (this is a simulation)
        const userExists = true;

        if (userExists) {
            alert("User already exists!");
            window.location.href = "/library_manager/frontend/html/startpage.html";
        } else {
            alert("Sign-up failed. Please try again.");
        }
    });
});