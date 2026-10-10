const welcomeMessage = document.getElementById("welcomeMessage");
const dashboardMessage = document.getElementById("dashboardMessage");
const totalBalance = document.getElementById("totalBalance");
const savingsBalance = document.getElementById("savingsBalance");
const currentBalance = document.getElementById("currentBalance");
const savingsCount = document.getElementById("savingsCount");
const currentCount = document.getElementById("currentCount");
const accountsList = document.getElementById("accountsList");
const refreshButton = document.getElementById("refreshButton");
const logoutButton = document.getElementById("logoutButton");

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(Number(amount));
}

function maskAccountNumber(accountNumber) {
  const number = String(accountNumber);
  return `XXXX XXXX ${number.slice(-4)}`;
}

function renderAccounts(accounts) {
  accountsList.replaceChildren();

  if (!accounts.length) {
    accountsList.textContent = "No accounts found.";
    return;
  }

  for (const account of accounts) {
    const card = document.createElement("article");
    card.className = "account-card";

    const heading = document.createElement("h3");
    heading.textContent = `${account.account_type} Account`;

    const number = document.createElement("p");
    number.className = "account-number";
    number.textContent = maskAccountNumber(account.account_number);

    const balance = document.createElement("p");
    balance.className = "account-balance";
    balance.textContent = formatCurrency(account.balance);

    const status = document.createElement("span");
    status.className = "account-status";
    status.textContent = account.status;

    card.append(heading, number, balance, status);
    accountsList.appendChild(card);
  }
}

async function loadDashboard() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    window.location.replace("index.html");
    return;
  }

  refreshButton.disabled = true;
  dashboardMessage.textContent = "";
  accountsList.textContent = "Loading your accounts...";

  try {
    const [accounts, profile] = await Promise.all([
      apiRequest("/accounts"),
      apiRequest("/customers/me"),
    ]);

    let total = 0;
    let savings = 0;
    let current = 0;
    let savingsNumber = 0;
    let currentNumber = 0;

    for (const account of accounts) {
      const balance = Number(account.balance);
      total += balance;

      if (account.account_type === "SAVINGS") {
        savings += balance;
        savingsNumber++;
      }

      if (account.account_type === "CURRENT") {
        current += balance;
        currentNumber++;
      }
    }

    totalBalance.textContent = formatCurrency(total);
    savingsBalance.textContent = formatCurrency(savings);
    currentBalance.textContent = formatCurrency(current);

    savingsCount.textContent = `${savingsNumber} savings account(s)`;

    currentCount.textContent = `${currentNumber} current account(s)`;

    const customer = profile.customer || profile;
    const customerName = customer.name;

    welcomeMessage.textContent = customerName
      ? `Welcome back, ${customerName}!`
      : "Welcome back!";

    renderAccounts(accounts);

    // Check which account types the customer already has
    const hasSavings = accounts.some(
      (account) => account.account_type === "SAVINGS",
    );

    const hasCurrent = accounts.some(
      (account) => account.account_type === "CURRENT",
    );

    // Hide the action when both accounts already exist
    const openAccountAction = document.getElementById("openAccountAction");

    if (openAccountAction) {
      openAccountAction.style.display =
        hasSavings && hasCurrent ? "none" : "flex";
    }
  } catch (error) {
    dashboardMessage.textContent =
      error.message || "Unable to load your dashboard.";

    accountsList.textContent = "Could not load accounts.";

    if (error.message && error.message.toLowerCase().includes("unauthorized")) {
      sessionStorage.removeItem("access_token");
      window.location.replace("index.html");
    }
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", loadDashboard);

logoutButton.addEventListener("click", function () {
  sessionStorage.removeItem("access_token");
  window.location.replace("index.html");
});

loadDashboard();
