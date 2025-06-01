// Sistema de chat mejorado y más robusto para Render
let socket = null;
let currentComisionId = null;
let currentTemaId = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectInterval = null;
let pingInterval = null;

window.chatManager = {
    init: function() {
        console.log("🚀 Inicializando sistema de chat...");
        
        // Verificar si SocketIO está disponible
        if (typeof io === 'undefined') {
            console.error("❌ Socket.IO no está disponible");
            this.showError("Servicio de chat no disponible");
            return;
        }
        
        this.initializeSocket();
        this.setupEventListeners();
        this.getContextFromPage();
        this.startPingKeepAlive();
    },
    
    initializeSocket: function() {
        try {
            // Configuración optimizada para Render
            const socketOptions = {
                transports: ['polling', 'websocket'],
                upgrade: true,
                rememberUpgrade: false, // Forzar polling en Render
                timeout: 30000,
                forceNew: true,
                reconnection: true,
                reconnectionAttempts: maxReconnectAttempts,
                reconnectionDelay: 2000,
                reconnectionDelayMax: 10000,
                randomizationFactor: 0.5,
                pingTimeout: 60000,
                pingInterval: 25000
            };
            
            socket = io(socketOptions);
            console.log("✅ Socket inicializado con configuración para Render");
        } catch (error) {
            console.error("❌ Error inicializando socket:", error);
            this.showError("No se pudo conectar al chat");
        }
    },
    
    startPingKeepAlive: function() {
        // Enviar ping cada 20 segundos para mantener conexión activa
        if (pingInterval) {
            clearInterval(pingInterval);
        }
        
        pingInterval = setInterval(() => {
            if (socket && socket.connected) {
                socket.emit('ping');
            }
        }, 20000);
    },
    
    getContextFromPage: function() {
        // Obtener IDs de la página actual
        const comisionId = document.body.dataset.comisionId;
        const temaId = document.body.dataset.temaId;
        
        console.log(`📍 Contexto: Comisión=${comisionId}, Tema=${temaId}`);
        
        if (comisionId) {
            this.joinComision(comisionId);
        }
        if (temaId) {
            this.joinTema(temaId);
        }
    },
    
    joinComision: function(id) {
        if (!socket || !id) return;
        
        console.log("🏠 Uniéndose a comisión:", id);
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
        }, 1000);
    },
    
    joinTema: function(id) {
        if (!socket || !id) return;
        
        console.log("💡 Uniéndose a tema:", id);
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
        }, 1000);
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
            setTimeout(() => {
                if (currentComisionId) {
                    self.joinComision(currentComisionId);
                }
                if (currentTemaId) {
                    self.joinTema(currentTemaId);
                }
            }, 500);
        });
        
        socket.on('disconnect', function(reason) {
            console.log('❌ Desconectado del servidor de chat:', reason);
            self.updateConnectionStatus('Desconectado', 'danger');
            
            // Intentar reconectar si no fue desconexión manual
            if (reason !== 'io client disconnect' && reason !== 'transport close') {
                self.attemptReconnect();
            }
        });
        
        socket.on('connect_error', function(error) {
            console.error('❌ Error de conexión:', error);
            self.updateConnectionStatus('Error de conexión', 'warning');
            self.attemptReconnect();
        });
        
        // Respuesta a ping
        socket.on('pong', function(data) {
            console.log('🏓 Pong recibido');
        });
        
        // Eventos de mensajes
        socket.on('new_message_comision', (data) => {
            console.log('📨 Nuevo mensaje en comisión:', data);
            self.displayMessage(data);
        });
        
        socket.on('new_message_tema', (data) => {
            console.log('💬 Nuevo mensaje en tema:', data);
            self.displayMessage(data);
        });
        
        socket.on('messages_comision', (data) => {
            console.log('📥 Mensajes de comisión recibidos:', data.total || 0);
            self.displayMessages(data);
        });
        
        socket.on('messages_tema', (data) => {
            console.log('📥 Mensajes de tema recibidos:', data.total || 0);
            self.displayMessages(data);
        });
        
        // Eventos de sala
        socket.on('joined_room', (data) => {
            console.log('🚪 Unido a sala:', data.room);
            self.updateConnectionStatus(`Conectado (${data.type})`, 'success');
        });
        
        socket.on('left_room', (data) => {
            console.log('👋 Salió de sala:', data.room);
        });
        
        // Manejo de errores
        socket.on('error', (data) => {
            console.error('❌ Error del servidor:', data.message);
            self.showError(data.message || 'Error del servidor');
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
            
            // Limitar longitud del mensaje
            chatInput.addEventListener('input', (e) => {
                if (e.target.value.length > 1000) {
                    e.target.value = e.target.value.substring(0, 1000);
                    this.showTempMessage('Mensaje limitado a 1000 caracteres', 'warning');
                }
            });
        }
    },
    
    sendMessage: function() {
        const input = document.getElementById('chat-input');
        if (!input || !socket || !socket.connected) {
            console.log('❌ No conectado o input no encontrado');
            this.showTempMessage('No está conectado al chat', 'danger');
            return;
        }
        
        const mensaje = input.value.trim();
        if (!mensaje) return;
        
        if (mensaje.length > 1000) {
            this.showTempMessage('Mensaje demasiado largo (máximo 1000 caracteres)', 'warning');
            return;
        }
        
        console.log('📤 Enviando mensaje:', mensaje.substring(0, 50) + '...');
        
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
            console.error('❌ Error enviando mensaje:', error);
            this.showTempMessage('Error enviando mensaje', 'danger');
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
        
        const messageTime = data.fecha || new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        // Crear avatar con iniciales
        const avatarHtml = isOwn ? '' : `
            <div class="message-avatar">
                ${data.usuario.initials || (data.usuario.nombre[0] + data.usuario.apellidos[0])}
            </div>
        `;
        
        messageDiv.innerHTML = `
            <div class="message-container">
                ${avatarHtml}
                <div class="message-content-wrapper">
                    <div class="message-header">
                        ${!isOwn ? `<strong>${this.escapeHtml(data.usuario.nombre)} ${this.escapeHtml(data.usuario.apellidos)}</strong>` : 'Tú'}
                        <small class="message-time">${messageTime}</small>
                    </div>
                    <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
                </div>
            </div>
        `;
        
        messagesDiv.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Efecto de aparición
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
    },
    
    displayMessages: function(data) {
        const messagesDiv = document.getElementById('chat-messages');
        if (!messagesDiv || !data || !data.mensajes) return;
        
        messagesDiv.innerHTML = '';
        
        if (data.mensajes.length === 0) {
            messagesDiv.innerHTML = `
                <div class="empty-chat text-center py-4">
                    <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                    <h6 class="text-muted">No hay mensajes aún</h6>
                    <small class="text-muted">¡Sé el primero en escribir!</small>
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
            const icons = {
                'success': '●',
                'danger': '○',
                'warning': '◐'
            };
            
            const icon = icons[type] || '◐';
            const className = `text-${type}`;
            
            statusElement.innerHTML = `${icon} ${status}`;
            statusElement.className = `float-end ${className}`;
            
            console.log(`🔔 Estado: ${status}`);
        }
    },
    
    attemptReconnect: function() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            console.log('❌ Máximo de intentos de reconexión alcanzado');
            this.showError('No se pudo reconectar al chat. Actualice la página.');
            return;
        }
        
        reconnectAttempts++;
        console.log(`🔄 Intento de reconexión ${reconnectAttempts}/${maxReconnectAttempts}`);
        
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
                <div class="error-state text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h6 class="text-warning">${message}</h6>
                    <small class="text-muted">Actualice la página para reintentar</small>
                    <br>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="location.reload()">
                        <i class="fas fa-refresh"></i> Actualizar
                    </button>
                </div>
            `;
        }
        
        this.updateConnectionStatus('Error', 'danger');
    },
    
    showTempMessage: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = `
            top: 80px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove después de 3 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
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
    },
    
    cleanup: function() {
        // Limpiar intervalos
        if (pingInterval) {
            clearInterval(pingInterval);
            pingInterval = null;
        }
        
        // Desconectar socket
        if (socket) {
            socket.disconnect();
            socket = null;
        }
        
        console.log('🧹 Chat limpiado');
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
                console.error('❌ Error inicializando chat:', error);
                window.chatManager.showError('Error inicializando chat');
            }
        }, 2000); // Aumentar delay para Render
    }
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (window.chatManager) {
        window.chatManager.cleanup();
    }
});

// Manejar cambios de visibilidad de la página
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Página oculta - reducir actividad
        console.log('👁️ Página oculta');
    } else {
        // Página visible - reactivar si es necesario
        console.log('👁️ Página visible');
        if (socket && !socket.connected) {
            console.log('🔄 Reintentando conexión...');
            socket.connect();
        }
    }
});
