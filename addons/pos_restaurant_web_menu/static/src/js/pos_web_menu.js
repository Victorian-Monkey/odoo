// Gestione carrello lato client per POS Restaurant Web Menu
let cart = [];

function updateCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const placeOrderBtn = document.getElementById('place-order-btn');
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="text-muted text-center">Il carrello è vuoto</p>';
        cartTotalElement.textContent = '€0.00';
        placeOrderBtn.disabled = true;
        return;
    }
    
    let total = 0;
    let html = '';
    
    cart.forEach((item, index) => {
        total += item.price * item.quantity;
        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="text-muted">€${item.price.toFixed(2)} x ${item.quantity}</div>
                </div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="decreaseQuantity(${index})">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn" onclick="increaseQuantity(${index})">+</button>
                    <button class="btn btn-sm btn-danger ml-2" onclick="removeFromCart(${index})">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    cartItemsContainer.innerHTML = html;
    cartTotalElement.textContent = `€${total.toFixed(2)}`;
    
    const tableSelect = document.getElementById('table-select');
    placeOrderBtn.disabled = !tableSelect.value;
}

function addToCart(productId, productName, productPrice) {
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: 1,
        });
    }
    
    updateCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

function increaseQuantity(index) {
    cart[index].quantity += 1;
    updateCart();
}

function decreaseQuantity(index) {
    if (cart[index].quantity > 1) {
        cart[index].quantity -= 1;
    } else {
        removeFromCart(index);
    }
    updateCart();
}

function placeOrder() {
    const tableSelect = document.getElementById('table-select');
    const tableId = tableSelect.value;
    
    if (!tableId) {
        alert('Seleziona un tavolo');
        return;
    }
    
    if (cart.length === 0) {
        alert('Il carrello è vuoto');
        return;
    }
    
    const products = cart.map(item => ({
        id: item.id,
        quantity: item.quantity,
    }));
    
    // Chiamata AJAX per creare l'ordine
    fetch('/pos/web/menu/create_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pos_config_id: window.posConfigId,
            table_id: parseInt(tableId),
            products: products,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message || 'Ordine creato con successo!');
            cart = [];
            updateCart();
            tableSelect.value = '';
        } else {
            alert('Errore: ' + (data.error || 'Impossibile creare l\'ordine'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Errore durante la creazione dell\'ordine');
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Aggiungi prodotti al carrello
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = parseInt(this.dataset.productId);
            const productName = this.dataset.productName;
            const productPrice = parseFloat(this.dataset.productPrice);
            addToCart(productId, productName, productPrice);
        });
    });
    
    // Selezione tavolo
    const tableSelect = document.getElementById('table-select');
    if (tableSelect) {
        tableSelect.addEventListener('change', function() {
            const placeOrderBtn = document.getElementById('place-order-btn');
            placeOrderBtn.disabled = !this.value || cart.length === 0;
        });
    }
    
    // Pulsante ordina
    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', placeOrder);
    }
});

// Esponi funzioni globalmente per i pulsanti inline
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.increaseQuantity = increaseQuantity;
window.decreaseQuantity = decreaseQuantity;
window.placeOrder = placeOrder;

