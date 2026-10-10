
const beneficiaryForm = document.getElementById("beneficiaryForm");
const beneficiaryName = document.getElementById("beneficiaryName");
const beneficiaryAccount = document.getElementById("beneficiaryAccount");
const beneficiaryBank = document.getElementById("beneficiaryBank");
const addBeneficiaryButton = document.getElementById("addBeneficiaryButton");
const beneficiaryMessage = document.getElementById("beneficiaryMessage");
const beneficiariesList = document.getElementById("beneficiariesList");
const refreshBeneficiaries = document.getElementById("refreshBeneficiaries");

if (!sessionStorage.getItem("access_token")) {
    window.location.replace("index.html");
}

function showMessage(message, isSuccess = false) {
    beneficiaryMessage.textContent = message;
    beneficiaryMessage.style.color = isSuccess ? "#15803d" : "#b91c1c";
}

function maskAccountNumber(accountNumber) {
    const number = String(accountNumber || "");
    return `XXXX XXXX ${number.slice(-4)}`;
}

function createTextElement(tag, text, className = "") {
    const element = document.createElement(tag);
    element.textContent = text ?? "—";

    if (className) {
        element.className = className;
    }

    return element;
}

function renderBeneficiaries(beneficiaries) {
    beneficiariesList.replaceChildren();

    if (!beneficiaries.length) {
        beneficiariesList.appendChild(
            createTextElement("p", "No beneficiaries added yet.")
        );
        return;
    }

    for (const beneficiary of beneficiaries) {
        const card = document.createElement("article");
        card.className = "account-card";

        card.appendChild(
            createTextElement("h3", beneficiary.name)
        );

        card.appendChild(
            createTextElement(
                "p",
                `Account: ${maskAccountNumber(beneficiary.account_number)}`,
                "account-number"
            )
        );

        card.appendChild(
            createTextElement(
                "p",
                `Bank: ${beneficiary.bank_name || "—"}`
            )
        );

        const actions = document.createElement("div");
        actions.className = "beneficiary-actions";

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => editBeneficiary(beneficiary));

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.style.backgroundColor = "#dc2626";
        deleteButton.addEventListener("click", () => deleteBeneficiary(beneficiary));

        actions.append(editButton, deleteButton);
        card.appendChild(actions);
        beneficiariesList.appendChild(card);
    }
}

async function loadBeneficiaries() {
    refreshBeneficiaries.disabled = true;
    beneficiariesList.replaceChildren();
    beneficiariesList.appendChild(
        createTextElement("p", "Loading beneficiaries...")
    );

    try {
        const beneficiaries = await apiRequest("/beneficiaries");
        renderBeneficiaries(beneficiaries);
        showMessage("");
    } catch (error) {
        beneficiariesList.replaceChildren();
        showMessage(error.message || "Unable to load beneficiaries.");
    } finally {
        refreshBeneficiaries.disabled = false;
    }
}

beneficiaryForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const name = beneficiaryName.value.trim();
    const accountNumber = beneficiaryAccount.value.trim();
    const bankName = beneficiaryBank.value.trim();

    if (!name || !bankName) {
        showMessage("Please fill in all required fields.");
        return;
    }

    if (!/^\d{12}$/.test(accountNumber)) {
        showMessage("Enter a valid 12-digit account number.");
        return;
    }

    addBeneficiaryButton.disabled = true;
    addBeneficiaryButton.textContent = "Saving...";

    try {
        await apiRequest("/beneficiaries", {
            method: "POST",
            body: JSON.stringify({
                name: name,
                account_number: accountNumber,
                bank_name: bankName
            })
        });

        showMessage("Beneficiary added successfully.", true);
        beneficiaryForm.reset();
        await loadBeneficiaries();
    } catch (error) {
        showMessage(error.message || "Unable to add beneficiary.");
    } finally {
        addBeneficiaryButton.disabled = false;
        addBeneficiaryButton.textContent = "Add Beneficiary";
    }
});

async function editBeneficiary(beneficiary) {
    const name = prompt("Enter beneficiary name:", beneficiary.name);
    if (name === null) return;

    const accountNumber = prompt(
        "Enter 12-digit account number:",
        beneficiary.account_number
    );
    if (accountNumber === null) return;

    const bankName = prompt(
        "Enter bank name:",
        beneficiary.bank_name || ""
    );
    if (bankName === null) return;

    if (!name.trim() || !bankName.trim()) {
        showMessage("Name and bank name are required.");
        return;
    }

    if (!/^\d{12}$/.test(accountNumber.trim())) {
        showMessage("Enter a valid 12-digit account number.");
        return;
    }

    try {
        await apiRequest(`/beneficiaries/${beneficiary.beneficiary_id}`, {
            method: "PUT",
            body: JSON.stringify({
                name: name.trim(),
                account_number: accountNumber.trim(),
                bank_name: bankName.trim()
            })
        });

        showMessage("Beneficiary updated successfully.", true);
        await loadBeneficiaries();
    } catch (error) {
        showMessage(error.message || "Unable to update beneficiary.");
    }
}

async function deleteBeneficiary(beneficiary) {
    const confirmed = confirm(
        `Delete beneficiary "${beneficiary.name}"?`
    );

    if (!confirmed) return;

    try {
        await apiRequest(`/beneficiaries/${beneficiary.beneficiary_id}`, {
            method: "DELETE"
        });

        showMessage("Beneficiary deleted successfully.", true);
        await loadBeneficiaries();
    } catch (error) {
        showMessage(error.message || "Unable to delete beneficiary.");
    }
}

refreshBeneficiaries.addEventListener("click", loadBeneficiaries);

loadBeneficiaries();