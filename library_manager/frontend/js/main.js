// JavaScript to handle button click and redirect to login page
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script loaded!");
    document.getElementById("startButton").addEventListener('click', function(){
        window.location.href = "/library_manager/frontend/html/login.html";  // 
    });
});
