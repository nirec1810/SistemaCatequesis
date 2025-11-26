document.addEventListener("DOMContentLoaded", function() {
    // Selects
    async function poblarSelects() {
        try {
            // Familias
            const resFam = await fetch('/api/familias');
            if (resFam.ok) {
                const familias = await resFam.json();
                const famSel = document.querySelector('select[name="familia"]');
                if (famSel) {
                    famSel.innerHTML = '<option value="">-- Seleccione familia (opcional) --</option>';
                    familias.forEach(f => {
                        const opt = document.createElement('option');
                        opt.value = f.idFamilia;
                        opt.textContent = `${f.nombreContacto} (${f.telefono || 'sin teléfono'})`;
                        famSel.appendChild(opt);
                    });
                }
            }

            // Notificaciones
            const resNot = await fetch('/api/notificaciones');
            if (resNot.ok) {
                const nots = await resNot.json();
                const notSel = document.querySelector('select[name="notificacion"]');
                if (notSel) {
                    notSel.innerHTML = '<option value="">-- Seleccione notificación (opcional) --</option>';
                    nots.forEach(n => {
                        const opt = document.createElement('option');
                        opt.value = n.idNotificacion;
                        opt.textContent = `${n.tipo} - ${n.mensaje.slice(0,40)}...`;
                        notSel.appendChild(opt);
                    });
                }
            }
        } catch (err) {
            console.error("Error cargando selects:", err);
        }
    }

    poblarSelects();

    // Validar
    const form = document.querySelector('form[data-form="registrar-catequizando"]');
    if (form) {
        form.addEventListener('submit', function(evt) {
            // simple validación cliente
            const nombre = form.querySelector('input[name="nombre"]').value.trim();
            const apellidos = form.querySelector('input[name="apellidos"]').value.trim();
            const fecha = form.querySelector('input[name="fechaNacimiento"]').value;

            if (!nombre || !apellidos || !fecha) {
                alert("Por favor complete los campos: Nombre, Apellidos y Fecha de Nacimiento.");
                evt.preventDefault();
                return;
            }

            // Desactivar botón y mostrar mensaje
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Guardando...";
            }
        });
    }

    // Listado
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const q = this.value.toLowerCase();
            const rows = document.querySelectorAll('#tabla-catequizandos tbody tr');
            rows.forEach(row => {
                const texto = row.textContent.toLowerCase();
                row.style.display = texto.indexOf(q) !== -1 ? '' : 'none';
            });
        });
    }

    // Confirmaciones 
    document.querySelectorAll('form[data-confirm]').forEach(f => {
        f.addEventListener('submit', function(e){
            const msg = f.getAttribute('data-confirm') || '¿Confirmar acción?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});
