const budgetInput = document.getElementById("budget");
const budgetValue = document.getElementById("budget-value");
const tagButtons = document.querySelectorAll(".tag");
const chipRemoveButtons = document.querySelectorAll(".chip-remove");
const recommendBtn = document.getElementById("recommend-btn");
const productList = document.getElementById("product-list");
const statusText = document.getElementById("status");
const downloadBtn = document.getElementById("download-btn");
const categorySelect = document.getElementById("category");

let currentRecommendations = [];
let catalogItems = [];

const colorPairs = [
  ["#2563EB", "#93C5FD"],
  ["#111827", "#6B7280"],
  ["#F97316", "#FDBA74"],
  ["#22C55E", "#86EFAC"],
  ["#8B5CF6", "#C4B5FD"],
];

function formatCurrency(value) {
  return `\u20B9${Number(value).toLocaleString("en-IN")}`;
}

function updateBudget() {
  if (!budgetInput || !budgetValue) return;
  budgetValue.textContent = formatCurrency(budgetInput.value);
}

function hashString(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash << 5) - hash + text.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function buildImageData(name) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
  const paletteIndex = hashString(name) % colorPairs.length;
  const [from, to] = colorPairs[paletteIndex];
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='72' height='72'>
    <defs>
      <linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>
        <stop offset='0' stop-color='${from}' />
        <stop offset='1' stop-color='${to}' />
      </linearGradient>
    </defs>
    <rect width='72' height='72' rx='16' fill='url(#g)' />
    <circle cx='36' cy='28' r='16' fill='rgba(255,255,255,0.45)' />
    <text x='36' y='48' text-anchor='middle' font-family='Plus Jakarta Sans, sans-serif'
      font-size='18' font-weight='700' fill='white'>${initials}</text>
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function setStatus(text, isError = false) {
  if (!statusText) return;
  statusText.textContent = text;
  statusText.classList.toggle("is-error", isError);
}

function renderSkeletons() {
  if (!productList) return;
  productList.innerHTML = "";
  for (let i = 0; i < 3; i += 1) {
    const sk = document.createElement("div");
    sk.className = "skeleton-card";
    productList.appendChild(sk);
  }
}

function renderEmpty(message) {
  if (!productList) return;
  productList.innerHTML = `<div class="empty-state">${message}</div>`;
}

function renderStars(rating) {
  const full = Math.round(rating);
  return "\u2605".repeat(full) + "\u2606".repeat(5 - full);
}

function normalizeScores(items) {
  const scores = items.map((item) => Number(item.score) || 0);
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  return { min, max };
}

function scoreToMatch(score, min, max) {
  if (max === min) return 92;
  const normalized = (score - min) / (max - min);
  return Math.round(85 + normalized * 14);
}

function scoreToRating(score, min, max) {
  if (max === min) return 4.4;
  const normalized = (score - min) / (max - min);
  return Number((4.1 + normalized * 0.8).toFixed(1));
}

function estimatePrice(productId, score) {
  const base = 14000 + (Number(productId) % 70) * 1000;
  const bonus = Math.round((Number(score) || 0) * 1200);
  return base + bonus;
}

function resolvePrice(item) {
  const numeric = Number(item.price);
  if (Number.isFinite(numeric) && numeric > 0) {
    return numeric;
  }
  return estimatePrice(item.product_id, item.score);
}

function deriveScore(item) {
  const seed = hashString(String(item.product_name || item.product_id));
  const normalized = (seed % 100) / 100;
  return Number((3.9 + normalized * 0.9).toFixed(4));
}

function normalizeFeatures(raw) {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "string") {
    return raw
      .split(";")
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return [];
}

function normalizeText(value) {
  return String(value ?? "").trim().toLowerCase();
}

function getSelectedFeatures() {
  return Array.from(document.querySelectorAll(".tag.is-active"))
    .map((tag) => tag.textContent.trim())
    .filter(Boolean);
}

function getSelectedBrands() {
  return Array.from(document.querySelectorAll(".chip"))
    .map((chip) => {
      const label = chip.childNodes[0]?.textContent || "";
      return label.trim();
    })
    .filter(Boolean);
}

function applyBaseFilters(items) {
  let filtered = [...items];
  const selectedCategory = normalizeText(categorySelect?.value);
  const budget = budgetInput ? Number(budgetInput.value) : null;

  if (selectedCategory) {
    filtered = filtered.filter(
      (item) => normalizeText(item.category) === selectedCategory
    );
  }

  if (budget) {
    filtered = filtered.filter((item) => resolvePrice(item) <= budget);
  }

  return filtered;
}

function applyExtraFilters(items, options = {}) {
  let filtered = [...items];
  const selectedBrands = getSelectedBrands();
  const selectedFeatures = getSelectedFeatures();

  if (selectedBrands.length && options.allowBrands !== false) {
    filtered = filtered.filter((item) =>
      selectedBrands.some(
        (brand) => normalizeText(brand) === normalizeText(item.brand)
      )
    );
  }

  if (selectedFeatures.length && options.allowFeatures !== false) {
    filtered = filtered.filter((item) => {
      const features = normalizeFeatures(item.features).map(normalizeText);
      return selectedFeatures.some((feature) => features.includes(normalizeText(feature)));
    });
  }

  return filtered;
}

function applyFiltersWithFallback(items) {
  const baseFiltered = applyBaseFilters(items);
  if (!baseFiltered.length) {
    return { results: [], attempt: -1 };
  }

  const attempts = [
    { allowBrands: true, allowFeatures: true },
    { allowBrands: true, allowFeatures: false },
    { allowBrands: false, allowFeatures: false },
  ];

  for (let i = 0; i < attempts.length; i += 1) {
    const filtered = applyExtraFilters(baseFiltered, attempts[i]);
    if (filtered.length) {
      return { results: filtered, attempt: i };
    }
  }

  return { results: baseFiltered, attempt: attempts.length - 1 };
}

