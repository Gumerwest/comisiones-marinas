// Sistema de chat en tiempo real mejorado y más robusto
let socket = null;
let currentComisionId = null;
let currentTemaId = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectInterval = null;

window.chatManager = {
    init: function() {
        console.log("Inicializando sistema de chat...");
        
        // Verificar si SocketIO está disponible
        if (typeof io === 'undefined') {
            console.error("Socket.IO no está disponible");
            this.showError("Servicio de chat no disponible");
            return;
        }
        
        this.initializeSocket();
        this.setupEventListeners();
        this.getContextFromPage();
    },
    
    initializeSocket: function() {
        try {
            // Configuración más robusta para Render
            socket = io({
                transports: ['polling', 'websocket'],
                upgrade: true,
                rememberUpgrade: true,
                timeout: 20000,
                forceNew: true,
                reconnection: true,
                reconnectionAttempts: maxReconnectAttempts,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000
            });
            
            console.log("Socket inicializado");
        } catch (error) {
            console.error("Error inicializando socket:", error);
            this.showError("No se pudo conectar al chat");
        }
    },
    
    getContextFromPage: function() {
        // Obtener IDs de la página actual
        const comisionId = document.body.dataset.comisionId;
        const temaId = document.body.dataset.temaId;
        
        if (comisionId) {
            this.joinComision(comisionId);
        }
        if (temaId) {
            this.joinTema(temaId);
        }
    },
    
    joinComision: function(id) {
        if (!socket || !id) return;
        
        console.log("Uniéndose a comisión:", id);
        currentComisionId = id;
        currentTemaId = null;
        
        socket.emit('join_comision', { comision_id: parseInt(id) });
        
        // Solicitar mensajes después de un breve delay
        setTimeout(() => {
            socket.emit('get_messages_comision', { 
                comision_id: parseInt(id),
                limit: 50,
                offset: 0
            });
        }, 500);
    },
    
    joinTema: function(id) {
        if (!socket || !id) return;
        
        console.log("Uniéndose a tema:", id);
        currentTemaId = id;
        currentComisionId = null;
        
        socket.emit('join_tema', { tema_id: parseInt(id) });
        
        // Solicitar mensajes después de un breve delay
        setTimeout(() => {
            socket.emit('get_messages_tema', { 
                tema_id: parseInt(id),
                limit: 50,
                offset: 0
            });
        }, 500);
    },
    
    setupEventListeners: function() {
        if (!socket) return;
        
        const self = this;
        
        // Eventos de conexión
        socket.on('connect', function() {
            console.log('✅ Conectado al servidor de chat');
            reconnectAttempts = 0;
            self.updateConnectionStatus('Conectado', 'success');
            
            // Reunirse a las salas después de reconectar
            if (currentComisionId) {
                self.joinComision(currentComisionId);
            }
            if (currentTemaId) {
                self.joinTema(currentTemaId);
            }
        });
        
        socket.on('disconnect', function(reason) {
            console.log('❌ Desconectado del servidor de chat:', reason);
            self.updateConnectionStatus('Desconectado', 'danger');
            
            // Intentar reconectar si no fue desconexión manual
            if (reason !== 'io client disconnect') {
                self.attemptReconnect();
            }
        });
        
        socket.on('connect_error', function(error) {
            console.error('Error de conexión:', error);
            self.updateConnectionStatus('Error de conexión', 'warning');
            self.attemptReconnect();
        });
        
        // Eventos de mensajes
        socket.on('new_message_comision', (data) => {
            console.log('Nuevo mensaje en comisión:', data);
            self.displayMessage(data);
        });
        
        socket.on('new_message_tema', (data) => {
            console.log('Nuevo mensaje en tema:', data);
            self.displayMessage(data);
        });
        
        socket.on('messages_comision', (data) => {
            console.log('Mensajes de comisión recibidos:', data);
            self.displayMessages(data);
        });
        
        socket.on('messages_tema', (data) => {
            console.log('Mensajes de tema recibidos:', data);
            self.displayMessages(data);
        });
        
        // Eventos de sala
        socket.on('joined_room', (data) => {
            console.log('Unido a sala:', data);
        });
        
        // Configurar formulario de chat
        this.setupChatForm();
    },
    
    setupChatForm: function() {
        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
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
        if (!input || !socket || !socket.connected) {
            console.log('No conectado o input no encontrado');
            this.showError('No está conectado al chat');
            return;
        }
        
        const mensaje = input.value.trim();
        if (!mensaje) return;
        
        console.log('Enviando mensaje:', mensaje);
        
        try {
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
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.showError('Error enviando mensaje');
        }
    },
    
    displayMessage: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv || !data) return;
        
        const currentUserId = messagesDiv.dataset.currentUserId;
        const isOwn = String(data.usuario.id) === String(currentUserId);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isOwn ? 'own-message' : 'other-message'}`;
        messageDiv.style.animation = 'slideIn 0.3s ease-out';
        
        const messageTime = new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                ${!isOwn ? `<strong>${this.escapeHtml(data.usuario.nombre)} ${this.escapeHtml(data.usuario.apellidos)}</strong>` : 'Tú'}
                <small class="ms-2">${data.fecha || messageTime}</small>
            </div>
            <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
        `;
        
        messagesDiv.appendChild(messageDiv);
        this.scrollToBottom();
    },
    
    displayMessages: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv || !data || !data.mensajes) return;
        
        messagesDiv.innerHTML = '';
        
        if (data.mensajes.length === 0) {
            messagesDiv.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-comments fa-2x mb-2"></i>
                    <br><small>No hay mensajes aún</small>
                    <br><small>¡Sé el primero en escribir!</small>
                </div>
            `;
            return;
        }
        
        data.mensajes.forEach(msg => {
            this.displayMessage(msg);
        });
        
        this.scrollToBottom();
    },
    
    scrollToBottom: function() {
        const messagesDiv = document.getElementById('chat-messages');
        if (messagesDiv) {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    },
    
    updateConnectionStatus: function(status, type) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            const icon = type === 'success' ? '●' : type === 'danger' ? '○' : '◐';
            const className = `text-${type}`;
            
            statusElement.innerHTML = `${icon} ${status}`;
            statusElement.className = `float-end ${className}`;
        }
    },
    
    attemptReconnect: function() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            console.log('Máximo de intentos de reconexión alcanzado');
            this.showError('No se pudo reconectar al chat');
            return;
        }
        
        reconnectAttempts++;
        console.log(`Intento de reconexión ${reconnectAttempts}/${maxReconnectAttempts}`);
        
        this.updateConnectionStatus(`Reconectando... (${reconnectAttempts}/${maxReconnectAttempts})`, 'warning');
        
        setTimeout(() => {
            if (socket && !socket.connected) {
                socket.connect();
            }
        }, 2000 * reconnectAttempts);
    },
    
    showError: function(message) {
        const messagesDiv = document.getElementById('chat-messages');
        if (messagesDiv) {
            messagesDiv.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2 text-warning"></i>
                    <br><strong>${message}</strong>
                    <br><small>Actualice la página para reintentar</small>
                    <br><button class="btn btn-sm btn-outline-primary mt-2" onclick="location.reload()">
                        <i class="fas fa-refresh"></i> Actualizar
                    </button>
                </div>
            `;
        }
        
        this.updateConnectionStatus('Error', 'danger');
    },
    
    escapeHtml: function(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
        // Dar tiempo para que se carguen las librerías
        setTimeout(() => {
            try {
                window.chatManager.init();
            } catch (error) {
                console.error('Error inicializando chat:', error);
                window.chatManager.showError('Error inicializando chat');
            }
        }, 1000);
    }
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (socket && socket.connected) {
        socket.disconnect();
    }
});
