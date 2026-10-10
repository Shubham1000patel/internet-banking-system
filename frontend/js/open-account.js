
const openAccountForm = document.getElementById("openAccountForm");
const accountType = document.getElementById("accountType");
const initialBalance = document.getElementById("initialBalance");
const openAccountButton = document.getElementById("openAccountButton");
const accountMessage = document.getElementById("accountMessage");

if (!sessionStorage.getItem("access_token")) {
    window.location.replace("index.html");
}

async function checkAvailableAccounts() {
    try {
        const accounts = await apiRequest("/accounts");

        const hasSavings = accounts.some(
            account => account.account_type === "SAVINGS"
        );

        const hasCurrent = accounts.some(
            account => account.account_type === "CURRENT"
        );

        // Disable account types that already exist
        for (const option of accountType.options) {
            if (option.value === "SAVINGS" && hasSavings) {
                option.disabled = true;
            }

            if (option.value === "CURRENT" && hasCurrent) {
                option.disabled = true;
            }
        }

        if (hasSavings && hasCurrent) {
            accountMessage.style.color = "#b91c1c";
            accountMessage.textContent =
                "You already have both Savings and Current accounts.";

            openAccountButton.disabled = true;
        }
    } catch (error) {
        accountMessage.style.color = "#b91c1c";
        accountMessage.textContent =
            error.message || "Unable to check your existing accounts.";

        openAccountButton.disabled = true;
    }
}

openAccountForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    accountMessage.textContent = "";
    openAccountButton.disabled = true;
    openAccountButton.textContent = "Opening Account...";

    try {
        const response = await apiRequest("/accounts", {
            method: "POST",
            body: JSON.stringify({
                account_type: accountType.value,
                initial_balance: Number(initialBalance.value)
            })
        });

        accountMessage.style.color = "green";
        accountMessage.textContent =
            `Account created successfully! Account number: ${response.account_number}`;

        openAccountForm.reset();
        initialBalance.value = "0.00";

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 2000);

    } catch (error) {
        accountMessage.style.color = "#b91c1c";
        accountMessage.textContent =
            error.message || "Unable to create account.";

        openAccountButton.disabled = false;
        openAccountButton.textContent = "Open Account";
    }
});

checkAvailableAccounts();