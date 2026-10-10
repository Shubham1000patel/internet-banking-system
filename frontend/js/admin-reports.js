const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const reportMessage = document.getElementById("reportMessage");
const reportTableBody = document.getElementById(
    "financialReportsTableBody"
);

function getAdminToken() {
    return sessionStorage.getItem("admin_access_token");
}

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

function formatCount(value) {
    const number = Number(value);

    if (!Number.isSafeInteger(number) || number < 0) {
        return "Check count data";
    }

    return number.toLocaleString("en-IN");
}

function formatReportAmount(value) {
    if (value === null || value === undefined || value === "") {
        return '<span class="warning-text">Amount unavailable</span>';
    }

    const amount = String(value).trim();

    if (!/^\d+(?:\.\d+)?$/.test(amount)) {
        return '<span class="warning-text">Invalid amount</span>';
    }

    const digitsOnly = amount.replace(".", "");

    if (digitsOnly.length > 18) {
        return '<span class="warning-text">Check amount data</span>';
    }

    return `₹${escapeHtml(amount)}`;
}

function logoutAdmin() {
    sessionStorage.removeItem("admin_access_token");
    sessionStorage.removeItem("admin_token_type");
    sessionStorage.removeItem("admin_id");
    sessionStorage.removeItem("admin_name");
    sessionStorage.removeItem("admin_email");
    sessionStorage.removeItem("admin_role");

    window.location.replace("admin-login.html");
}

function normalizeReportData(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (data && Array.isArray(data.reports)) {
        return data.reports;
    }

    throw new Error("Unexpected response format from the financial reports API.");
}

async function loadFinancialReports() {
    const token = getAdminToken();

    if (!token) {
        window.location.replace("admin-login.html");
        return;
    }

    reportMessage.textContent = "Loading financial reports...";
    reportMessage.style.color = "#64748b";

    reportTableBody.innerHTML = `
        <tr>
            <td colspan="3">Loading report data...</td>
        </tr>
    `;

    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/admin/reports/financial`,
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
                "Unable to load financial reports."
            );
        }

        const reports = normalizeReportData(data);

        renderFinancialReports(reports);

        reportMessage.textContent = reports.length
            ? "Financial reports loaded successfully."
            : "No financial report data found.";

        reportMessage.style.color = reports.length
            ? "#166534"
            : "#64748b";

    } catch (error) {
        reportMessage.textContent =
            error.message || "Unable to connect to the backend.";

        reportMessage.style.color = "#b91c1c";

        document.getElementById("transactionTypeCount").textContent = "—";
        document.getElementById("totalTransactions").textContent = "—";
        document.getElementById("totalReportAmount").textContent = "—";

        reportTableBody.innerHTML = `
            <tr>
                <td colspan="3">Unable to display financial reports.</td>
            </tr>
        `;
    }
}

function renderFinancialReports(reports) {
    document.getElementById("transactionTypeCount").textContent =
        reports.length.toLocaleString("en-IN");

    let totalTransactions = 0;
    let validCounts = true;

    for (const report of reports) {
        const count = Number(report.transaction_count);

        if (!Number.isSafeInteger(count) || count < 0) {
            validCounts = false;
            break;
        }

        totalTransactions += count;

        if (!Number.isSafeInteger(totalTransactions)) {
            validCounts = false;
            break;
        }
    }

    document.getElementById("totalTransactions").textContent =
        validCounts
            ? totalTransactions.toLocaleString("en-IN")
            : "Check count data";

    // Do not add money amounts using floating-point arithmetic.
    // The individual report amounts are displayed only after validation.
    document.getElementById("totalReportAmount").textContent =
        "See breakdown";

    if (reports.length === 0) {
        reportTableBody.innerHTML = `
            <tr>
                <td colspan="3">No report data available.</td>
            </tr>
        `;
        return;
    }

    reportTableBody.innerHTML = reports.map((report) => `
        <tr>
            <td>
                <span class="type-badge">
                    ${escapeHtml(report.transaction_type ?? "Unknown")}
                </span>
            </td>

            <td>${formatCount(report.transaction_count)}</td>

            <td>${formatReportAmount(report.total_amount)}</td>
        </tr>
    `).join("");
}

document
    .getElementById("refreshReports")
    .addEventListener("click", loadFinancialReports);

document
    .getElementById("adminLogoutButton")
    .addEventListener("click", function (event) {
        event.preventDefault();
        logoutAdmin();
    });

loadFinancialReports();
