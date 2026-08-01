/**
 * auth.js
 * --------
 * Handles the login and register forms. Both forms live on separate
 * pages but share this one script; each page only wires up the form
 * that actually exists in its DOM.
 */

document.addEventListener("DOMContentLoaded", async () => {
  await initPage(); // navbar + currentUser, from main.js

  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideAlert("auth-alert");

      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const submitBtn = loginForm.querySelector("button[type=submit]");

      submitBtn.disabled = true;
      submitBtn.textContent = "Logging in...";
      try {
        await api.post("/login", { email, password });
        window.location.href = "products.html";
      } catch (err) {
        showAlert("auth-alert", err.message, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Log in";
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideAlert("auth-alert");

      const name = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirm-password").value;
      const submitBtn = registerForm.querySelector("button[type=submit]");

      if (password !== confirmPassword) {
        showAlert("auth-alert", "Passwords do not match.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Creating account...";
      try {
        await api.post("/register", { name, email, password });
        window.location.href = "products.html";
      } catch (err) {
        showAlert("auth-alert", err.message, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Create account";
      }
    });
  }
});
