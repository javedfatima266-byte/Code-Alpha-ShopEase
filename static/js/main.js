/**
 * ShopEase — Main Frontend Script
 * Handles UI interactions, cart quantity controls, dropdowns, and mobile drawers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Drawer Toggle
  const mobileToggle = document.getElementById('mobileToggleBtn');
  const mobileDrawer = document.getElementById('mobileDrawer');

  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      mobileDrawer.classList.toggle('open');
    });

    // Close mobile drawer when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileDrawer.contains(e.target) && !mobileToggle.contains(e.target)) {
        mobileDrawer.classList.remove('open');
      }
    });
  }

  // 2. User Profile Dropdown Toggle
  const userBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');

  if (userBtn && userDropdown) {
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!userDropdown.contains(e.target) && !userBtn.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });
  }

  // 3. Alert Messages Close & Auto-Dismiss
  const alertCloseBtns = document.querySelectorAll('.alert-close');
  alertCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Auto-dismiss success and info alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-success, .alert-info');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      if (document.body.contains(alert)) {
        alert.style.transition = 'all 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        setTimeout(() => alert.remove(), 400);
      }
    }, 5000);
  });

  // 4. Quantity Controls on Product Detail Page
  const detailQtyInput = document.getElementById('detailQtyInput');
  const detailQtyMinus = document.getElementById('detailQtyMinus');
  const detailQtyPlus = document.getElementById('detailQtyPlus');

  if (detailQtyInput && detailQtyMinus && detailQtyPlus) {
    const maxStock = parseInt(detailQtyInput.getAttribute('max'), 10) || 999;
    const minQty = parseInt(detailQtyInput.getAttribute('min'), 10) || 1;

    detailQtyMinus.addEventListener('click', () => {
      let val = parseInt(detailQtyInput.value, 10) || 1;
      if (val > minQty) {
        detailQtyInput.value = val - 1;
      }
    });

    detailQtyPlus.addEventListener('click', () => {
      let val = parseInt(detailQtyInput.value, 10) || 1;
      if (val < maxStock) {
        detailQtyInput.value = val + 1;
      }
    });

    detailQtyInput.addEventListener('change', () => {
      let val = parseInt(detailQtyInput.value, 10);
      if (isNaN(val) || val < minQty) {
        detailQtyInput.value = minQty;
      } else if (val > maxStock) {
        detailQtyInput.value = maxStock;
      }
    });
  }

  // 5. Checkout payment option selector styling
  const paymentCards = document.querySelectorAll('.payment-option-card');
  paymentCards.forEach(card => {
    card.addEventListener('click', () => {
      const radio = card.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        paymentCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');
      }
    });
  });

  // 6. Global Quick Search Shortcut (Press '/' to focus search input)
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      const searchInput = document.querySelector('.search-input');
      if (searchInput) {
        searchInput.focus();
      }
    }
  });
});
