const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const adminLoginForm = document.getElementById("adminLoginForm");
const adminEmail = document.getElementById("adminEmail");
const adminPassword = document.getElementById("adminPassword");
const adminLoginButton = document.getElementById("adminLoginButton");
const adminLoginMessage = document.getElementById("adminLoginMessage");

adminLoginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = adminEmail.value.trim();
    const password = adminPassword.value;

    adminLoginMessage.textContent = "";
    adminLoginButton.disabled = true;
    adminLoginButton.textContent = "Signing in...";

    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/admin/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.detail || data.message || "Admin login failed."
            );
        }

        if (!data.access_token) {
            throw new Error(
                "Login response did not contain an access token."
            );
        }

        // Keep admin session separate from customer session.
        sessionStorage.setItem("admin_access_token", data.access_token);
        sessionStorage.setItem("admin_token_type", data.token_type || "bearer");
        sessionStorage.setItem("admin_id", String(data.admin_id));
        sessionStorage.setItem("admin_name", data.name || "");
        sessionStorage.setItem("admin_email", data.email || "");
        sessionStorage.setItem("admin_role", data.role || "");

        adminLoginMessage.textContent =
            data.message || "Login successful. Opening admin dashboard...";

        adminLoginMessage.style.color = "green";

        window.location.href = "admin-dashboard.html";

    } catch (error) {
        adminLoginMessage.textContent =
            error.message || "Unable to connect to the server.";

        adminLoginMessage.style.color = "red";
    } finally {
        adminLoginButton.disabled = false;
        adminLoginButton.textContent = "Sign In to Admin Panel";
    }
});

