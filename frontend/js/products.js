/**
 * products.js
 * -------------
 * Product catalog page: loads + renders products, wires up search /
 * category filter / price sort, handles "Add to cart", and — only for
 * logged-in admins — renders a small inline admin panel for product CRUD.
 */

let allCategories = [];

async function loadCategories() {
  try {
    const data = await api.get("/categories");
    allCategories = data.categories;
    const select = document.getElementById("filter-category");
    select.innerHTML = `<option value="">All categories</option>` +
      allCategories.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
  } catch (err) {
    console.error(err);
  }
}

function buildQuery() {
  const search = document.getElementById("filter-search").value.trim();
  const category = document.getElementById("filter-category").value;
  const sort = document.getElementById("filter-sort").value;

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (category) params.set("category", category);
  if (sort) params.set("sort", sort);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

function renderProductCard(product) {
  const stockLabel = product.in_stock
    ? `<span class="stock-pill in">In stock</span>`
    : `<span class="stock-pill out">Out of stock</span>`;

  return `
    <div class="product-card" data-id="${product.id}">
      <div class="thumb"><img src="${escapeHtml(product.image || '')}" alt="${escapeHtml(product.name)}" loading="lazy" /></div>
      <div class="body">
        <div class="category">${escapeHtml(product.category)}</div>
        <h3>${escapeHtml(product.name)}</h3>
        <div class="desc">${escapeHtml(product.description || '')}</div>
        <div class="footer-row">
          <span class="price-ticket">${formatPrice(product.price)}</span>
          ${stockLabel}
        </div>
        <button class="btn btn-primary btn-block add-to-cart-btn" ${product.in_stock ? '' : 'disabled'}
                data-id="${product.id}" data-name="${escapeHtml(product.name)}">
          ${product.in_stock ? 'Add to cart' : 'Unavailable'}
        </button>
      </div>
    </div>
  `;
}

async function loadProducts() {
  const grid = document.getElementById("product-grid");
  grid.innerHTML = `<div class="loading-row"><div class="spinner"></div></div>`;

  try {
    const data = await api.get(`/products${buildQuery()}`);
    if (data.products.length === 0) {
      grid.innerHTML = `<div class="empty-state"><h3>No products found</h3><p>Try a different search term or category.</p></div>`;
      return;
    }
    grid.innerHTML = data.products.map(renderProductCard).join("");

    grid.querySelectorAll(".add-to-cart-btn").forEach((btn) => {
      btn.addEventListener("click", () => handleAddToCart(btn));
    });
  } catch (err) {
    grid.innerHTML = `<div class="empty-state"><h3>Couldn't load products</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

async function handleAddToCart(btn) {
  if (!currentUser) {
    window.location.href = "login.html";
    return;
  }

  const productId = Number(btn.dataset.id);
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Adding...";

  try {
    await api.post("/cart/add", { product_id: productId, quantity: 1 });
    toast(`${btn.dataset.name} added to cart.`, "success");
    await refreshCartBadge();
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

/* ---------------------------------------------------------------------
   Admin panel: only rendered/wired up if the logged-in user is an admin.
   --------------------------------------------------------------------- */
async function setupAdminPanel() {
  const panel = document.getElementById("admin-panel");
  if (!panel) return;

  if (!currentUser || !currentUser.is_admin) {
    panel.style.display = "none";
    return;
  }
  panel.style.display = "block";

  document.getElementById("admin-add-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById("admin-name").value.trim(),
      category: document.getElementById("admin-category").value.trim(),
      price: document.getElementById("admin-price").value,
      quantity: document.getElementById("admin-quantity").value,
      description: document.getElementById("admin-description").value.trim(),
      image: document.getElementById("admin-image").value.trim(),
    };
    try {
      await api.post("/admin/product", payload);
      toast("Product created.", "success");
      e.target.reset();
      await loadCategories();
      await loadProducts();
      await loadAdminTable();
    } catch (err) {
      toast(err.message, "error");
    }
  });

  await loadAdminTable();
}

async function loadAdminTable() {
  const tbody = document.getElementById("admin-table-body");
  if (!tbody) return;

  try {
    const data = await api.get("/products");
    tbody.innerHTML = data.products.map((p) => `
      <tr data-id="${p.id}">
        <td>${p.id}</td>
        <td>${escapeHtml(p.name)}</td>
        <td>${escapeHtml(p.category)}</td>
        <td><input type="number" step="0.01" class="edit-price" value="${p.price}" /></td>
        <td><input type="number" class="edit-quantity" value="${p.quantity}" /></td>
        <td>
          <button class="btn btn-outline btn-sm save-product-btn">Save</button>
          <button class="btn btn-ghost btn-sm delete-product-btn">Delete</button>
        </td>
      </tr>
    `).join("");

    tbody.querySelectorAll(".save-product-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const row = btn.closest("tr");
        const id = row.dataset.id;
        const price = row.querySelector(".edit-price").value;
        const quantity = row.querySelector(".edit-quantity").value;
        try {
          await api.put(`/admin/product/${id}`, { price, quantity });
          toast("Product updated.", "success");
          await loadProducts();
        } catch (err) {
          toast(err.message, "error");
        }
      });
    });

    tbody.querySelectorAll(".delete-product-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const row = btn.closest("tr");
        const id = row.dataset.id;
        if (!confirm("Delete this product?")) return;
        try {
          await api.del(`/admin/product/${id}`);
          toast("Product deleted.", "success");
          await loadCategories();
          await loadProducts();
          await loadAdminTable();
        } catch (err) {
          toast(err.message, "error");
        }
      });
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Couldn't load products.</td></tr>`;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await initPage(); // navbar + currentUser, from main.js
  await loadCategories();
  await loadProducts();
  await setupAdminPanel();

  document.getElementById("filter-search").addEventListener("input", debounce(loadProducts, 350));
  document.getElementById("filter-category").addEventListener("change", loadProducts);
  document.getElementById("filter-sort").addEventListener("change", loadProducts);
});

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