function enrichItem(item) {
  const score = Number(item.score);
  const resolvedScore = Number.isFinite(score) ? score : deriveScore(item);
  const enriched = {
    ...item,
    score: resolvedScore,
  };
  return {
    ...enriched,
    price: resolvePrice(enriched),
    features: normalizeFeatures(enriched.features),
  };
}

function createProductCard(item, scoreRange) {
  const article = document.createElement("article");
  article.className = "product-card";

  const productImage = document.createElement("div");
  productImage.className = "product-image";
  const img = document.createElement("img");
  img.alt = item.product_name;
  img.src = item.image_url || buildImageData(item.product_name);
  productImage.appendChild(img);

  const info = document.createElement("div");
  info.className = "product-info";

  const main = document.createElement("div");
  main.className = "product-main";
  const title = document.createElement("h3");
  title.textContent = item.product_name;

  const ratingWrap = document.createElement("div");
  ratingWrap.className = "rating";
  const ratingValue = scoreToRating(Number(item.score), scoreRange.min, scoreRange.max);
  const stars = document.createElement("span");
  stars.className = "stars";
  stars.setAttribute("aria-hidden", "true");
  stars.textContent = renderStars(ratingValue);
  const ratingLabel = document.createElement("span");
  ratingLabel.className = "rating-value";
  ratingLabel.textContent = ratingValue.toFixed(1);
  ratingWrap.appendChild(stars);
  ratingWrap.appendChild(ratingLabel);

  main.appendChild(title);
  main.appendChild(ratingWrap);

  const meta = document.createElement("div");
  meta.className = "product-meta";
  const match = document.createElement("span");
  match.className = "match";
  const matchScore = scoreToMatch(Number(item.score), scoreRange.min, scoreRange.max);
  match.textContent = `Match Score: ${matchScore}%`;
  const price = document.createElement("span");
  price.className = "price";
  price.textContent = formatCurrency(resolvePrice(item));
  meta.appendChild(match);
  meta.appendChild(price);

  info.appendChild(main);
  info.appendChild(meta);

  const button = document.createElement("button");
  button.className = "btn-secondary";
  button.type = "button";
  button.textContent = "View Product";

  article.appendChild(productImage);
  article.appendChild(info);
  article.appendChild(button);

  return {
    article,
    meta: {
      matchScore,
      price: price.textContent,
      rating: ratingValue,
    },
  };
}

function renderProducts(items) {
  if (!productList) return;
  productList.innerHTML = "";
  if (!items.length) {
    renderEmpty("No products match your preferences.");
    return;
  }

  const scoreRange = normalizeScores(items);
  currentRecommendations = [];

  items.forEach((item) => {
    const { article, meta } = createProductCard(item, scoreRange);
    productList.appendChild(article);
    currentRecommendations.push({ ...item, ...meta });
  });
}

function escapeCsv(value) {
  const safe = String(value ?? "");
  if (safe.includes(",") || safe.includes("\n") || safe.includes('"')) {
    return `"${safe.replace(/"/g, '""')}"`;
  }
  return safe;
}

function downloadCsv() {
  if (!currentRecommendations.length) return;

  const headers = [
    "product_id",
    "product_name",
    "category",
    "brand",
    "price",
    "features",
    "score",
    "match_score",
    "rating",
  ];
  const rows = currentRecommendations.map((item) => [
    item.product_id,
    item.product_name,
    item.category,
    item.brand,
    item.price,
    Array.isArray(item.features) ? item.features.join(";") : item.features,
    item.score,
    item.matchScore,
    item.rating,
  ]);

  const csv = [headers.join(","), ...rows.map((row) => row.map(escapeCsv).join(","))].join(
    "\n"
  );

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "recommendations.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function renderFromCatalog() {
  if (!catalogItems.length) {
    renderEmpty("No products available yet.");
    return;
  }

  const { results, attempt } = applyFiltersWithFallback(catalogItems);
  if (attempt === -1) {
    renderProducts([]);
    setStatus(
      "No products found for this category and budget. Try increasing the budget or changing category."
    );
    return;
  }

  renderProducts(results);
  if (attempt === 0) {
    setStatus(`Showing ${results.length} products.`);
  } else if (attempt === 1) {
    setStatus(`No feature match. Showing ${results.length} closest products.`);
  } else {
    setStatus(`No brand match. Showing ${results.length} closest products.`);
  }
}

async function loadCatalog() {
  if (!recommendBtn) return;
  recommendBtn.disabled = true;
  if (downloadBtn) downloadBtn.disabled = true;
  setStatus("Loading products...");
  renderSkeletons();

  try {
    const response = await fetch("/products");
    const payload = await response.json();

    if (!response.ok) {
      const detail = payload?.detail || "Request failed";
      throw new Error(detail);
    }

    const items = Array.isArray(payload) ? payload : payload?.products || [];
    catalogItems = items.map(enrichItem);
    renderFromCatalog();
  } catch (error) {
    renderEmpty("Could not load products right now.");
    setStatus(error.message || "Unexpected error occurred", true);
  } finally {
    recommendBtn.disabled = false;
    if (downloadBtn) downloadBtn.disabled = currentRecommendations.length === 0;
  }
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
    if (!catalogItems.length) {
      loadCatalog();
      return;
    }
    renderFromCatalog();
  });
}

if (downloadBtn) {
  downloadBtn.addEventListener("click", downloadCsv);
  downloadBtn.disabled = true;
}

loadCatalog();
