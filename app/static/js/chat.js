// Sistema de chat en tiempo real para comisiones y temas
const socket = io();
let currentComisionId = null;
let currentTemaId = null;

window.chatManager = {
    init: function() {
        console.log("Inicializando sistema de chat...");
        
        // Obtener IDs de la página actual
        const comisionId = document.body.dataset.comisionId;
        const temaId = document.body.dataset.temaId;
        
        // Unirse a la sala correspondiente
        if (comisionId) {
            this.joinComision(comisionId);
        }
        if (temaId) {
            this.joinTema(temaId);
        }
        
        // Configurar todos los eventos
        this.setupEventListeners();
    },
    
    joinComision: function(id) {
        console.log("Uniéndose a comisión:", id);
        currentComisionId = id;
        currentTemaId = null;
        socket.emit('join_comision', { comision_id: id });
        socket.emit('get_messages_comision', { comision_id: id });
    },
    
    joinTema: function(id) {
        console.log("Uniéndose a tema:", id);
        currentTemaId = id;
        currentComisionId = null;
        socket.emit('join_tema', { tema_id: id });
        socket.emit('get_messages_tema', { tema_id: id });
    },
    
    setupEventListeners: function() {
        // Escuchar mensajes nuevos
        socket.on('new_message_comision', (data) => {
            this.displayMessage(data);
        });
        
        socket.on('new_message_tema', (data) => {
            this.displayMessage(data);
        });
        
        socket.on('messages_comision', (data) => {
            this.displayMessages(data);
        });
        
        socket.on('messages_tema', (data) => {
            this.displayMessages(data);
        });
        
        // Manejar conexión
        socket.on('connected', (data) => {
            console.log('Conectado al chat, usuario ID:', data.user_id);
        });
        
        socket.on('joined_room', (data) => {
            console.log('Unido a la sala:', data.room);
        });
        
        // Configurar formulario de chat
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        // Configurar tecla Enter en el input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    },
    
    sendMessage: function() {
        const input = document.getElementById('chat-input');
        if (!input) return;
        
        const mensaje = input.value.trim();
        if (!mensaje) return;
        
        // Enviar mensaje según el contexto
        if (currentComisionId) {
            socket.emit('send_message_comision', {
                comision_id: currentComisionId,
                mensaje: mensaje
            });
        } else if (currentTemaId) {
            socket.emit('send_message_tema', {
                tema_id: currentTemaId,
                mensaje: mensaje
            });
        }
        
        // Limpiar input
        input.value = '';
        input.focus();
    },
    
    displayMessage: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv) return;
        
        // Obtener ID del usuario actual
        const currentUserId = messagesDiv.dataset.currentUserId;
        const isOwn = data.usuario.id == currentUserId;
        
        // Crear elemento del mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isOwn ? 'own-message' : 'other-message'}`;
        messageDiv.style.opacity = '0';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                ${!isOwn ? `<strong>${data.usuario.nombre} ${data.usuario.apellidos}</strong>` : 'Tú'}
                <small class="ms-2">${data.fecha}</small>
            </div>
            <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
        `;
        
        // Añadir al contenedor
        messagesDiv.appendChild(messageDiv);
        
        // Animación de entrada
        setTimeout(() => {
            messageDiv.style.transition = 'opacity 0.3s ease';
            messageDiv.style.opacity = '1';
        }, 10);
        
        // Scroll al final
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // Sonido de notificación si no es propio
        if (!isOwn) {
            this.playNotificationSound();
        }
    },
    
    displayMessages: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv || !data.mensajes) return;
        
        // Limpiar mensajes anteriores
        messagesDiv.innerHTML = '';
        
        // Si no hay mensajes
        if (data.mensajes.length === 0) {
            messagesDiv.innerHTML = `
                <div class="text-center text-muted mt-5">
                    <i class="fas fa-comments fa-3x mb-3 opacity-50"></i>
                    <p>No hay mensajes aún. ¡Sé el primero en escribir!</p>
                </div>
            `;
            return;
        }
        
        // Mostrar cada mensaje
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
    },
    
    playNotificationSound: function() {
        // Crear un sonido simple de notificación
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSZuu+3XqVYUCjyS0+/+sEEGRKriw3VYCQNF09yGORM');
            audio.volume = 0.3;
            audio.play();
        } catch (e) {
            // Si falla el sonido, no pasa nada
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en una página con chat
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
        window.chatManager.init();
    }
});

// Reconectar si se pierde la conexión
socket.on('disconnect', () => {
    console.log('Desconectado del servidor de chat');
});

socket.on('connect', () => {
    console.log('Reconectado al servidor de chat');
    // Volver a unirse a las salas si estábamos en alguna
    if (currentComisionId) {
        window.chatManager.joinComision(currentComisionId);
    } else if (currentTemaId) {
        window.chatManager.joinTema(currentTemaId);
    }
});
