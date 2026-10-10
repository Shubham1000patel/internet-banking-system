
const registerForm = document.getElementById("registerForm");
const registerButton = document.getElementById("registerButton");
const registerMessage = document.getElementById("registerMessage");
const dateOfBirthInput = document.getElementById("date_of_birth");

function showRegisterMessage(message, isError = false) {
    registerMessage.textContent = message;
    registerMessage.style.color = isError ? "red" : "green";
}

// Prevent selecting a future date of birth.
dateOfBirthInput.max = new Date().toLocaleDateString("en-CA");

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const address = document.getElementById("address").value.trim();
    const dateOfBirth = dateOfBirthInput.value;
    const password = document.getElementById("password").value;
    const confirmPassword =
        document.getElementById("confirmPassword").value;

    if (!name || !email || !phone || !address || !dateOfBirth || !password) {
        showRegisterMessage("Please complete all required fields.", true);
        return;
    }

    if (password.length < 8) {
        showRegisterMessage(
            "Password must contain at least 8 characters.",
            true
        );
        return;
    }

    if (password !== confirmPassword) {
        showRegisterMessage("Passwords do not match.", true);
        return;
    }

    if (dateOfBirth > dateOfBirthInput.max) {
        showRegisterMessage("Date of birth cannot be in the future.", true);
        return;
    }

    registerButton.disabled = true;
    showRegisterMessage("Creating your customer account...");

    try {
        const result = await apiRequest("/auth/register", {
            method: "POST",
            body: JSON.stringify({
                name: name,
                email: email,
                phone: phone,
                address: address,
                date_of_birth: dateOfBirth,
                password: password
            })
        });

        showRegisterMessage(
            `${result.message} Your Customer ID is ${result.customer_id}. Redirecting to login...`
        );

        registerForm.reset();

        // Give the customer time to read their ID before navigating.
        setTimeout(() => {
            window.location.href = "index.html";
        }, 2500);

    } catch (error) {
        showRegisterMessage(
            error.message || "Registration failed. Please try again.",
            true
        );
    } finally {
        registerButton.disabled = false;
    }
});