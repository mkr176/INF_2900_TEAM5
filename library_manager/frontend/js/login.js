document.getElementById("loginButton").addEventListener('click', function(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if(username && password){
        alert("Logging in...");
    } else {
        alert("Both username and password are required")
    }
});

document.getElementById("signButton").addEventListener('click', function(){
    window.location.href = 'library_manager/frontend/html/sign.html'; //add url for sign.html
});