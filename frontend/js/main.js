/**
 * main.js
 * --------
 * Shared page chrome: highlights the active nav link, keeps a
 * `currentUser` in memory, updates the cart-count badge, and provides a
 * tiny toast() helper used by every page for success/error feedback.
 *
 * Every page includes this file *after* api.js and calls initPage() on
 * DOMContentLoaded.
 */

let currentUser = null;

/** Show a floating toast message (auto-dismisses). */
function toast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

/** Show/hide an inline <div class="alert"> element by id. */
function showAlert(elementId, message, type = "error") {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.className = `alert alert-${type} show`;
}
function hideAlert(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.className = "alert";
}

/** Highlight the current page in the nav bar based on the file name. */
function markActiveNavLink() {
  const page = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".navbar-links a").forEach((a) => {
    if (a.getAttribute("href") === page) a.classList.add("active");
  });
}

/** Fetch the logged-in user (if any) and update the navbar accordingly. */
async function loadCurrentUser() {
  try {
    const data = await api.get("/me");
    currentUser = data.user;
  } catch (_) {
    currentUser = null;
  }

  const userSlot = document.getElementById("navbar-user-slot");
  if (!userSlot) return;

  if (currentUser) {
    userSlot.innerHTML = `
      <span class="navbar-user">Hi, ${escapeHtml(currentUser.name)}</span>
      <button class="btn btn-outline btn-sm" id="logout-btn">Log out</button>
    `;
    document.getElementById("logout-btn").addEventListener("click", async () => {
      await api.post("/logout");
      currentUser = null;
      window.location.href = "login.html";
    });
  } else {
    userSlot.innerHTML = `
      <a class="btn btn-outline btn-sm" href="login.html">Log in</a>
      <a class="btn btn-primary btn-sm" href="register.html">Sign up</a>
    `;
  }
}

/** Update the little count badge next to the cart nav link. */
async function refreshCartBadge() {
  const badge = document.getElementById("cart-count-badge");
  if (!badge) return;

  if (!currentUser) {
    badge.style.display = "none";
    return;
  }

  try {
    const data = await api.get("/cart");
    const count = data.items.reduce((sum, item) => sum + item.quantity, 0);
    if (count > 0) {
      badge.textContent = count;
      badge.style.display = "flex";
    } else {
      badge.style.display = "none";
    }
  } catch (_) {
    badge.style.display = "none";
  }
}

/** Basic HTML-escaping for any user-supplied text we render. */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(value) {
  return `$${Number(value).toFixed(2)}`;
}

/** Redirect to login.html if nobody is logged in. Returns true if OK to proceed. */
function requireAuthOrRedirect() {
  if (!currentUser) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

/**
 * Call once per page, awaited at the top of that page's own
 * DOMContentLoaded handler (see products.js / cart.js / orders.js /
 * auth.js). Sets up the navbar (active link, login state, cart badge)
 * before any page-specific data loading runs, so page scripts can rely
 * on `currentUser` being accurate afterwards.
 */
async function initPage() {
  markActiveNavLink();
  await loadCurrentUser();
  await refreshCartBadge();
}
