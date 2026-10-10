const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const transactionsTableBody = document.getElementById("transactionsTableBody");
const transactionMessage = document.getElementById("transactionMessage");
const transactionCount = document.getElementById("transactionCount");

let allTransactions = [];
let searchRequestId = 0;

// Get admin authentication token.
function getAdminToken() {
    return sessionStorage.getItem("admin_access_token");
}

// Escape values before inserting them into HTML.
function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (character) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}

// Format transaction dates.
function formatDate(value) {
    if (!value) return "—";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "—";

    return date.toLocaleString("en-IN");
}

// Format amounts without changing the original decimal precision.
function formatAmount(value) {
    if (value === null || value === undefined || value === "") {
        return '<span class="warning-text">Amount unavailable</span>';
    }

    const amount = String(value).trim();
    const decimalPattern = /^-?\d+(?:\.\d+)?$/;

    if (!decimalPattern.test(amount)) {
        return '<span class="warning-text">Invalid amount</span>';
    }

    const digitsOnly = amount.replace(/[-.]/g, "");

    if (digitsOnly.length > 18 || amount.startsWith("-")) {
        return `
            <span class="warning-text"
                  title="${escapeHtml(amount)}">
                Check amount data
            </span>
        `;
    }

    return `₹${escapeHtml(amount)}`;
}

// Assign a CSS class based on transaction status.
function getTransactionStatusClass(status) {
    const normalizedStatus = String(status || "").toUpperCase();

    if (["SUCCESS", "SUCCESSFUL", "COMPLETED"].includes(normalizedStatus)) {
        return "status-success";
    }

    if (["FAILED", "REJECTED", "CANCELLED"].includes(normalizedStatus)) {
        return "status-failed";
    }

    if (normalizedStatus === "PENDING") {
        return "status-pending";
    }

    return "status-other";
}

// Clear admin session and return to login.
function logoutAdmin() {
    sessionStorage.removeItem("admin_access_token");
    sessionStorage.removeItem("admin_token_type");
    sessionStorage.removeItem("admin_id");
    sessionStorage.removeItem("admin_name");
    sessionStorage.removeItem("admin_email");
    sessionStorage.removeItem("admin_role");

    window.location.replace("admin-login.html");
}

// Validate and normalize the API response.
function normalizeTransactions(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (data && Array.isArray(data.transactions)) {
        return data.transactions;
    }

    if (
        data &&
        typeof data === "object" &&
        "transaction_id" in data
    ) {
        return [data];
    }

    throw new Error("Unexpected transaction response from the backend.");
}

// Load transactions using the backend search endpoint.
async function loadTransactions() {
    const requestId = ++searchRequestId;
    const token = getAdminToken();

    if (!token) {
        window.location.replace("admin-login.html");
        return;
    }

    const accountNumber = document
        .getElementById("transactionSearch")
        .value.trim();

    const transactionType = document
        .getElementById("transactionTypeFilter")
        .value;

    const status = document
        .getElementById("transactionStatusFilter")
        .value;

    const params = new URLSearchParams();

    if (accountNumber) {
        params.set("account_number", accountNumber);
    }

    if (transactionType) {
        params.set("transaction_type", transactionType);
    }

    if (status) {
        params.set("status", status);
    }

    const queryString = params.toString();

    // If no filters are selected, load the full transaction list.
    const endpoint = queryString
        ? `${ADMIN_API_BASE_URL}/admin/transactions/search?${queryString}`
        : `${ADMIN_API_BASE_URL}/admin/transactions`;

    transactionMessage.textContent = "Loading transactions...";
    transactionMessage.style.color = "#64748b";

    transactionsTableBody.innerHTML = `
        <tr>
            <td colspan="8">Loading transactions...</td>
        </tr>
    `;

    try {
        const response = await fetch(endpoint, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Accept": "application/json"
            }
        });

        const data = await response.json().catch(() => null);

        // Ignore an older request if a newer search has started.
        if (requestId !== searchRequestId) return;

        if (response.status === 401 || response.status === 403) {
            logoutAdmin();
            return;
        }

        if (!response.ok) {
            throw new Error(
                data?.detail ||
                data?.message ||
                "Unable to load transactions."
            );
        }

        allTransactions = normalizeTransactions(data);

        renderTransactions(allTransactions);

        transactionMessage.textContent =
            allTransactions.length === 0
                ? "No transactions found."
                : `Loaded ${allTransactions.length} transaction(s).`;

        transactionMessage.style.color =
            allTransactions.length === 0 ? "#64748b" : "#166534";

    } catch (error) {
        if (requestId !== searchRequestId) return;

        transactionMessage.textContent =
            error.message || "Unable to connect to the backend.";

        transactionMessage.style.color = "#b91c1c";

        transactionsTableBody.innerHTML = `
            <tr>
                <td colspan="8">Unable to display transactions.</td>
            </tr>
        `;

        transactionCount.textContent = "0";
    }
}

// Render the transactions returned by the backend.
function renderTransactions(transactions) {
    transactionCount.textContent = String(transactions.length);

    if (transactions.length === 0) {
        transactionsTableBody.innerHTML = `
            <tr>
                <td colspan="8">No matching transactions found.</td>
            </tr>
        `;
        return;
    }

    transactionsTableBody.innerHTML = transactions.map((transaction) => {
        const status = String(
            transaction.status ?? "UNKNOWN"
        ).toUpperCase();

        return `
            <tr>
                <td>${escapeHtml(transaction.transaction_id ?? "—")}</td>
                <td>${escapeHtml(transaction.from_account ?? "—")}</td>
                <td>${escapeHtml(transaction.to_account ?? "—")}</td>
                <td>${escapeHtml(transaction.transaction_type ?? "—")}</td>
                <td>${formatAmount(transaction.amount)}</td>
                <td>
                    <span class="status ${getTransactionStatusClass(status)}">
                        ${escapeHtml(status)}
                    </span>
                </td>
                <td>${escapeHtml(transaction.description ?? "—")}</td>
                <td>${escapeHtml(formatDate(transaction.transaction_date))}</td>
            </tr>
        `;
    }).join("");
}

// Refresh all transactions.
document
    .getElementById("refreshTransactions")
    .addEventListener("click", loadTransactions);

// Search by account number.
document
    .getElementById("transactionSearch")
    .addEventListener("input", loadTransactions);

// Filter by transaction type.
document
    .getElementById("transactionTypeFilter")
    .addEventListener("change", loadTransactions);

// Filter by transaction status.
document
    .getElementById("transactionStatusFilter")
    .addEventListener("change", loadTransactions);

// Admin logout.
document
    .getElementById("adminLogoutButton")
    .addEventListener("click", logoutAdmin);

// Load transactions when the page opens.
loadTransactions();
