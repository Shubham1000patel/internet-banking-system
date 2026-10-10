const ADMIN_API_BASE_URL = "http://127.0.0.1:8000";

const customersTableBody = document.getElementById("customersTableBody");
const customerMessage = document.getElementById("customerMessage");
const customerSearch = document.getElementById("customerSearch");
const statusFilter = document.getElementById("statusFilter");
const customerCount = document.getElementById("customerCount");

let customers = [];

function getAdminToken() {
  return sessionStorage.getItem("admin_access_token");
}

function escapeHTML(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );
}

function showMessage(message, isError = false) {
  customerMessage.textContent = message;
  customerMessage.style.color = isError ? "#b91c1c" : "#166534";
}

async function adminRequest(endpoint, options = {}) {
  const token = getAdminToken();

  if (!token) {
    window.location.replace("admin-login.html");
    throw new Error("Please sign in to the Admin Panel.");
  }

  const response = await fetch(`${ADMIN_API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (response.status === 401 || response.status === 403) {
    sessionStorage.removeItem("admin_access_token");
    window.location.replace("admin-login.html");
    throw new Error("Admin session expired or access denied.");
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || "The request failed.");
  }

  return data;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("en-IN");
}

function statusClass(status) {
  return String(status || "")
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "");
}

function renderCustomers() {
  const searchTerm = customerSearch.value.trim().toLowerCase();
  const selectedStatus = statusFilter.value.toUpperCase();

  const filteredCustomers = customers.filter((customer) => {
    const searchableText = [
      customer.customer_id,
      customer.name,
      customer.email,
      customer.phone,
      customer.address,
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchableText.includes(searchTerm);

    const matchesStatus =
      !selectedStatus ||
      String(customer.status || "").toUpperCase() === selectedStatus;

    return matchesSearch && matchesStatus;
  });

  customerCount.textContent = `Showing ${filteredCustomers.length} of ${customers.length} customers`;

  if (filteredCustomers.length === 0) {
    customersTableBody.innerHTML = `
            <tr>
                <td colspan="9">No customers found.</td>
            </tr>
        `;
    return;
  }

  customersTableBody.innerHTML = filteredCustomers
    .map((customer) => {
      const currentStatus = String(customer.status || "").toUpperCase();

      const options = ["ACTIVE", "BLOCKED", "INACTIVE", "KYC_REQUIRED"]
        .map(
          (status) => `
                <option value="${status}"
                    ${status === currentStatus ? "selected" : ""}>
                    ${status}
                </option>
            `,
        )
        .join("");

      return `
            <tr>
                <td>${escapeHTML(customer.customer_id)}</td>
                <td>${escapeHTML(customer.name)}</td>
                <td>${escapeHTML(customer.email)}</td>
                <td>${escapeHTML(customer.phone)}</td>
                <td>${escapeHTML(customer.address)}</td>
                <td>${escapeHTML(customer.date_of_birth)}</td>
                <td>
                    <span class="status status-${statusClass(currentStatus)}">
                        ${escapeHTML(currentStatus || "UNKNOWN")}
                    </span>
                </td>
                <td>${escapeHTML(formatDate(customer.created_at))}</td>
                <td>
                    <div class="actions">
                        <select
                            aria-label="New status for customer ${escapeHTML(customer.customer_id)}"
                            data-status-select="${escapeHTML(customer.customer_id)}">
                            ${options}
                        </select>
                        <button
                            type="button"
                            data-update-customer="${escapeHTML(customer.customer_id)}">
                            Update
                        </button>
                    </div>
                </td>
            </tr>
        `;
    })
    .join("");
}

async function loadCustomers() {
  customersTableBody.innerHTML = `
        <tr><td colspan="9">Loading customers...</td></tr>
    `;

  showMessage("");

  try {
    const data = await adminRequest("/admin/customers");

    if (!Array.isArray(data)) {
      throw new Error("Unexpected customer response format.");
    }

    customers = data;
    renderCustomers();
  } catch (error) {
    customersTableBody.innerHTML = `
            <tr><td colspan="9">Unable to load customers.</td></tr>
        `;
    customerCount.textContent = "";
    showMessage(error.message, true);
  }
}

async function updateCustomerStatus(customerId) {
  const select = document.querySelector(
    `[data-status-select="${CSS.escape(String(customerId))}"]`,
  );

  if (!select) return;

  const newStatus = select.value;
  const customer = customers.find(
    (item) => String(item.customer_id) === String(customerId),
  );

  if (!customer) return;

  if (String(customer.status).toUpperCase() === newStatus) {
    showMessage("The customer already has this status.");
    return;
  }

  const confirmed = window.confirm(
    `Change customer ${customerId} status to ${newStatus}?`,
  );

  if (!confirmed) return;

  try {
    await adminRequest(
      `/admin/customers/${encodeURIComponent(customerId)}/status`,
      {
        method: "PUT",
        body: JSON.stringify({
          status: newStatus,
        }),
      },
    );

    showMessage(`Customer ${customerId} status updated.`);
    await loadCustomers();
  } catch (error) {
    showMessage(error.message, true);
  }
}

document
  .getElementById("refreshCustomers")
  .addEventListener("click", loadCustomers);

customerSearch.addEventListener("input", renderCustomers);
statusFilter.addEventListener("change", renderCustomers);

customersTableBody.addEventListener("click", (event) => {
  const button = event.target.closest("[data-update-customer]");

  if (button) {
    updateCustomerStatus(button.dataset.updateCustomer);
  }
});

loadCustomers();
