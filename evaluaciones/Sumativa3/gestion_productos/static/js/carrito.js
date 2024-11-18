// Funciones del carrito
const carrito = {
    init: function() {
        this.sidebar = document.getElementById('carritoSidebar');
        this.contador = document.getElementById('carrito-contador');
        this.itemsContainer = document.getElementById('carritoItems');
        this.toggleButton = document.querySelector('.carrito-toggle');
        
        // Event Listeners
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => this.toggleSidebar());
        }

        document.addEventListener('click', (e) => {
            if (e.target.matches('.agregar-al-carrito')) {
                e.preventDefault();
                const productoId = e.target.dataset.productoId;
                this.agregarProducto(productoId);
            }
        });

        // Cargar carrito inicial
        this.actualizarCarrito();
    },

    toggleSidebar: function() {
        this.sidebar.classList.toggle('translate-x-full');
    },

    async agregarProducto: function(productoId) {
        try {
            const response = await fetch('/carrito/agregar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    cantidad: 1
                })
            });

            const data = await response.json();
            if (response.ok) {
                this.actualizarContador(data.total_items);
                this.actualizarListaCarrito(data.cart);
                this.mostrarMensaje('Producto agregado al carrito', 'success');
            } else {
                this.mostrarMensaje(data.error, 'error');
            }
        } catch (error) {
            this.mostrarMensaje('Error al agregar el producto', 'error');
        }
    },

    async quitarProducto: function(productoId) {
        try {
            const response = await fetch('/carrito/quitar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    producto_id: productoId
                })
            });

            const data = await response.json();
            if (response.ok) {
                this.actualizarContador(data.total_items);
                this.actualizarListaCarrito(data.cart);
                this.mostrarMensaje('Producto eliminado del carrito', 'success');
            }
        } catch (error) {
            this.mostrarMensaje('Error al eliminar el producto', 'error');
        }
    },

    async actualizarCantidad: function(productoId, cantidad) {
        try {
            const response = await fetch('/carrito/actualizar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    cantidad: cantidad
                })
            });

            const data = await response.json();
            if (response.ok) {
                this.actualizarContador(data.total_items);
                this.actualizarListaCarrito(data.cart);
            }
        } catch (error) {
            this.mostrarMensaje('Error al actualizar el carrito', 'error');
        }
    },

    async actualizarCarrito: function() {
        try {
            const response = await fetch('/carrito/obtener/');
            const data = await response.json();
            if (response.ok) {
                this.actualizarContador(data.total_items);
                this.actualizarListaCarrito(data.cart);
            }
        } catch (error) {
            console.error('Error al obtener el carrito:', error);
        }
    },

    actualizarContador: function(total) {
        if (this.contador) {
            this.contador.textContent = total;
        }
    },

    actualizarListaCarrito: function(cart) {
        if (!this.itemsContainer) return;
        
        this.itemsContainer.innerHTML = '';
        let total = 0;

        Object.entries(cart).forEach(([id, item]) => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const itemHTML = `
                <div class="flex items-center justify-between p-2 border-b">
                    <div class="flex items-center">
                        ${item.imagen ? 
                            `<img src="${item.imagen}" alt="${item.nombre}" class="w-12 h-12 object-cover rounded">` :
                            '<div class="w-12 h-12 bg-gray-200 rounded"></div>'
                        }
                        <div class="ml-2">
                            <h4 class="font-semibold">${item.nombre}</h4>
                            <p class="text-sm text-gray-600">$${item.precio}</p>
                        </div>
                    </div>
                    <div class="flex items-center">
                        <input type="number" 
                               value="${item.cantidad}" 
                               min="1" 
                               class="w-16 p-1 border rounded"
                               onchange="carrito.actualizarCantidad('${id}', this.value)">
                        <button onclick="carrito.quitarProducto('${id}')" 
                                class="ml-2 text-red-500 hover:text-red-700">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>`;
            this.itemsContainer.insertAdjacentHTML('beforeend', itemHTML);
        });

        // Agregar total
        const totalHTML = `
            <div class="mt-4 p-4 bg-gray-50 rounded">
                <div class="flex justify-between items-center">
                    <span class="font-semibold">Total:</span>
                    <span class="font-bold text-lg">$${total.toFixed(2)}</span>
                </div>
            </div>`;
        this.itemsContainer.insertAdjacentHTML('beforeend', totalHTML);
    },

    mostrarMensaje: function(mensaje, tipo) {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 p-4 rounded-lg ${
            tipo === 'error' ? 'bg-red-500' : 'bg-green-500'
        } text-white`;
        toast.textContent = mensaje;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    getCsrfToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => carrito.init());