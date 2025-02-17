document.getElementById("loginButton").addEventListener('click', function(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if(username && password){
        alert("Logging in...");
    } else {
        alert("Both username and password are required")
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const signButton = document.getElementById("signButton");

    if (signButton) {
        signButton.addEventListener('click', function () {
            console.log("Redirecting to sign up page...");
            window.location.href = '/library_manager/frontend/html/sign.html';
        });
    } else {
        console.error("El botón signButton no se encontró en el DOM.");
    }
});