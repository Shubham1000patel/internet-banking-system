
const billAccount = document.getElementById("billAccount");
const billPaymentForm = document.getElementById("billPaymentForm");
const billType = document.getElementById("billType");
const consumerNumber = document.getElementById("consumerNumber");
const providerName = document.getElementById("providerName");
const billAmount = document.getElementById("billAmount");
const payBillButton = document.getElementById("payBillButton");
const billPaymentMessage = document.getElementById("billPaymentMessage");
const billPaymentsBody = document.getElementById("billPaymentsBody");
const refreshBillPayments = document.getElementById("refreshBillPayments");

function showMessage(message, isError = false) {
    billPaymentMessage.textContent = message;
    billPaymentMessage.style.color = isError ? "red" : "green";
}

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "—";
    row.appendChild(cell);
}

function formatDate(value) {
    if (!value) return "—";

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? String(value)
        : date.toLocaleString();
}

function renderPaymentHistory(payments) {
    billPaymentsBody.replaceChildren();

    if (!Array.isArray(payments) || payments.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 5;
        cell.textContent = "No bill payments found.";
        row.appendChild(cell);
        billPaymentsBody.appendChild(row);
        return;
    }

    payments.forEach(payment => {
        const row = document.createElement("tr");

        addCell(row, formatDate(payment.payment_date));
        addCell(row, payment.bill_payment_id);
        addCell(row, payment.bill_type);
        addCell(row, `₹${payment.amount ?? "0.00"}`);
        addCell(row, payment.status);

        billPaymentsBody.appendChild(row);
    });
}

async function loadAccounts() {
    billAccount.innerHTML =
        '<option value="">Loading accounts...</option>';

    try {
        const accounts = await apiRequest("/accounts");

        billAccount.innerHTML =
            '<option value="">Select an account</option>';

        accounts.forEach(account => {
            const option = document.createElement("option");

            option.value = account.account_number;
            option.textContent =
                `${account.account_type} - ${account.account_number} ` +
                `(₹${account.balance})`;

            if (account.status !== "ACTIVE") {
                option.disabled = true;
            }

            billAccount.appendChild(option);
        });

        if (accounts.length === 0) {
            billAccount.innerHTML =
                '<option value="">No accounts available</option>';
        }
    } catch (error) {
        billAccount.innerHTML =
            '<option value="">Could not load accounts</option>';
        showMessage(error.message, true);
    }
}

async function loadBillPaymentHistory() {
    billPaymentsBody.innerHTML =
        '<tr><td colspan="5">Loading payment history...</td></tr>';

    try {
        const payments = await apiRequest("/bill-payments");
        renderPaymentHistory(payments);
    } catch (error) {
        billPaymentsBody.innerHTML =
            '<tr><td colspan="5">Could not load payment history.</td></tr>';

        showMessage(error.message, true);
    }
}

billPaymentForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const accountNumber = billAccount.value;
    const selectedBillType = billType.value;
    const billNumber = consumerNumber.value.trim();
    const provider = providerName.value.trim();
    const amount = Number(billAmount.value);

    if (!accountNumber || !selectedBillType || !billNumber || !provider) {
        showMessage("Please complete all bill details.", true);
        return;
    }

    if (!Number.isFinite(amount) || amount <= 0) {
        showMessage("Enter an amount greater than ₹0.", true);
        return;
    }

    payBillButton.disabled = true;
    showMessage("Processing bill payment...");

    try {
        const result = await apiRequest("/bill-payments", {
            method: "POST",
            body: JSON.stringify({
                account_number: accountNumber,
                bill_type: selectedBillType,
                bill_number: billNumber,
                provider_name: provider,
                amount: amount
            })
        });

        showMessage(
            result.message || "Bill payment completed successfully."
        );

        billPaymentForm.reset();

        await Promise.all([
            loadAccounts(),
            loadBillPaymentHistory()
        ]);
    } catch (error) {
        showMessage(error.message || "Bill payment failed.", true);
    } finally {
        payBillButton.disabled = false;
    }
});

refreshBillPayments.addEventListener("click", loadBillPaymentHistory);

async function initializeBillPaymentsPage() {
    await Promise.all([
        loadAccounts(),
        loadBillPaymentHistory()
    ]);
}

initializeBillPaymentsPage();