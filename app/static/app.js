const form = document.getElementById("recommend-form");
const userInput = document.getElementById("user-id");
const cards = document.getElementById("cards");
const message = document.getElementById("message");
const submitBtn = document.getElementById("submit-btn");
const resultMeta = document.getElementById("result-meta");

function setMessage(text, isError = false) {
  message.textContent = text;
  message.style.color = isError ? "#ffb6a0" : "#ffc566";
}

function clearMessage() {
  message.textContent = "";
}

function renderLoading() {
  cards.innerHTML = "";
  for (let i = 0; i < 3; i += 1) {
    const sk = document.createElement("div");
    sk.className = "skeleton";
    cards.appendChild(sk);
  }
}

function renderEmpty(text) {
  cards.innerHTML = `<div class="empty">${text}</div>`;
}

function renderCards(items) {
  cards.innerHTML = "";
  if (!items.length) {
    renderEmpty("No recommendations available for this user.");
    return;
  }

  items.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "card";
    card.style.animationDelay = `${index * 60}ms`;

    const score = Number(item.score).toFixed(4);
    card.innerHTML = `
      <div class="card-top">
        <h3>${item.product_name}</h3>
        <span class="score">Score: ${score}</span>
      </div>
      <div>
        <span class="chip">${item.category}</span>
        <span class="chip">Product ID: ${item.product_id}</span>
      </div>
    `;
    cards.appendChild(card);
  });
}

async function fetchRecommendations(userId) {
  submitBtn.disabled = true;
  setMessage("Finding recommendations...");
  renderLoading();
  resultMeta.textContent = `Top 5 results for user ${userId}`;

  try {
    const response = await fetch(`/recommend/${userId}`);
    const payload = await response.json();

    if (!response.ok) {
      const detail = payload?.detail || "Request failed";
      throw new Error(detail);
    }

    clearMessage();
    renderCards(payload.recommended_products || []);
  } catch (err) {
    renderEmpty("Could not load recommendations right now.");
    setMessage(err.message || "Unexpected error occurred", true);
  } finally {
    submitBtn.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const userId = Number.parseInt(userInput.value, 10);
  if (!Number.isInteger(userId) || userId <= 0) {
    setMessage("Please enter a valid positive user ID.", true);
    renderEmpty("Enter a valid user ID to get recommendations.");
    return;
  }

  fetchRecommendations(userId);
});

fetchRecommendations(1);
