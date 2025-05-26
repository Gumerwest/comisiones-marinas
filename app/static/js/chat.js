// Sistema de chat en tiempo real simplificado
let socket = null;
let currentComisionId = null;
let currentTemaId = null;

window.chatManager = {
    init: function() {
        console.log("Inicializando sistema de chat...");
        
        // Inicializar Socket.IO
        socket = io({
            transports: ['polling'],
            upgrade: false
        });
        
        // Obtener IDs de la página actual
        const comisionId = document.body.dataset.comisionId;
        const temaId = document.body.dataset.temaId;
        
        if (comisionId) {
            this.joinComision(comisionId);
        }
        if (temaId) {
            this.joinTema(temaId);
        }
        
        this.setupEventListeners();
    },
    
    joinComision: function(id) {
        console.log("Uniéndose a comisión:", id);
        currentComisionId = id;
        currentTemaId = null;
        socket.emit('join_comision', { comision_id: parseInt(id) });
        socket.emit('get_messages_comision', { comision_id: parseInt(id) });
    },
    
    joinTema: function(id) {
        console.log("Uniéndose a tema:", id);
        currentTemaId = id;
        currentComisionId = null;
        socket.emit('join_tema', { tema_id: parseInt(id) });
        socket.emit('get_messages_tema', { tema_id: parseInt(id) });
    },
    
    setupEventListeners: function() {
        const self = this;
        
        // Eventos de conexión
        socket.on('connect', function() {
            console.log('Conectado al servidor de chat');
            const status = document.getElementById('connection-status');
            if (status) {
                status.textContent = '● Conectado';
                status.className = 'text-success';
            }
        });
        
        socket.on('disconnect', function() {
            console.log('Desconectado del servidor de chat');
            const status = document.getElementById('connection-status');
            if (status) {
                status.textContent = '○ Desconectado';
                status.className = 'text-danger';
            }
        });
        
        // Escuchar mensajes nuevos
        socket.on('new_message_comision', (data) => {
            self.displayMessage(data);
        });
        
        socket.on('new_message_tema', (data) => {
            self.displayMessage(data);
        });
        
        socket.on('messages_comision', (data) => {
            self.displayMessages(data);
        });
        
        socket.on('messages_tema', (data) => {
            self.displayMessages(data);
        });
        
        // Configurar formulario de chat
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                self.sendMessage();
            });
        }
        
        // Configurar tecla Enter
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    self.sendMessage();
                }
            });
        }
    },
    
    sendMessage: function() {
        const input = document.getElementById('chat-input');
        if (!input || !socket || !socket.connected) {
            console.log('No conectado o input no encontrado');
            return;
        }
        
        const mensaje = input.value.trim();
        if (!mensaje) return;
        
        console.log('Enviando mensaje:', mensaje);
        
        if (currentComisionId) {
            socket.emit('send_message_comision', {
                comision_id: parseInt(currentComisionId),
                mensaje: mensaje
            });
        } else if (currentTemaId) {
            socket.emit('send_message_tema', {
                tema_id: parseInt(currentTemaId),
                mensaje: mensaje
            });
        }
        
        input.value = '';
        input.focus();
    },
    
    displayMessage: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv) return;
        
        const currentUserId = messagesDiv.dataset.currentUserId;
        const isOwn = String(data.usuario.id) === String(currentUserId);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isOwn ? 'own-message' : 'other-message'}`;
        
        messageDiv.innerHTML = `
            <div class="message-header">
                ${!isOwn ? `<strong>${data.usuario.nombre} ${data.usuario.apellidos}</strong>` : 'Tú'}
                <small class="ms-2">${data.fecha}</small>
            </div>
            <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
        `;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    },
    
    displayMessages: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv || !data.mensajes) return;
        
        messagesDiv.innerHTML = '';
        
        if (data.mensajes.length === 0) {
            messagesDiv.innerHTML = `
                <div class="text-center text-muted">
                    <small>No hay mensajes aún</small>
                </div>
            `;
            return;
        }
        
        data.mensajes.forEach(msg => {
            this.displayMessage(msg);
        });
    },
    
    escapeHtml: function(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
        setTimeout(() => {
            window.chatManager.init();
        }, 500);
    }
});
