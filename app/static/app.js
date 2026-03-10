const budgetInput = document.getElementById("budget");
const budgetValue = document.getElementById("budget-value");
const tagButtons = document.querySelectorAll(".tag");
const chipRemoveButtons = document.querySelectorAll(".chip-remove");
const recommendBtn = document.getElementById("recommend-btn");

function formatCurrency(value) {
  return `\u20B9${Number(value).toLocaleString("en-IN")}`;
}

function updateBudget() {
  if (!budgetInput || !budgetValue) return;
  budgetValue.textContent = formatCurrency(budgetInput.value);
}

if (budgetInput) {
  budgetInput.addEventListener("input", updateBudget);
  updateBudget();
}

tagButtons.forEach((button) => {
  button.addEventListener("click", () => {
    button.classList.toggle("is-active");
  });
});

chipRemoveButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const chip = button.closest(".chip");
    if (chip) {
      chip.remove();
    }
  });
});

if (recommendBtn) {
  recommendBtn.addEventListener("click", () => {
    recommendBtn.classList.add("is-loading");
    recommendBtn.disabled = true;

    window.setTimeout(() => {
      recommendBtn.classList.remove("is-loading");
      recommendBtn.disabled = false;
    }, 600);
  });
}
