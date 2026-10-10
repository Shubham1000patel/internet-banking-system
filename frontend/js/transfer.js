
const transferForm = document.getElementById("transferForm");
const fromAccount = document.getElementById("fromAccount");
const toAccount = document.getElementById("toAccount");
const amount = document.getElementById("amount");
const transferButton = document.getElementById("transferButton");
const transferMessage = document.getElementById("transferMessage");

if (!sessionStorage.getItem("access_token")) {
    window.location.replace("index.html");
}

function showMessage(message, isSuccess = false) {
    transferMessage.textContent = message;
    transferMessage.style.color = isSuccess ? "green" : "#b91c1c";
}

async function loadAccounts() {
    try {
        const accounts = await apiRequest("/accounts");

        fromAccount.replaceChildren();

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select your account";
        fromAccount.appendChild(placeholder);

        for (const account of accounts) {
            const option = document.createElement("option");
            option.value = account.account_number;
            option.textContent =
                `${account.account_type} - XXXX ${account.account_number.slice(-4)} - ₹${account.balance}`;

            fromAccount.appendChild(option);
        }

        if (accounts.length === 0) {
            showMessage("You don't have an account available for transfers.");
            transferButton.disabled = true;
        }
    } catch (error) {
        showMessage(error.message || "Unable to load your accounts.");
        transferButton.disabled = true;
    }
}

transferForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const source = fromAccount.value;
    const destination = toAccount.value.trim();
    const transferAmount = Number(amount.value);

    if (!source) {
        showMessage("Please select your source account.");
        return;
    }

    if (!/^\d{12}$/.test(destination)) {
        showMessage("Enter a valid 12-digit recipient account number.");
        return;
    }

    if (source === destination) {
        showMessage("You cannot transfer money to the same account.");
        return;
    }

    if (!Number.isFinite(transferAmount) || transferAmount <= 0) {
        showMessage("Transfer amount must be greater than zero.");
        return;
    }

    transferButton.disabled = true;
    transferButton.textContent = "Processing Transfer...";
    showMessage("");

    try {
        // Use your existing FastAPI transfer endpoint.
       const idempotencyKey = crypto.randomUUID();

       const result = await apiRequest("/transfers", {
            method: "POST",
            headers: {
                "Idempotency-Key": idempotencyKey
            },
            body: JSON.stringify({
                from_account: source,
                to_account: destination,
                amount: transferAmount
            })
        });

        showMessage(
            result.message || "Transfer completed successfully.",
            true
        );

        transferForm.reset();
        await loadAccounts();

    } catch (error) {
        showMessage(error.message || "Transfer failed.");
    } finally {
        transferButton.disabled = false;
        transferButton.textContent = "Transfer Money";
    }
});

loadAccounts();