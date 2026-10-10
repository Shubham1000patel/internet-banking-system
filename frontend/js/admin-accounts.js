const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const accountsTableBody = document.getElementById("accountsTableBody");
const accountMessage = document.getElementById("accountMessage");
const accountCount = document.getElementById("accountCount");

let allAccounts = [];

// Get the logged-in admin's token.
function getAdminToken() {
    return sessionStorage.getItem("admin_access_token");
}

// Safely display API values in HTML.
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

// Format account creation date.
function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleString("en-IN");
}

// Validate balances before displaying them as currency.
function formatBalance(value) {
    if (value === null || value === undefined || value === "") {
        return '<span class="warning-text">Balance unavailable</span>';
    }

    const balance = String(value).trim();

    const decimalPattern = /^-?\d+(?:\.\d+)?$/;

    if (!decimalPattern.test(balance)) {
        return '<span class="warning-text">Invalid balance value</span>';
    }

    const digitsOnly = balance.replace(/[-.]/g, "");

    // Do not display suspicious negative or excessively long balances
    // as trustworthy monetary values.
    if (digitsOnly.length > 18 || balance.startsWith("-")) {
        return `
            <span class="warning-text"
                  title="${escapeHtml(balance)}">
                Check balance data
            </span>
        `;
    }

    // Preserve the decimal representation returned by the backend.
    return `₹${escapeHtml(balance)}`;
}

// Return the CSS class for an account status.
function getStatusClass(status) {
    const normalizedStatus = String(status || "").toUpperCase();

    if (normalizedStatus === "ACTIVE") {
        return "status-active";
    }

    if (normalizedStatus === "BLOCKED") {
        return "status-blocked";
    }

    return "status-other";
}

// Clear admin session and redirect to login.
function logoutAdmin() {
    sessionStorage.removeItem("admin_access_token");
    sessionStorage.removeItem("admin_token_type");
    sessionStorage.removeItem("admin_id");
    sessionStorage.removeItem("admin_name");
    sessionStorage.removeItem("admin_email");
    sessionStorage.removeItem("admin_role");

    window.location.replace("admin-login.html");
}

