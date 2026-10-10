
const statementAccount = document.getElementById("statementAccount");
const statementForm = document.getElementById("statementForm");
const startDate = document.getElementById("startDate");
const endDate = document.getElementById("endDate");
const statementMessage = document.getElementById("statementMessage");
const statementBody = document.getElementById("statementBody");
const downloadStatement = document.getElementById("downloadStatement");

let displayedTransactions = [];

function showStatementMessage(message, isError = false) {
    statementMessage.textContent = message;
    statementMessage.style.color = isError ? "red" : "green";
}

function getTransactionDate(transaction) {
    const value =
        transaction.transaction_date ??
        transaction.created_at ??
        transaction.date;

    if (!value) return null;

    const date = new Date(value);

    return Number.isNaN(date.getTime()) ? null : date;
}

function renderStatement(transactions) {
    statementBody.replaceChildren();

    if (transactions.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 5;
        cell.textContent = "No transactions found for this date range.";
        row.appendChild(cell);
        statementBody.appendChild(row);
        return;
    }

    transactions.forEach(transaction => {
        const row = document.createElement("tr");
        const date = getTransactionDate(transaction);

        const values = [
            date ? date.toLocaleString() : "—",
            transaction.transaction_id ?? "—",
            transaction.transaction_type ?? "—",
            `₹${transaction.amount ?? "0.00"}`,
            transaction.status ?? "—"
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = String(value);
            row.appendChild(cell);
        });

        statementBody.appendChild(row);
    });
}

async function loadStatementAccounts() {
    try {
        const accounts = await apiRequest("/accounts");

        statementAccount.innerHTML =
            '<option value="">Select an account</option>';

        accounts.forEach(account => {
            const option = document.createElement("option");
            option.value = account.account_number;
            option.textContent =
                `${account.account_type} - ${account.account_number}`;

            statementAccount.appendChild(option);
        });

        if (accounts.length === 0) {
            statementAccount.innerHTML =
                '<option value="">No accounts available</option>';
        }
    } catch (error) {
        statementAccount.innerHTML =
            '<option value="">Could not load accounts</option>';
        showStatementMessage(error.message, true);
    }
}

statementForm.addEventListener("submit", async event => {
    event.preventDefault();

    const accountNumber = statementAccount.value;
    const from = startDate.value;
    const to = endDate.value;

    if (!accountNumber || !from || !to) {
        showStatementMessage("Please complete all fields.", true);
        return;
    }

    if (from > to) {
        showStatementMessage(
            "From Date cannot be later than To Date.",
            true
        );
        return;
    }

    showStatementMessage("Loading statement...");
    displayedTransactions = [];
    downloadStatement.disabled = true;

    try {
        const transactions = await apiRequest(
            `/accounts/${encodeURIComponent(accountNumber)}/transactions`
        );

        if (!Array.isArray(transactions)) {
            throw new Error("Unexpected transaction response.");
        }

        displayedTransactions = transactions.filter(transaction => {
            const date = getTransactionDate(transaction);

            if (!date) return false;

            const dateOnly =
                `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

            return dateOnly >= from && dateOnly <= to;
        });

        renderStatement(displayedTransactions);
        downloadStatement.disabled = displayedTransactions.length === 0;

        showStatementMessage(
            `Statement generated: ${displayedTransactions.length} transaction(s).`
        );
    } catch (error) {
        statementBody.innerHTML =
            '<tr><td colspan="5">Could not load the statement.</td></tr>';
        showStatementMessage(error.message, true);
    }
});

downloadStatement.addEventListener("click", () => {
    if (displayedTransactions.length === 0) return;

    const escapeCsv = value =>
        `"${String(value ?? "").replace(/"/g, '""')}"`;

    const rows = [
        ["Date", "Transaction ID", "Type", "Amount", "Status"],
        ...displayedTransactions.map(transaction => {
            const date = getTransactionDate(transaction);

            return [
                date ? date.toISOString() : "",
                transaction.transaction_id ?? "",
                transaction.transaction_type ?? "",
                transaction.amount ?? "",
                transaction.status ?? ""
            ];
        })
    ];

    const csv = rows.map(row => row.map(escapeCsv).join(",")).join("\r\n");
    const blob = new Blob(["\uFEFF" + csv], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "account_statement.csv";
    link.click();

    URL.revokeObjectURL(url);
});

loadStatementAccounts();