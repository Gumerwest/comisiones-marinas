// Funcionalidad de chat en tiempo real con Socket.IO

class ChatManager {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.currentType = null; // 'comision' o 'tema'
        this.currentId = null;
    }
    
    init() {
        // Conectar con Socket.IO
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Conectado al servidor de chat');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Desconectado del servidor de chat');
        });
        
        // Listeners para mensajes
        this.socket.on('new_message_comision', (data) => {
            this.addMessageToChat(data, 'comision');
        });
        
        this.socket.on('new_message_tema', (data) => {
            this.addMessageToChat(data, 'tema');
        });
        
        this.socket.on('messages_comision', (data) => {
            this.loadMessages(data.mensajes, 'comision');
        });
        
        this.socket.on('messages_tema', (data) => {
            this.loadMessages(data.mensajes, 'tema');
        });
    }
    
    joinComision(comisionId) {
        if (this.currentRoom) {
            this.socket.emit('leave_comision', { comision_id: this.currentId });
        }
        
        this.currentType = 'comision';
        this.currentId = comisionId;
        this.currentRoom = `comision_${comisionId}`;
        
        this.socket.emit('join_comision', { comision_id: comisionId });
        this.socket.emit('get_messages_comision', { comision_id: comisionId });
    }
    
    joinTema(temaId) {
        if (this.currentRoom) {
            this.socket.emit('leave_tema', { tema_id: this.currentId });
        }
        
        this.currentType = 'tema';
        this.currentId = temaId;
        this.currentRoom = `tema_${temaId}`;
        
        this.socket.emit('join_tema', { tema_id: temaId });
        this.socket.emit('get_messages_tema', { tema_id: temaId });
    }
    
    sendMessage(mensaje) {
        if (!this.currentRoom || !mensaje.trim()) return;
        
        if (this.currentType === 'comision') {
            this.socket.emit('send_message_comision', {
                comision_id: this.currentId,
                mensaje: mensaje
            });
        } else if (this.currentType === 'tema') {
            this.socket.emit('send_message_tema', {
                tema_id: this.currentId,
                mensaje: mensaje
            });
        }
    }
    
    loadMessages(mensajes, type) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;
        
        chatContainer.innerHTML = '';
        mensajes.forEach(msg => {
            this.addMessageToChat(msg, type, false);
        });
        
        // Scroll al final
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    addMessageToChat(data, type, scroll = true) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        
        const currentUserId = parseInt(chatContainer.dataset.currentUserId);
        const isOwnMessage = data.usuario.id === currentUserId;
        
        if (isOwnMessage) {
            messageDiv.classList.add('own-message');
        } else {
            messageDiv.classList.add('other-message');
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${data.usuario.nombre} ${data.usuario.apellidos}</strong>
                <small class="${isOwnMessage ? 'text-white-50' : 'text-muted'} ms-2">${data.fecha}</small>
            </div>
            <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        
        if (scroll) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar chat cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en una página con chat
    const chatForm = document.getElementById('chat-form');
    if (!chatForm) return;
    
    const chatManager = new ChatManager();
    chatManager.init();
    
    // Exponer globalmente para uso en templates
    window.chatManager = chatManager;
    
    // Configurar formulario de envío de mensajes
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        if (input && input.value.trim()) {
            chatManager.sendMessage(input.value);
            input.value = '';
        }
    });
    
    // Auto-unirse a la sala si estamos en una página de comisión o tema
    const comisionId = document.body.dataset.comisionId;
    const temaId = document.body.dataset.temaId;
    
    if (comisionId) {
        chatManager.joinComision(parseInt(comisionId));
    } else if (temaId) {
        chatManager.joinTema(parseInt(temaId));
    }
});