// Load accounts from the backend.
async function loadAccounts() {
    accountMessage.textContent = "Loading accounts...";
    accountMessage.style.color = "#64748b";

    accountsTableBody.innerHTML = `
        <tr>
            <td colspan="7">Loading accounts...</td>
        </tr>
    `;

    const token = getAdminToken();

    if (!token) {
        window.location.replace("admin-login.html");
        return;
    }

    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/admin/accounts`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json"
                }
            }
        );

        const data = await response.json().catch(() => null);

        if (response.status === 401 || response.status === 403) {
            logoutAdmin();
            return;
        }

        if (!response.ok) {
            throw new Error(
                data?.detail ||
                data?.message ||
                "Unable to load accounts."
            );
        }

        // Support a list, an object containing an accounts list,
        // or a single account object.
        if (Array.isArray(data)) {
            allAccounts = data;
        } else if (data && Array.isArray(data.accounts)) {
            allAccounts = data.accounts;
        } else if (
            data &&
            typeof data === "object" &&
            "account_number" in data
        ) {
            allAccounts = [data];
        } else {
            throw new Error(
                "Unexpected response format from /admin/accounts."
            );
        }

        renderAccounts();

        accountMessage.textContent =
            allAccounts.length === 0
                ? "No accounts found."
                : "Accounts loaded successfully.";

        accountMessage.style.color =
            allAccounts.length === 0 ? "#64748b" : "#166534";

    } catch (error) {
        accountMessage.textContent =
            error.message || "Unable to connect to the backend.";

        accountMessage.style.color = "#b91c1c";

        accountsTableBody.innerHTML = `
            <tr>
                <td colspan="7">Unable to display accounts.</td>
            </tr>
        `;

        accountCount.textContent = "0";
    }
}

// Search and filter accounts, then display them in the table.
function renderAccounts() {
    const searchText = document
        .getElementById("accountSearch")
        .value.trim()
        .toLowerCase();

    const typeFilter = document
        .getElementById("accountTypeFilter")
        .value;

    const statusFilter = document
        .getElementById("accountStatusFilter")
        .value;

    const filteredAccounts = allAccounts.filter((account) => {
        const accountNumber = String(
            account.account_number ?? ""
        ).toLowerCase();

        const customerId = String(
            account.customer_id ?? ""
        ).toLowerCase();

        const accountType = String(
            account.account_type ?? ""
        ).toUpperCase();

        const status = String(
            account.status ?? ""
        ).toUpperCase();

        const matchesSearch =
            accountNumber.includes(searchText) ||
            customerId.includes(searchText);

        const matchesType =
            !typeFilter || accountType === typeFilter;

        const matchesStatus =
            !statusFilter || status === statusFilter;

        return matchesSearch && matchesType && matchesStatus;
    });

    accountCount.textContent = String(filteredAccounts.length);

    if (filteredAccounts.length === 0) {
        accountsTableBody.innerHTML = `
            <tr>
                <td colspan="7">No matching accounts found.</td>
            </tr>
        `;

        return;
    }

    accountsTableBody.innerHTML = filteredAccounts.map((account) => {
        const status = String(
            account.status ?? "UNKNOWN"
        ).toUpperCase();

        const accountNumber = String(
            account.account_number ?? ""
        );

        const statusOptions = ["ACTIVE", "BLOCKED", "INACTIVE"];

        // Preserve an existing status even if it is not in our
        // standard options, so the current value is not hidden.
        if (status && !statusOptions.includes(status)) {
            statusOptions.push(status);
        }

        const optionsHtml = statusOptions.map((option) => {
            return `
                <option value="${escapeHtml(option)}"
                    ${status === option ? "selected" : ""}>
                    ${escapeHtml(option)}
                </option>
            `;
        }).join("");

        return `
            <tr>
                <td>${escapeHtml(accountNumber || "—")}</td>

                <td>${escapeHtml(account.customer_id ?? "—")}</td>

                <td>${escapeHtml(account.account_type ?? "—")}</td>

                <td>${formatBalance(account.balance)}</td>

                <td>
                    <span class="status ${getStatusClass(status)}">
                        ${escapeHtml(status)}
                    </span>
                </td>

                <td>${escapeHtml(formatDate(account.created_at))}</td>

                <td>
                    <select
                        class="account-status-select"
                        id="status-${escapeHtml(accountNumber)}"
                        aria-label="New status for account ${escapeHtml(accountNumber)}"
                    >
                        ${optionsHtml}
                    </select>

                    <button
                        type="button"
                        class="update-account-status"
                        data-account-number="${escapeHtml(accountNumber)}"
                    >
                        Update
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

// Update an account's status through the confirmed PUT endpoint.
accountsTableBody.addEventListener("click", async (event) => {
    const button = event.target.closest(".update-account-status");

    if (!button) {
        return;
    }

    const accountNumber = button.dataset.accountNumber;

    const select = document.getElementById(
        `status-${accountNumber}`
    );

    if (!select) {
        accountMessage.textContent = "Unable to find the status selector.";
        accountMessage.style.color = "#b91c1c";
        return;
    }

    const newStatus = select.value;

    const currentAccount = allAccounts.find(
        (account) =>
            String(account.account_number) === accountNumber
    );

    const currentStatus = String(
        currentAccount?.status ?? ""
    ).toUpperCase();

    if (newStatus === currentStatus) {
        accountMessage.textContent = "The account already has this status.";
        accountMessage.style.color = "#64748b";
        return;
    }

    const confirmed = confirm(
        `Change account ${accountNumber} status to ${newStatus}?`
    );

    if (!confirmed) {
        return;
    }

    const token = getAdminToken();

    if (!token) {
        window.location.replace("admin-login.html");
        return;
    }

    button.disabled = true;
    button.textContent = "Updating...";

    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/admin/accounts/${encodeURIComponent(accountNumber)}/status`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const data = await response.json().catch(() => ({}));

        if (response.status === 401 || response.status === 403) {
            logoutAdmin();
            return;
        }

        if (!response.ok) {
            throw new Error(
                data.detail ||
                data.message ||
                "Unable to update account status."
            );
        }

        accountMessage.textContent =
            data.message ||
            `Account ${data.account_number || accountNumber} status updated to ${data.status || newStatus}.`;

        accountMessage.style.color = "#166534";

        // Reload from the backend to show the saved status.
        await loadAccounts();

    } catch (error) {
        accountMessage.textContent =
            error.message || "Unable to update account status.";

        accountMessage.style.color = "#b91c1c";

    } finally {
        // The table may have been redrawn after a successful update.
        // Only restore the button if it still exists in the page.
        if (button.isConnected) {
            button.disabled = false;
            button.textContent = "Update";
        }
    }
});

// Refresh the account list.
document
    .getElementById("refreshAccounts")
    .addEventListener("click", loadAccounts);

// Search by account number or customer ID.
document
    .getElementById("accountSearch")
    .addEventListener("input", renderAccounts);

// Filter by account type.
document
    .getElementById("accountTypeFilter")
    .addEventListener("change", renderAccounts);

// Filter by account status.
document
    .getElementById("accountStatusFilter")
    .addEventListener("change", renderAccounts);

// Log out the administrator.
document
    .getElementById("adminLogoutButton")
    .addEventListener("click", logoutAdmin);

// Load accounts when the page opens.
loadAccounts();

