const accountSelect = document.getElementById("accountSelect");
const transactionTableBody = document.getElementById("transactionTableBody");
const transactionMessage = document.getElementById("transactionMessage");
const refreshTransactions = document.getElementById("refreshTransactions");

if (!sessionStorage.getItem("access_token")) {
    window.location.replace("index.html");
}

function formatMoney(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR"
    }).format(Number(value));
}

function formatDate(value) {
    if (!value) return "—";

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? String(value)
        : date.toLocaleString("en-IN");
}

function showMessage(message, isError = true) {
    transactionMessage.textContent = message;
    transactionMessage.style.color = isError ? "#b91c1c" : "#15803d";
}

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "—";
    row.appendChild(cell);
}

async function loadTransactions() {
    const accountNumber = accountSelect.value;

    transactionTableBody.replaceChildren();
    showMessage("");

    if (!accountNumber) {
        showMessage("Select an account to view transactions.");
        return;
    }

    refreshTransactions.disabled = true;

    try {
        const transactions = await apiRequest(
            `/accounts/${encodeURIComponent(accountNumber)}/transactions`
        );

        if (!Array.isArray(transactions) || transactions.length === 0) {
            const row = document.createElement("tr");
            addCell(row, "No transactions found.");
            const cell = row.querySelector("td");
            cell.colSpan = 5;
            transactionTableBody.appendChild(row);
            return;
        }

        for (const transaction of transactions) {
            const row = document.createElement("tr");

            addCell(row, formatDate(
                transaction.created_at ?? transaction.transaction_date
            ));
            addCell(row, transaction.transaction_id ?? transaction.id);
            addCell(row, transaction.transaction_type ?? transaction.type);
            addCell(row, formatMoney(transaction.amount));
            addCell(row, transaction.status);

            transactionTableBody.appendChild(row);
        }
    } catch (error) {
        showMessage(error.message || "Unable to load transactions.");

        const row = document.createElement("tr");
        addCell(row, "Could not load transactions.");
        row.querySelector("td").colSpan = 5;
        transactionTableBody.appendChild(row);
    } finally {
        refreshTransactions.disabled = false;
    }
}

async function loadAccounts() {
    try {
        const accounts = await apiRequest("/accounts");

        accountSelect.replaceChildren();

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select an account";
        accountSelect.appendChild(placeholder);

        for (const account of accounts) {
            const option = document.createElement("option");
            option.value = account.account_number;
            option.textContent =
                `${account.account_type} — XXXX ${account.account_number.slice(-4)}`;

            accountSelect.appendChild(option);
        }

        if (accounts.length === 0) {
            showMessage("No accounts are available.");
            transactionTableBody.replaceChildren();
            return;
        }

        await loadTransactions();
    } catch (error) {
        showMessage(error.message || "Unable to load your accounts.");
    }
}

accountSelect.addEventListener("change", loadTransactions);
refreshTransactions.addEventListener("click", loadTransactions);

loadAccounts();