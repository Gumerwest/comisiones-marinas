// Funcionalidad JavaScript mejorada para la plataforma de Comisiones Marinas

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    initializeTooltips();
    
    // Inicializar funcionalidades principales
    initializeComments();
    initializeFormValidation();
    initializeFilePreview();
    initializeConfirmActions();
    initializeAnimations();
    initializeSearch();
    
    console.log('🚢 Plataforma Comisiones Marinas - JavaScript inicializado');
});

// Inicializar tooltips de Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Gestión de comentarios mejorada
function initializeComments() {
    const comentariosContainer = document.querySelector('.comentarios-container');
    if (!comentariosContainer) return;
    
    const comentariosNuevos = document.querySelectorAll('.comentario-nuevo');
    
    if (comentariosNuevos.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const comentario = entry.target;
                    const comentarioId = comentario.dataset.comentarioId;
                    
                    // Marcar visualmente como leído después de 2 segundos
                    setTimeout(() => {
                        comentario.classList.remove('comentario-nuevo');
                        comentario.style.transform = 'scale(1.02)';
                        setTimeout(() => {
                            comentario.style.transform = 'scale(1)';
                        }, 200);
                    }, 2000);
                }
            });
        }, { 
            threshold: 0.7,
            rootMargin: '0px 0px -50px 0px'
        });
        
        comentariosNuevos.forEach(comentario => {
            observer.observe(comentario);
        });
    }
    
    // Mejorar el área de comentarios
    const comentarioTextarea = document.querySelector('textarea[name="contenido"]');
    if (comentarioTextarea) {
        comentarioTextarea.addEventListener('focus', function() {
            this.style.minHeight = '100px';
            this.parentElement.style.transform = 'scale(1.01)';
        });
        
        comentarioTextarea.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.style.minHeight = '';
                this.parentElement.style.transform = 'scale(1)';
            }
        });
        
        // Auto-expand textarea
        comentarioTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
}

// Validación de formularios mejorada
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Encontrar el primer campo inválido y hacer scroll hasta él
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Validación en tiempo real
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
}

// Previsualización de archivos mejorada
function initializeFilePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.querySelector(`#preview-${this.id}`);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    preview.style.opacity = '0';
                    preview.style.transform = 'scale(0.8)';
                    
                    // Animación de aparición
                    setTimeout(() => {
                        preview.style.transition = 'all 0.3s ease';
                        preview.style.opacity = '1';
                        preview.style.transform = 'scale(1)';
                    }, 100);
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Mejorar el diseño de inputs de archivo
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.className = 'file-input-wrapper';
        wrapper.style.position = 'relative';
        
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Ningún archivo seleccionado';
            let label = wrapper.querySelector('.file-label');
            if (!label) {
                label = document.createElement('small');
                label.className = 'file-label text-muted';
                wrapper.appendChild(label);
            }
            label.textContent = `Archivo: ${fileName}`;
        });
    });
}

// Confirmaciones mejoradas para acciones destructivas
function initializeConfirmActions() {
    const confirmActions = document.querySelectorAll('[data-confirm]');
    
    confirmActions.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.dataset.confirm || '¿Está seguro de que desea realizar esta acción?';
            const isDestructive = this.classList.contains('btn-danger') || 
                               this.textContent.toLowerCase().includes('eliminar') ||
                               this.textContent.toLowerCase().includes('rechazar');
            
            // Crear modal de confirmación personalizado para acciones destructivas
            if (isDestructive) {
                event.preventDefault();
                showCustomConfirm(message, () => {
                    // Si es un formulario, enviarlo
                    if (this.tagName === 'BUTTON' && this.form) {
                        this.form.submit();
                    } else if (this.tagName === 'A') {
                        window.location.href = this.href;
                    }
                });
            } else {
                // Confirmación estándar para acciones no destructivas
                if (!confirm(message)) {
                    event.preventDefault();
                }
            }
        });
    });
}

// Modal de confirmación personalizado
function showCustomConfirm(message, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i>Confirmar Acción
                    </h5>
                </div>
                <div class="modal-body">
                    <p class="mb-0">${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>Cancelar
                    </button>
                    <button type="button" class="btn btn-danger" id="confirm-action">
                        <i class="fas fa-check me-1"></i>Confirmar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    modal.querySelector('#confirm-action').addEventListener('click', () => {
        bootstrapModal.hide();
        onConfirm();
    });
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Animaciones y efectos visuales
function initializeAnimations() {
    // Animación de aparición para elementos
    const animatedElements = document.querySelectorAll('.fade-in-up, .card, .member-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'all 0.6s ease';
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
    
    // Efecto hover para tarjetas
    const cards = document.querySelectorAll('.card, .member-card, .function-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
    });
    
    // Animación para badges y elementos importantes
    const badges = document.querySelectorAll('.badge-leader, .badge');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Búsqueda en tiempo real (si existe un campo de búsqueda)
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.toLowerCase().trim();
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    });
}

// Función de búsqueda
function performSearch(query) {
    const searchableElements = document.querySelectorAll('.searchable, [data-searchable]');
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const matches = text.includes(query) || query === '';
        
        if (matches) {
            element.style.display = '';
            element.style.opacity = '1';
        } else {
            element.style.opacity = '0.3';
            element.style.transform = 'scale(0.95)';
        }
        
        element.style.transition = 'all 0.3s ease';
    });
}

// Utilidades adicionales
const Utils = {
    // Copiar texto al portapapeles
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copiado al portapapeles', 'success');
        });
    },
    
    // Mostrar notificación toast
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(toast);
        
        // Animación de entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        }, 100);
        
        // Auto-remove después de 3 segundos
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    },
    
    // Formatear fecha
    formatDate: function(date) {
        return new Intl.DateTimeFormat('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Exponer utilidades globalmente
window.ComisionesUtils = Utils;

// Mejoras de accesibilidad
document.addEventListener('keydown', function(e) {
    // Esc para cerrar modales
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
    
    // Ctrl+/ para mostrar shortcuts (si existe)
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        const shortcutsModal = document.querySelector('#shortcuts-modal');
        if (shortcutsModal) {
            const modal = new bootstrap.Modal(shortcutsModal);
            modal.show();
        }
    }
});

// Performance monitoring
const performanceObserver = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
        if (entry.loadTime > 2000) {
            console.warn(`Elemento lento detectado: ${entry.name} - ${entry.loadTime}ms`);
        }
    });
});

if ('PerformanceObserver' in window) {
    performanceObserver.observe({ entryTypes: ['navigation', 'resource'] });
}

// Error handling global
window.addEventListener('error', function(e) {
    console.error('Error detectado:', e.error);
    // En producción, aquí se podría enviar el error a un servicio de monitoreo
});

// Service Worker registration (para futuras mejoras PWA)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/sw.js')
        //     .then((registration) => console.log('SW registered'))
        //     .catch((error) => console.log('SW registration failed'));
    });
}
