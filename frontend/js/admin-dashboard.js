const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const dashboardMessage = document.getElementById("dashboardMessage");

function getAdminToken() {
    return sessionStorage.getItem("admin_access_token");
}

function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 2
    }).format(number);
}

function formatCurrency(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(number);
}

async function adminApiRequest(endpoint) {
    const token = getAdminToken();

    if (!token) {
        window.location.replace("admin-login.html");
        throw new Error("Admin session not found. Please sign in.");
    }

    const response = await fetch(
        `${ADMIN_API_BASE_URL}${endpoint}`,
        {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Accept": "application/json"
            }
        }
    );

    const data = await response.json().catch(() => ({}));

    if (response.status === 401 || response.status === 403) {
        sessionStorage.removeItem("admin_access_token");
        sessionStorage.removeItem("admin_token_type");
        sessionStorage.removeItem("admin_id");
        sessionStorage.removeItem("admin_name");
        sessionStorage.removeItem("admin_email");
        sessionStorage.removeItem("admin_role");

        window.location.replace("admin-login.html");

        throw new Error("Your admin session has expired or is not authorized.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || "Unable to load admin dashboard."
        );
    }

    return data;
}

function displayAdminProfile() {
    const name = sessionStorage.getItem("admin_name") || "Administrator";
    const email = sessionStorage.getItem("admin_email") || "";
    const role = sessionStorage.getItem("admin_role") || "ADMIN";

    document.getElementById("adminWelcome").textContent = `Welcome, ${name}`;
    document.getElementById("adminEmailDisplay").textContent = email;
    document.getElementById("adminRoleDisplay").textContent = role;
}

async function loadAdminDashboard() {
    dashboardMessage.textContent = "Loading dashboard...";
    dashboardMessage.style.color = "#64748b";

    try {
        const data = await adminApiRequest("/admin/dashboard");

        document.getElementById("totalCustomers").textContent =
            formatNumber(data.total_customers);

        document.getElementById("totalAccounts").textContent =
            formatNumber(data.total_accounts);

        document.getElementById("totalTransactions").textContent =
            formatNumber(data.total_transactions);

        // The financial report endpoint will provide more detail later.
        document.getElementById("financialSummary").textContent =
            formatCurrency(data.total_transaction_amount);

        dashboardMessage.textContent = "";
    } catch (error) {
        dashboardMessage.textContent = error.message;
        dashboardMessage.style.color = "#b91c1c";
    }
}

document.getElementById("refreshDashboard").addEventListener("click", () => {
    loadAdminDashboard();
});

document.getElementById("adminLogoutButton").addEventListener("click", () => {
    sessionStorage.removeItem("admin_access_token");
    sessionStorage.removeItem("admin_token_type");
    sessionStorage.removeItem("admin_id");
    sessionStorage.removeItem("admin_name");
    sessionStorage.removeItem("admin_email");
    sessionStorage.removeItem("admin_role");

    window.location.replace("admin-login.html");
});

displayAdminProfile();
loadAdminDashboard();

