from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import get_connection

app = Flask(__name__)
app.secret_key = "secret_key_123"

# Ruta principal /Home
@app.route("/")
def index():
    return render_template("index.html")

# Formulario: Registrar Catequizando
@app.route("/registrar-catequizando")
def registrar_catequizando():
    return render_template("registrar_catequizando.html")

# Procesar el formulario
@app.route("/guardar-catequizando", methods=["POST"])
def guardar_catequizando():

    nombre = request.form["nombre"]
    apellidos = request.form["apellidos"]
    fechaNacimiento = request.form["fechaNacimiento"]
    documentoIdentidad = request.form["documentoIdentidad"]
    feBautismo = request.form.get("feBautismo", 0)

    # Datos de la familia
    familia_existente = request.form.get("familia_existente")

    nuevo_nombre = request.form.get("nuevo_nombre")
    nuevo_correo = request.form.get("nuevo_correo")
    nuevo_telefono = request.form.get("nuevo_telefono")
    nuevo_direccion = request.form.get("nuevo_direccion")

    conn = get_connection()
    cursor = conn.cursor()

    # Caso Usar familia existente
    if familia_existente and familia_existente != "":
        familia_id = int(familia_existente)

    # Caso Crear nueva familia
    else:
        if not nuevo_nombre or nuevo_nombre.strip() == "":
            flash("Debe ingresar el nombre del familiar.", "danger")
            return redirect(url_for("registrar_catequizando"))

        nuevo_correo = nuevo_correo or ""
        nuevo_telefono = nuevo_telefono or ""
        nuevo_direccion = nuevo_direccion or ""

        try:
            cursor.execute("""
                INSERT INTO Administrativo.Familia
                (nombreContacto, correo, telefono, direccion)
                OUTPUT INSERTED.idFamilia
                VALUES (?, ?, ?, ?)
            """, (nuevo_nombre.strip(), nuevo_correo, nuevo_telefono, nuevo_direccion))

            row = cursor.fetchone()

            if not row or row[0] is None:
                raise Exception("No se pudo obtener el ID de la familia creada.")

            familia_id = int(row[0])

            conn.commit()

        except Exception as e:
            conn.rollback()
            flash(f"Error al registrar familia: {str(e)}", "danger")
            return redirect(url_for("registrar_catequizando"))

    # Notificación por defecto
    notificacion_id = 1

    # Insertar catequizando 
    try:
        cursor.execute("""
            INSERT INTO Administrativo.Catequizando
            (nombre, apellidos, fechaNacimiento, documentoIdentidad, feBautismo,
             estado, Familia_idFamilia, Notificacion_idNotificacion)
            OUTPUT INSERTED.idCatequizando
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        """, (nombre, apellidos, fechaNacimiento, documentoIdentidad,
              feBautismo, familia_id, notificacion_id))

        conn.commit()

        flash("Catequizando y familia registrados exitosamente ✔", "success")
        return redirect(url_for("index"))

    except Exception as e:
        conn.rollback()
        flash(f"Error registrando catequizando: {str(e)}", "danger")
        return redirect(url_for("registrar_catequizando"))


# Listar los catequizandos
@app.route("/listar-catequizandos")
def listar_catequizandos():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT idCatequizando, nombre, apellidos, documentoIdentidad, feBautismo
            FROM Administrativo.Catequizando
        """)

        datos = cursor.fetchall()
        return render_template("listar_catequizando.html", datos=datos)

    except Exception as e:
        return f"Error: {e}"

# API: Obtener las familias
@app.route("/api/familias")
def api_familias():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT idFamilia, nombreContacto, correo, telefono, direccion FROM Administrativo.Familia")
        filas = cursor.fetchall()

        result = []
        for f in filas:
            result.append({
                "idFamilia": f[0],
                "nombreContacto": f[1],
                "correo": f[2],
                "telefono": f[3],
                "direccion": f[4]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Obtener las notificaciones
@app.route("/api/notificaciones")
def api_notificaciones():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT idNotificacion, tipo, mensaje, fechaEnvio, leido, Usuario_idUsuario FROM Control.Notificacion")
        filas = cursor.fetchall()

        result = []
        for n in filas:
            result.append({
                "idNotificacion": n[0],
                "tipo": n[1],
                "mensaje": n[2],
                "fechaEnvio": n[3].isoformat() if n[3] else None,
                "leido": bool(n[4]),
                "Usuario_idUsuario": n[5]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/editar-catequizando/<int:id>")
def editar_catequizando(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT idCatequizando, nombre, apellidos, fechaNacimiento,
               documentoIdentidad, feBautismo, Familia_idFamilia
        FROM Administrativo.Catequizando
        WHERE idCatequizando = ?
    """, (id,))
    
    dato = cursor.fetchone()

    if not dato:
        flash("Catequizando no encontrado.", "danger")
        return redirect(url_for("listar_catequizandos"))

    return render_template("editar_catequizando.html", c=dato)


@app.route("/actualizar-catequizando/<int:id>", methods=["POST"])
def actualizar_catequizando(id):
    nombre = request.form["nombre"]
    apellidos = request.form["apellidos"]
    fechaNacimiento = request.form["fechaNacimiento"]
    documentoIdentidad = request.form["documentoIdentidad"]
    feBautismo = request.form.get("feBautismo", 0)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Administrativo.Catequizando
            SET nombre=?, apellidos=?, fechaNacimiento=?, documentoIdentidad=?, feBautismo=?
            WHERE idCatequizando=?
        """, (nombre, apellidos, fechaNacimiento, documentoIdentidad, feBautismo, id))

        conn.commit()
        flash("Catequizando actualizado correctamente ✔", "success")
        return redirect(url_for("listar_catequizandos"))

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        return redirect(url_for("editar_catequizando", id=id))


@app.route("/eliminar-catequizando/<int:id>", methods=["POST"])
def eliminar_catequizando(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Administrativo.Catequizando WHERE idCatequizando = ?", (id,))
        conn.commit()

        flash("Catequizando eliminado correctamente ✔", "success")
        return redirect(url_for("listar_catequizandos"))

    except Exception as e:
        conn.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        return redirect(url_for("listar_catequizandos"))


# Iniciar servidor
if __name__ == "__main__":
    app.run(debug=True)
