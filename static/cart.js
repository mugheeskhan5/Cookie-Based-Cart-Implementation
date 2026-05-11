// Cookie helper functions
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    // Encode value to ensure valid cookie string
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for(let i=0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

// Cart functionality
function getCart() {
    let cart = getCookie("cart");
    if (cart) {
        try {
            return JSON.parse(cart);
        } catch(e) {
            return [];
        }
    }
    return [];
}

function saveCart(cart) {
    // Save as compact JSON as per requirements
    setCookie("cart", JSON.stringify(cart), 7); // 7 days expiry
    updateCartCount();
}

function logAction(action, details) {
    fetch('/log-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action, details: details })
    }).catch(err => console.error("Logging failed", err));
}

function addToCart(id, name, price) {
    let cart = getCart();
    let item = cart.find(i => i.n === name); // Use 'n' for name as compact key
    if (item) {
        item.q += 1;
    } else {
        cart.push({ n: name, p: price, q: 1 });
    }
    saveCart(cart);
    logAction("Item added to cart", `${name} - $${price}`);
    alert(`${name} added to cart!`);
}

function updateQuantity(name, change) {
    let cart = getCart();
    let item = cart.find(i => i.n === name);
    if (item) {
        item.q += change;
        if (item.q <= 0) {
            cart = cart.filter(i => i.n !== name);
            logAction("Item removed from cart", name);
        } else {
            logAction("Item quantity updated", `${name} - New Quantity: ${item.q}`);
        }
        saveCart(cart);
        renderCart();
    }
}

function removeItem(name) {
    let cart = getCart();
    cart = cart.filter(i => i.n !== name);
    saveCart(cart);
    logAction("Item removed from cart", name);
    renderCart();
}

function clearCart() {
    let cart = getCart();
    let itemCount = cart.reduce((sum, item) => sum + item.q, 0);
    saveCart([]);
    logAction("Cart cleared", `Cleared ${itemCount} items`);
    renderCart();
}

function updateCartCount() {
    let cart = getCart();
    let count = cart.reduce((sum, item) => sum + item.q, 0);
    let countElem = document.getElementById("cart-count");
    if(countElem) {
        countElem.innerText = count;
    }
}

function renderCart() {
    let cartTableBody = document.getElementById("cart-table-body");
    let cartTotalElem = document.getElementById("cart-total");
    
    if (!cartTableBody) return; // Not on the cart page
    
    let cart = getCart();
    cartTableBody.innerHTML = "";
    
    let checkoutSection = document.getElementById("checkout-section");
    let cartDataInput = document.getElementById("cart-data-input");
    
    if (cart.length === 0) {
        cartTableBody.innerHTML = "<tr><td colspan='5' style='text-align: center; padding: 2rem;'>Your cart is empty.</td></tr>";
        cartTotalElem.innerText = "0.00";
        if(checkoutSection) checkoutSection.style.display = "none";
        return;
    } else {
        if(checkoutSection) {
            checkoutSection.style.display = "block";
            cartDataInput.value = JSON.stringify(cart);
        }
    }
    
    let total = 0;
    cart.forEach(item => {
        let itemTotal = item.p * item.q;
        total += itemTotal;
        
        let tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${item.n}</td>
            <td>$${item.p.toFixed(2)}</td>
            <td>
                <div class="quantity-controls">
                    <button class="btn btn-sm btn-icon" onclick="updateQuantity('${item.n}', -1)">-</button>
                    <span class="quantity-val">${item.q}</span>
                    <button class="btn btn-sm btn-icon" onclick="updateQuantity('${item.n}', 1)">+</button>
                </div>
            </td>
            <td><strong>$${itemTotal.toFixed(2)}</strong></td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeItem('${item.n}')">Remove</button>
            </td>
        `;
        cartTableBody.appendChild(tr);
    });
    
    cartTotalElem.innerText = total.toFixed(2);
    // Update the hidden input in case quantity changes
    if(cartDataInput) {
        cartDataInput.value = JSON.stringify(cart);
    }
}

// Clear cart after checkout
function clearCartCookieOnly() {
    setCookie("cart", JSON.stringify([]), 7);
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    updateCartCount();
    if(document.getElementById("cart-table-body")) {
        renderCart();
    }
});
