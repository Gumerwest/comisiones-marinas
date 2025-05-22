// Funcionalidad JavaScript para la plataforma de Comisiones Marinas

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Marcar comentarios como leídos al hacer scroll
    const comentariosContainer = document.querySelector('.comentarios-container');
    if (comentariosContainer) {
        const comentariosNuevos = document.querySelectorAll('.comentario-nuevo');
        
        if (comentariosNuevos.length > 0) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const comentario = entry.target;
                        const comentarioId = comentario.dataset.comentarioId;
                        
                        // Marcar visualmente como leído
                        setTimeout(() => {
                            comentario.classList.remove('comentario-nuevo');
                        }, 1000);
                    }
                });
            }, { threshold: 0.5 });
            
            comentariosNuevos.forEach(comentario => {
                observer.observe(comentario);
            });
        }
    }
    
    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Previsualización de imágenes al subirlas
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.querySelector(`#preview-${this.id}`);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Confirmación para acciones destructivas
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.dataset.confirm || '¿Está seguro de que desea realizar esta acción?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
    
    // Auto-ocultar mensajes flash después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});
