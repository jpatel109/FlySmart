document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll('.addon-option input[type="checkbox"]');
  const totalDisplay = document.getElementById('addon-total');
  const toggleBtn = document.getElementById('toggle-addons');
  const addonArrow = document.getElementById('addon-arrow');
  const content = document.getElementById('addons-content');

  // Update total price including base fare, tax, and selected addons
  function updateAddonsTotal() {
    let addonTotal = 0;

    checkboxes.forEach(cb => {
      const label = cb.closest('label');
      if (cb.checked) {
        addonTotal += parseInt(cb.value);
        label?.classList.add('checked', 'glow');
      } else {
        label?.classList.remove('checked', 'glow');
      }
    });

    // Update Add-on total text
    if (totalDisplay) {
      totalDisplay.textContent = `₹${addonTotal.toLocaleString("en-IN")}`;
    }

    // Get base fare and tax values from HTML
    const base = parseFloat(document.getElementById('baseFare')?.textContent.replace(/[^0-9.]/g, '') || 0);
    const tax = parseFloat(document.getElementById('taxes')?.textContent.replace(/[^0-9.]/g, '') || 0);

    // Calculate final total
    const grandTotal = base + tax + addonTotal;

    // Update total in the price detail section
    const totalEl = document.getElementById('grandTotal');
    if (totalEl) {
      totalEl.textContent = `₹${grandTotal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
    }
  }

  // Collapse/Expand add-on section
  function toggleAddonsSection() {
    content?.classList.toggle('hidden');
    addonArrow?.classList.toggle('rotated');
  }

  // Add event listeners
  checkboxes.forEach(cb => cb.addEventListener('change', updateAddonsTotal));
  toggleBtn?.addEventListener('click', toggleAddonsSection);

  // Initial call
  updateAddonsTotal();
});

// Optional legacy function for other price blocks
function updateAddonPrice(checkbox) {
  const checkboxes = document.querySelectorAll('.addon-card input[type="checkbox"]');
  let total = 0;
  checkboxes.forEach(cb => {
    if (cb.checked) total += parseInt(cb.value);
  });
  document.getElementById("totalPrice").textContent = `₹${total}`;
}

function toggleAddons() {
  const list = document.getElementById("addonList");
  list.style.display = list.style.display === "none" ? "block" : "none";
}

// Payment Form Validation //
document.addEventListener("DOMContentLoaded", function () {
  const cardNumberInput = document.getElementById('card-number');
  const cardNameInput = document.getElementById('card-name');
  const expiryInput = document.getElementById('expiry');
  const cvvInput = document.getElementById('cvv');

  // Format Card Number with spacing
  cardNumberInput.addEventListener('input', function () {
    let value = this.value.replace(/\D/g, '').substring(0, 16); // Remove non-digits, max 16
    value = value.replace(/(.{4})/g, '$1 ').trim(); // Add space every 4 digits
    this.value = value;
  });

  // Allow only letters and space in Card Name
  cardNameInput.addEventListener('input', function () {
    this.value = this.value.replace(/[^A-Za-z\s]/g, '');
  });

  // Format and validate Expiry Date
  expiryInput.addEventListener('input', function () {
    let value = this.value.replace(/\D/g, '').substring(0, 4); // Only digits, max 4
    if (value.length >= 3) {
      value = value.substring(0, 2) + '/' + value.substring(2);
    }
    this.value = value;
  });

  expiryInput.addEventListener('blur', function () {
    const regex = /^(0[1-9]|1[0-2])\/\d{2}$/;
    if (!regex.test(this.value)) {
      alert('Please enter a valid expiry date in MM/YY format.');
      this.focus();
    } else {
      // Optional: check if date is in the future
      const [month, year] = this.value.split('/').map(Number);
      const current = new Date();
      const exp = new Date(2000 + year, month - 1);
      if (exp < current) {
        alert('Expiry date must be in the future.');
        this.focus();
      }
    }
  });

  // Only allow 3 digits in CVV
  cvvInput.addEventListener('input', function () {
    this.value = this.value.replace(/\D/g, '').substring(0, 3);
  });
});

// Form Validation for Booking Details //
document.querySelector("form").addEventListener("submit", function(e) {
  const name = document.querySelector("input[name='full_name']").value.trim();
  const email = document.querySelector("input[name='email']").value.trim();
  const phone = document.querySelector("input[name='phone']").value.trim();

  const nameRegex = /^[a-zA-Z\s]+$/;
  const phoneRegex = /^[0-9]{10}$/;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!nameRegex.test(name)) {
      alert("Please enter a valid full name (letters and spaces only).");
      e.preventDefault();
      return;
  }
  if (!emailRegex.test(email)) {
      alert("Please enter a valid email address.");
      e.preventDefault();
      return;
  }
  if (!phoneRegex.test(phone)) {
      alert("Please enter a valid 10-digit phone number.");
      e.preventDefault();
      return;
  }
});
