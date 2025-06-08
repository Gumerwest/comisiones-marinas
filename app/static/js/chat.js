let socket = null;
let currentComisionId = null;
let currentTemaId = null;
let isInitialized = false;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectInterval = null;
let pingInterval = null;

window.chatManager = {
    init: function() {
    if (isInitialized) {
        console.log("⚠️ Chat ya inicializado, ignorando duplicado");
        return;
    }
    
    console.log("🚀 Inicializando sistema de chat...");
    isInitialized = true;


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
        const socketOptions = {
            transports: ['polling'],  // Solo polling, más confiable en Render
            upgrade: false,  // No intentar actualizar a websocket
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

        const protocol = window.location.protocol;
        const host = window.location.host;
        const socketUrl = `${protocol}//${host}`;

        console.log(`🔗 Conectando a: ${socketUrl}`);
        console.log(`🔧 Configuración: polling only (más estable en Render)`);

        socket = io(socketUrl, socketOptions);
        console.log("✅ Socket inicializado con configuración para Render");
    } catch (error) {
        console.error("❌ Error inicializando socket:", error);
        this.showError("No se pudo conectar al chat");
    }
},

    startPingKeepAlive: function() {
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

    // NUEVO: Limpiar conexiones previas
    if (currentComisionId && currentComisionId !== id) {
        console.log("🚪 Saliendo de comisión anterior:", currentComisionId);
        socket.emit('leave_comision', { comision_id: currentComisionId });
    }
    if (currentTemaId) {
        console.log("🚪 Saliendo de tema:", currentTemaId);
        socket.emit('leave_tema', { tema_id: currentTemaId });
        currentTemaId = null;
    }

    console.log("🏠 Uniéndose a comisión:", id);
    currentComisionId = id;

    socket.emit('join_comision', { comision_id: id });
    socket.emit('get_messages_comision', { comision_id: id, limit: 50, offset: 0 });
},


   joinTema: function(id) {
    if (!socket || !id) return;

    // NUEVO: Limpiar conexiones previas
    if (currentTemaId && currentTemaId !== id) {
        console.log("🚪 Saliendo de tema anterior:", currentTemaId);
        socket.emit('leave_tema', { tema_id: currentTemaId });
    }
    if (currentComisionId) {
        console.log("🚪 Saliendo de comisión:", currentComisionId);
        socket.emit('leave_comision', { comision_id: currentComisionId });
        currentComisionId = null;
    }

    console.log("💡 Uniéndose a tema:", id);
    currentTemaId = id;

    socket.emit('join_tema', { tema_id: id });
    socket.emit('get_messages_tema', { tema_id: id, limit: 50, offset: 0 });
},


    setupEventListeners: function() {
        if (!socket) return;

        const self = this;

        socket.on('connect', function() {
            console.log('✅ Conectado al servidor de chat');
            reconnectAttempts = 0;
            self.updateConnectionStatus('Conectado', 'success');

            setTimeout(() => {
                if (currentComisionId) {
                    self.joinComision(currentComisionId);
                }
                if (currentTemaId) {
                    self.joinTema(currentTemaId);
                }
            }, 500);
        });

        socket.on('connected', function(data) {
            console.log('🔗 Conexión confirmada:', data);
        });

        socket.on('disconnect', function(reason) {
            console.log('❌ Desconectado del servidor de chat:', reason);
            self.updateConnectionStatus('Desconectado', 'danger');

            if (reason !== 'io client disconnect' && reason !== 'transport close') {
                self.attemptReconnect();
            }
        });

        socket.on('connect_error', function(error) {
            console.error('❌ Error de conexión:', error);
            self.updateConnectionStatus('Error de conexión', 'warning');
            self.attemptReconnect();
        });

        socket.on('pong', function(data) {
            console.log('🏓 Pong recibido');
        });

        socket.on('joined_room', (data) => {
            console.log('✅ Unido a sala:', data);
        });

        socket.on('new_message_comision', (data) => {
            console.log('💬 Nuevo mensaje comisión:', data);
            self.displayMessage(data);
        });

        socket.on('new_message_tema', (data) => {
            console.log('💬 Nuevo mensaje tema:', data);
            self.displayMessage(data);
        });

        socket.on('messages_comision', (data) => {
            console.log('📜 Historial comisión:', data);
            self.displayMessages(data);
        });

        socket.on('messages_tema', (data) => {
            console.log('📜 Historial tema:', data);
            self.displayMessages(data);
        });

        socket.on('error', (data) => {
            console.error('⚠️ Error en chat:', data);
            if (data && data.message) {
                self.showTempMessage(data.message, 'warning');
            }
        });

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
                    comision_id: currentComisionId,
                    mensaje: mensaje
                });
            } else if (currentTemaId) {
                socket.emit('send_message_tema', {
                    tema_id: currentTemaId,
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

        const messageTime = data.fecha ? new Date(data.fecha).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        }) : new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatarHtml = isOwn ? '' : `
            <div class="message-avatar">
                ${data.usuario.initials || (data.usuario.nombre[0] + (data.usuario.apellidos ? data.usuario.apellidos[0] : ''))}
            </div>
        `;

        messageDiv.innerHTML = `
            <div class="message-container">
                ${avatarHtml}
                <div class="message-content-wrapper">
                    <div class="message-header">
                        ${!isOwn ? `<strong>${this.escapeHtml(data.usuario.nombre)} ${this.escapeHtml(data.usuario.apellidos || '')}</strong>` : 'Tú'}
                        <small class="message-time">${messageTime}</small>
                    </div>
                    <div class="message-content">${this.escapeHtml(data.mensaje)}</div>
                </div>
            </div>
        `;

        messagesDiv.appendChild(messageDiv);
        this.scrollToBottom();

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
            "'": '&#39;'
        };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    },

    cleanup: function() {
        if (pingInterval) {
            clearInterval(pingInterval);
            pingInterval = null;
        }

        if (socket) {
            socket.disconnect();
            socket = null;
        }

        console.log('🧹 Chat limpiado');
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
        const checkSocketIO = setInterval(() => {
            if (typeof io !== 'undefined') {
                clearInterval(checkSocketIO);
                console.log('✅ Socket.IO cargado, inicializando chat...');
                try {
                    window.chatManager.init();
                } catch (error) {
                    console.error('❌ Error inicializando chat:', error);
                    window.chatManager.showError('Error inicializando chat');
                }
            } else {
                console.log('⏳ Esperando que Socket.IO se cargue...');
            }
        }, 500);

        setTimeout(() => {
            clearInterval(checkSocketIO);
            if (typeof io === 'undefined') {
                console.error('❌ Socket.IO no se pudo cargar después de 10 segundos');
                window.chatManager.showError('No se pudo cargar el servicio de chat');
            }
        }, 10000);
    }
});

window.addEventListener('beforeunload', function() {
    if (window.chatManager) {
        window.chatManager.cleanup();
    }
});

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('👁️ Página oculta');
    } else {
        console.log('👁️ Página visible');
        if (socket && !socket.connected) {
            console.log('🔄 Reintentando conexión...');
            socket.connect();
        }
    }
});
