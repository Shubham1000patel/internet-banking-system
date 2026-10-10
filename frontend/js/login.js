
const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("loginButton");
const message = document.getElementById("message");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    message.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Signing in...";

    try {
        const result = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                login_id: email,
                password: password
            })
        });

        if (!result.access_token) {
            throw new Error("The server did not return an access token.");
        }

        // Temporary demo storage; we'll improve token handling later.
        sessionStorage.setItem("access_token", result.access_token);

        message.textContent = "Login successful! Opening dashboard...";
        message.style.color = "green";

        window.location.href = "dashboard.html";

    } catch (error) {
        message.textContent = error.message || "Login failed. Please try again.";
        message.style.color = "red";

    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Login Securely";
    }
});