/**
 * orders.js
 * -----------
 * Order history page: lists all past orders for the logged-in user,
 * most recent first, each with its line items.
 */

function renderOrder(order) {
  const date = new Date(order.created_at).toLocaleString();
  const lines = order.items.map((item) => `
    <div class="order-line">
      <span>${escapeHtml(item.product_name || 'Unknown product')} × ${item.quantity}</span>
      <span>${formatPrice(item.subtotal)}</span>
    </div>
  `).join("");

  return `
    <div class="order-card">
      <div class="order-head">
        <span class="oid">Order #${order.id}</span>
        <span class="odate">${date}</span>
      </div>
      ${lines}
      <div class="order-line" style="margin-top:8px; font-weight:700; color: var(--color-ink);">
        <span>Total</span>
        <span class="price-ticket">${formatPrice(order.total_price)}</span>
      </div>
    </div>
  `;
}

async function loadOrders() {
  const list = document.getElementById("orders-list");
  list.innerHTML = `<div class="loading-row"><div class="spinner"></div></div>`;

  try {
    const data = await api.get("/orders");
    if (data.orders.length === 0) {
      list.innerHTML = `<div class="empty-state"><h3>No orders yet</h3><p>Your completed orders will show up here.</p><br/><a class="btn btn-primary" href="products.html">Start shopping</a></div>`;
      return;
    }
    list.innerHTML = data.orders.map(renderOrder).join("");
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><h3>Couldn't load your orders</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await initPage(); // navbar + currentUser, from main.js
  if (!requireAuthOrRedirect()) return;

  await loadOrders();
});
