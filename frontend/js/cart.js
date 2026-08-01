/**
 * cart.js
 * ---------
 * Cart page: renders the current user's cart, lets them adjust
 * quantities or remove lines, and triggers checkout.
 */

function renderCartItem(item) {
  const p = item.product;
  return `
    <div class="cart-item" data-cart-item-id="${item.id}">
      <div class="thumb"><img src="${escapeHtml(p?.image || '')}" alt="${escapeHtml(p?.name || '')}" /></div>
      <div class="info">
        <h4>${escapeHtml(p?.name || 'Unknown product')}</h4>
        <div class="cat">${escapeHtml(p?.category || '')}</div>
      </div>
      <div class="qty-control">
        <button class="qty-decrease" aria-label="Decrease quantity">−</button>
        <span>${item.quantity}</span>
        <button class="qty-increase" aria-label="Increase quantity">+</button>
      </div>
      <span class="price-ticket">${formatPrice(item.subtotal)}</span>
      <button class="btn btn-ghost btn-sm remove-item-btn">Remove</button>
    </div>
  `;
}

async function loadCart() {
  const list = document.getElementById("cart-list");
  list.innerHTML = `<div class="loading-row"><div class="spinner"></div></div>`;

  try {
    const data = await api.get("/cart");

    if (data.items.length === 0) {
      list.innerHTML = `<div class="empty-state"><h3>Your cart is empty</h3><p>Browse products and add something you like.</p><br/><a class="btn btn-primary" href="products.html">Browse products</a></div>`;
      document.getElementById("checkout-btn").disabled = true;
    } else {
      list.innerHTML = data.items.map(renderCartItem).join("");
      document.getElementById("checkout-btn").disabled = false;
      wireCartItemButtons();
    }

    document.getElementById("summary-subtotal").textContent = formatPrice(data.total);
    document.getElementById("summary-total").textContent = formatPrice(data.total);
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><h3>Couldn't load your cart</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function wireCartItemButtons() {
  document.querySelectorAll(".cart-item").forEach((row) => {
    const cartItemId = Number(row.dataset.cartItemId);
    const qtySpan = row.querySelector(".qty-control span");

    row.querySelector(".qty-increase").addEventListener("click", () =>
      changeQuantity(cartItemId, Number(qtySpan.textContent) + 1)
    );
    row.querySelector(".qty-decrease").addEventListener("click", () => {
      const next = Number(qtySpan.textContent) - 1;
      if (next <= 0) {
        removeItem(cartItemId);
      } else {
        changeQuantity(cartItemId, next);
      }
    });
    row.querySelector(".remove-item-btn").addEventListener("click", () => removeItem(cartItemId));
  });
}

async function changeQuantity(cartItemId, quantity) {
  try {
    await api.put("/cart/update", { cart_item_id: cartItemId, quantity });
    await loadCart();
    await refreshCartBadge();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function removeItem(cartItemId) {
  try {
    await api.del("/cart/remove", { cart_item_id: cartItemId });
    toast("Item removed.", "success");
    await loadCart();
    await refreshCartBadge();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleCheckout() {
  const btn = document.getElementById("checkout-btn");
  btn.disabled = true;
  btn.textContent = "Placing order...";

  try {
    await api.post("/checkout");
    toast("Order placed successfully!", "success");
    await refreshCartBadge();
    window.location.href = "orders.html";
  } catch (err) {
    toast(err.message, "error");
    btn.disabled = false;
    btn.textContent = "Checkout";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await initPage(); // navbar + currentUser, from main.js
  if (!requireAuthOrRedirect()) return;

  await loadCart();
  document.getElementById("checkout-btn").addEventListener("click", handleCheckout);
});
