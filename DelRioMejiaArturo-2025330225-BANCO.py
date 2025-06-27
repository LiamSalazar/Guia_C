import sqlite3
import tkinter as tk
from tkinter import messagebox
import uuid
from PIL import Image, ImageTk
import os
from tkinter import simpledialog
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


#

DB_PATH = "BANCO_EL_BURRO_FELIZ.db"

def conectar_bd():
    return sqlite3.connect(DB_PATH)

def autenticar_credenciales(tabla, user, password):
    con = conectar_bd()
    cur = con.cursor()
    user = user.strip()
    password = password.strip()
    if tabla == "CLIENTE":
        cur.execute("SELECT * FROM CLIENTE WHERE TRIM(User)=? AND TRIM(Psswrd)=?", (user, password))
    elif tabla == "EMPLEADO":
        cur.execute("SELECT * FROM EMPLEADO WHERE TRIM(UserEmpleado)=? AND TRIM(Contrasena)=?", (user, password))
    elif tabla == "COMERCIO":
        cur.execute("SELECT * FROM COMERCIO WHERE TRIM(NomComercio)=? AND TRIM(DirComercio)=?", (user, password))
    resultado = cur.fetchone()
    con.close()
    return resultado

def consultar_saldo(datos_usuario):
    con = conectar_bd()
    cur = con.cursor()
    cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (datos_usuario[0],))
    nuevo_saldo = cur.fetchone()[0]
    con.close()
    messagebox.showinfo("Saldo", f"Tu saldo actual es: ${nuevo_saldo}")
    


def corregir_clave_rastreo():
    con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
    cur = con.cursor()
    
    # Eliminar COMPRAS_OLD si ya existe (previene error)
    cur.execute("DROP TABLE IF EXISTS COMPRAS_OLD")
    
    # 1. Renombrar la tabla vieja
    cur.execute("ALTER TABLE COMPRAS RENAME TO COMPRAS_OLD")

    # 2. Crear nueva tabla con ClaveRastreo como TEXT
    cur.execute("""
        CREATE TABLE COMPRAS (
            ClaveRastreo TEXT PRIMARY KEY,
            Saldo REAL NOT NULL,
            Importe REAL NOT NULL,
            CCliente INTEGER NOT NULL,
            CComercio INTEGER
        )
    """)

    # 3. Copiar datos de la tabla vieja
    cur.execute("SELECT * FROM COMPRAS_OLD")
    registros = cur.fetchall()

    for r in registros:
        clave = str(r[0])  # convertir a texto
        saldo = float(r[1])
        importe = float(r[2])
        ccliente = int(r[3])
        ccomercio = int(r[4]) if r[4] is not None else None
        cur.execute("INSERT INTO COMPRAS VALUES (?, ?, ?, ?, ?)", (clave, saldo, importe, ccliente, ccomercio))

    # 4. Eliminar la tabla vieja
    cur.execute("DROP TABLE COMPRAS_OLD")

    con.commit()
    con.close()
    print("✅ Tabla COMPRAS corregida correctamente (ClaveRastreo ahora es TEXT).")

corregir_clave_rastreo()


def operacion_monto(tipo, datos_usuario):
    ventana = tk.Toplevel()
    ventana.title(tipo.capitalize())

    tk.Label(ventana, text="Monto:").pack()
    monto_entry = tk.Entry(ventana)
    monto_entry.pack()

    def aplicar():
        try:
            monto_str = monto_entry.get().replace(",", ".")
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError("Monto inválido")

            con = conectar_bd()
            cur = con.cursor()

            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (datos_usuario[0],))
            saldo = cur.fetchone()[0]

            if tipo == "deposito":
                saldo += monto
            elif monto <= saldo:
                saldo -= monto
            else:
                raise ValueError("Saldo insuficiente")

            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (saldo, datos_usuario[0]))

            clave_rastreo = str(uuid.uuid4())[:12]
            cur.execute("""
                INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio)
                VALUES (?, ?, ?, ?, ?)
            """, (clave_rastreo, saldo, monto if tipo == "deposito" else -monto, datos_usuario[0], None))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", f"{tipo.capitalize()} realizado. Nuevo saldo: ${saldo:.2f}")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Aplicar", command=aplicar).pack()
    

def transferencia(datos_usuario):
    ventana = tk.Toplevel()
    ventana.title("Transferencia")

    tk.Label(ventana, text="Número de cuenta destino:").pack()
    destino_entry = tk.Entry(ventana)
    destino_entry.pack()

    tk.Label(ventana, text="Monto:").pack()
    monto_entry = tk.Entry(ventana)
    monto_entry.pack()

    def transferir():
        try:
            destino = int(destino_entry.get())
            monto_str = monto_entry.get().replace(",", ".")
            monto = float(monto_str)

            con = conectar_bd()
            cur = con.cursor()

            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (datos_usuario[0],))
            saldo_origen = cur.fetchone()
            if not saldo_origen:
                raise ValueError("Cuenta origen no encontrada")

            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (destino,))
            saldo_destino = cur.fetchone()
            if not saldo_destino:
                raise ValueError("Cuenta destino no encontrada")

            saldo_origen = saldo_origen[0]
            saldo_destino = saldo_destino[0]

            if monto <= 0 or monto > saldo_origen:
                raise ValueError("Monto inválido o saldo insuficiente")

            nuevo_saldo_origen = saldo_origen - monto
            nuevo_saldo_destino = saldo_destino + monto

            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_saldo_origen, datos_usuario[0]))
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_saldo_destino, destino))

            clave_rastreo_1 = str(uuid.uuid4())[:12]
            clave_rastreo_2 = str(uuid.uuid4())[:12]
            cur.execute("INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio) VALUES (?, ?, ?, ?, ?)",
                        (clave_rastreo_1, nuevo_saldo_origen, -monto, datos_usuario[0], None))
            cur.execute("INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio) VALUES (?, ?, ?, ?, ?)",
                        (clave_rastreo_2, nuevo_saldo_destino, monto, destino, None))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", "Transferencia realizada correctamente")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Transferir", command=transferir).pack()
    

def operacion_empleado(tipo):
    ventana = tk.Toplevel()
    ventana.title(f"{tipo.capitalize()} a cliente")

    tk.Label(ventana, text="Número de cliente:").pack()
    num_entry = tk.Entry(ventana)
    num_entry.pack()

    tk.Label(ventana, text="Monto:").pack()
    monto_entry = tk.Entry(ventana)
    monto_entry.pack()

    def aplicar():
        try:
            num = int(num_entry.get())
            monto_str = monto_entry.get().replace(",", ".")
            monto = float(monto_str)
            con = conectar_bd()
            cur = con.cursor()
            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (num,))
            datos = cur.fetchone()
            if not datos:
                raise ValueError("Cliente no encontrado")
            saldo = datos[0]
            if tipo == "deposito":
                saldo += monto
            elif monto <= saldo:
                saldo -= monto
            else:
                raise ValueError("Saldo insuficiente")

            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (saldo, num))

            clave_rastreo = str(uuid.uuid4())[:12]
            cur.execute("""INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio)
               VALUES (?, ?, ?, ?, ?)""",
               (clave_rastreo, float(saldo), float(monto) if tipo == "deposito" else -float(monto), num, None))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", f"{tipo.capitalize()} realizado. Nuevo saldo: ${saldo}")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Aplicar", command=aplicar).pack()

def transferencia_empleado():
    ventana = tk.Toplevel()
    ventana.title("Transferencia entre clientes")

    tk.Label(ventana, text="Cuenta origen:").pack()
    origen_entry = tk.Entry(ventana)
    origen_entry.pack()

    tk.Label(ventana, text="Cuenta destino:").pack()
    destino_entry = tk.Entry(ventana)
    destino_entry.pack()

    tk.Label(ventana, text="Monto:").pack()
    monto_entry = tk.Entry(ventana)
    monto_entry.pack()

    def transferir():
        try:
            origen = int(origen_entry.get())
            destino = int(destino_entry.get())
            monto_str = monto_entry.get().replace(",", ".")
            monto = float(monto_str)
            con = conectar_bd()
            cur = con.cursor()
            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (origen,))
            so = cur.fetchone()
            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (destino,))
            sd = cur.fetchone()
            if not so or not sd:
                raise ValueError("Cuenta no encontrada")
            if monto <= 0 or monto > so[0]:
                raise ValueError("Monto inválido")

            nuevo_so = so[0] - monto
            nuevo_sd = sd[0] + monto
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_so, origen))
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_sd, destino))

            clave_rastreo_1 = str(uuid.uuid4())[:12]
            clave_rastreo_2 = str(uuid.uuid4())[:12]
            cur.execute("INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio) VALUES (?, ?, ?, ?, ?)",
                        (clave_rastreo_1, float(nuevo_so), -float(monto), origen, None))
            cur.execute("INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio) VALUES (?, ?, ?, ?, ?)",
                        (clave_rastreo_2, float(nuevo_sd), float(monto), destino, None))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", "Transferencia completada")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Transferir", command=transferir).pack()

def registrar_venta(datos_usuario):
    import tkinter as tk
    from tkinter import messagebox
    import sqlite3

    ventana = tk.Toplevel()
    ventana.title("Registrar venta")

    tk.Label(ventana, text="Importe de la venta:").pack()
    monto_entry = tk.Entry(ventana)
    monto_entry.pack()

    tk.Label(ventana, text="Número de cliente (NumeroCliente):").pack()
    num_cliente_entry = tk.Entry(ventana)
    num_cliente_entry.pack()


    def guardar():
        try:
            importe_str = monto_entry.get().replace(",", ".")
            importe = float(importe_str)
            if importe <= 0:
                raise ValueError("El importe debe ser mayor que cero.")

            numero_cliente = int(num_cliente_entry.get().strip())
            clave_comercio = int(datos_usuario[0])  # ClaveComercio del comercio que registró

            with sqlite3.connect("BANCO_EL_BURRO_FELIZ.db") as con:
                cur = con.cursor()

                # Verificar existencia del cliente
                cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (numero_cliente,))
                resultado = cur.fetchone()
                if not resultado:
                    raise ValueError("Cliente no encontrado.")
                saldo_cliente = float(resultado[0])

                if importe > saldo_cliente:
                    raise ValueError("El cliente no tiene saldo suficiente.")

                # Actualizar saldo del cliente
                nuevo_saldo = saldo_cliente - importe
                cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_saldo, numero_cliente))

                # Insertar registro de la compra
                clave_rastreo = str(uuid.uuid4())[:12]
                cur.execute("""
                    INSERT INTO COMPRAS (ClaveRastreo, Saldo, Importe, CCliente, CComercio)
                    VALUES (?, ?, ?, ?, ?)
                """, (clave_rastreo, nuevo_saldo, -importe, numero_cliente, clave_comercio))

            messagebox.showinfo("Éxito", f"Venta registrada correctamente.")
            ventana.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"{type(e).__name__}: {str(e)}")
            




    tk.Button(ventana, text="Registrar", command=guardar).pack(pady=10)

def agregar_cuenta_cliente():
    ventana = tk.Toplevel()
    ventana.title("Agregar cuenta")

    tipo_var = tk.StringVar(value="Cliente")

    tk.Label(ventana, text="Tipo de cuenta:").pack()
    tk.OptionMenu(ventana, tipo_var, "Cliente", "Empleado", "Comercio").pack()

    frame_campos = tk.Frame(ventana)
    frame_campos.pack()
    entradas_dict = {}

    def mostrar_campos(*args):
        for widget in frame_campos.winfo_children():
            widget.destroy()
        entradas_dict.clear()
        tipo = tipo_var.get()

        if tipo == "Cliente":
            campos = ["Nombre", "Usuario", "Contraseña", "Dirección", "Teléfono", "Número CLABE", "Saldo inicial"]
        elif tipo == "Empleado":
            campos = ["NumEmpleado", "Usuario", "Contraseña", "Rol", "Nombre", "Sucursal"]
        elif tipo == "Comercio":
            campos = ["ClaveComercio", "Nombre Comercio", "Dirección Comercio"]

        for campo in campos:
            tk.Label(frame_campos, text=campo + ":").pack()
            entrada = tk.Entry(frame_campos, show="*" if "Contraseña" in campo else None)
            entrada.pack()
            entradas_dict[campo] = entrada

    tipo_var.trace_add("write", mostrar_campos)
    mostrar_campos()

    def guardar():
        try:
            tipo = tipo_var.get()
            datos = {campo: entrada.get().strip() for campo, entrada in entradas_dict.items()}
            con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
            cur = con.cursor()

            if tipo == "Cliente":
                saldo = float(datos["Saldo inicial"])
                cur.execute("""INSERT INTO CLIENTE 
                    (NombreCliente, User, Psswrd, DirCliente, Telefono, NumClabe, Saldo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (datos["Nombre"], datos["Usuario"], datos["Contraseña"],
                     datos["Dirección"], datos["Teléfono"], datos["Número CLABE"], saldo))

            elif tipo == "Empleado":
                cur.execute("""INSERT INTO EMPLEADO 
                    (NumEmpleado, UserEmpleado, Contrasena, Rol, Nombre, Sucursal)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (int(datos["NumEmpleado"]), datos["Usuario"], datos["Contraseña"],
                     int(datos["Rol"]), datos["Nombre"], int(datos["Sucursal"])))

            elif tipo == "Comercio":
                cur.execute("""INSERT INTO COMERCIO 
                    (ClaveComercio, NomComercio, DirComercio)
                    VALUES (?, ?, ?)""",
                    (datos["ClaveComercio"], datos["Nombre Comercio"], datos["Dirección Comercio"]))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", f"{tipo} agregado correctamente.")
            ventana.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Agregar", command=guardar).pack(pady=10)
    
def agregar_cuenta_cliente_tipo(tipo):
    ventana = tk.Toplevel()
    ventana.title(f"Agregar cuenta {tipo.lower()}")

    entradas_dict = {}

    tk.Label(ventana, text=f"Formulario para: {tipo}").pack()

    campos_por_tipo = {
        "Cliente": ["Nombre", "Usuario", "Contraseña", "Dirección", "Teléfono", "Número CLABE", "Saldo inicial"],
        "Empleado": ["NumEmpleado", "Usuario", "Contraseña", "Rol", "Nombre", "Sucursal"],
        "Comercio": ["ClaveComercio", "Nombre Comercio", "Dirección Comercio"]
    }

    campos = campos_por_tipo[tipo]

    import random

    for campo in campos:
        tk.Label(ventana, text=f"{campo}:").pack()
    
        if tipo == "Cliente" and campo == "Número CLABE":
            clabe = ''.join(random.choices("0123456789", k=16))
            entrada = tk.Entry(ventana)
            entrada.insert(0, clabe)
            entrada.configure(state="readonly")
    
        elif tipo == "Comercio" and campo == "ClaveComercio":
            clave = str(random.randint(10000, 999999))  # Un solo dígito
            entrada = tk.Entry(ventana)
            entrada.insert(0, clave)
            entrada.configure(state="readonly")
    
        else:
            entrada = tk.Entry(ventana, show="*" if "Contraseña" in campo else None)
    
        entrada.pack()
        entradas_dict[campo] = entrada      

    def guardar():
        try:
            datos = {campo: entrada.get().strip() for campo, entrada in entradas_dict.items()}
            con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
            cur = con.cursor()

            if tipo == "Cliente":
                saldo = float(datos["Saldo inicial"])
                cur.execute("""INSERT INTO CLIENTE 
                    (NombreCliente, User, Psswrd, DirCliente, Telefono, NumClabe, Saldo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (datos["Nombre"], datos["Usuario"], datos["Contraseña"],
                     datos["Dirección"], datos["Teléfono"], datos["Número CLABE"], saldo))

            elif tipo == "Empleado":
                cur.execute("""INSERT INTO EMPLEADO 
                    (NumEmpleado, UserEmpleado, Contrasena, Rol, Nombre, Sucursal)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (int(datos["NumEmpleado"]), datos["Usuario"], datos["Contraseña"],
                     int(datos["Rol"]), datos["Nombre"], int(datos["Sucursal"])))

            elif tipo == "Comercio":
                cur.execute("""INSERT INTO COMERCIO 
                    (ClaveComercio, NomComercio, DirComercio)
                    VALUES (?, ?, ?)""",
                    (datos["ClaveComercio"], datos["Nombre Comercio"], datos["Dirección Comercio"]))

            con.commit()
            con.close()
            messagebox.showinfo("Éxito", f"{tipo} agregado correctamente.")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana, text="Agregar", command=guardar).pack(pady=10)

def mostrar_reporte(datos_usuario):
    import tempfile

    try:
        clave_comercio = int(datos_usuario[0])
        
        # Solicitar número de cliente
        numero_cliente = simpledialog.askinteger("Cliente", "Ingrese el número de cliente:")
        if not numero_cliente:
            return

        con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
        cur = con.cursor()
        cur.execute("""
            SELECT ClaveRastreo, Importe, Saldo 
            FROM COMPRAS 
            WHERE CCliente=? AND CComercio=?
        """, (numero_cliente, clave_comercio))
        ventas = cur.fetchall()
        con.close()

        if not ventas:
            messagebox.showinfo("Sin datos", "No hay ventas registradas para este cliente.")
            return

        # Crear archivo temporal PDF
        temp_dir = tempfile.gettempdir()
        ruta_pdf = os.path.join(temp_dir, f"reporte_cliente_{numero_cliente}.pdf")
        c = canvas.Canvas(ruta_pdf, pagesize=LETTER)
        width, height = LETTER

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Reporte de Ventas - Cliente #{numero_cliente}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Comercio: {datos_usuario[1]}")

        # Tabla de ventas
        y = height - 120
        for venta in ventas:
            rastreo = venta[0] if venta[0] else "None"
            linea = f"Importe: ${venta[1]:.2f}"
            c.drawString(50, y, linea)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

        c.save()

        # Abrir el PDF automáticamente
        os.startfile(ruta_pdf) if os.name == "nt" else os.system(f"open {ruta_pdf}")

    except Exception as e:
        messagebox.showerror("Error", f"{type(e)._name_}: {str(e)}")

def mostrar_reporte2(datos_usuario):
    import tempfile

    try:
        clave_comercio = int(datos_usuario[0])
        
        # Solicitar número de cliente
        numero_cliente = simpledialog.askinteger("Cliente", "Ingrese el número de cliente:")
        if not numero_cliente:
            return

        con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
        cur = con.cursor()
        cur.execute("""
            SELECT ClaveRastreo, Importe, Saldo 
            FROM COMPRAS 
            WHERE CCliente=? AND CComercio=?
        """, (numero_cliente, clave_comercio))
        ventas = cur.fetchall()
        con.close()

        if not ventas:
            messagebox.showinfo("Sin datos", "No hay ventas registradas para este cliente.")
            return

        # Crear archivo temporal PDF
        temp_dir = tempfile.gettempdir()
        ruta_pdf = os.path.join(temp_dir, f"reporte_cliente_{numero_cliente}.pdf")
        c = canvas.Canvas(ruta_pdf, pagesize=LETTER)
        width, height = LETTER

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Reporte de Compras - Cliente #{numero_cliente}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Comercio: {datos_usuario[1]}")

        # Tabla de ventas
        y = height - 120
        for venta in ventas:
            rastreo = venta[0] if venta[0] else "None"
            linea = f"Importe: ${venta[1]:.2f}"
            c.drawString(50, y, linea)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

        c.save()

        # Abrir el PDF automáticamente
        os.startfile(ruta_pdf) if os.name == "nt" else os.system(f"open {ruta_pdf}")

    except Exception as e:
        messagebox.showerror("Error", f"{type(e)._name_}: {str(e)}")

def menu_operaciones(tipo_usuario, datos_usuario):
    menu = tk.Tk()
    menu.title("💼 Banco El Burro Feliz - Menú de Operaciones")
    menu.geometry("420x500")
    menu.configure(bg="#f0f4f7")  # Fondo suave
    
    # Encabezado
    encabezado = tk.Label(menu, text="🐴 Banco El Burro Feliz 🏦", font=("Helvetica", 18, "bold"), bg="#f0f4f7", fg="#004080")
    encabezado.pack(pady=20)

    # Subtítulo personalizado
    sub = f"Bienvenido, {datos_usuario[1]}" if tipo_usuario == "CLIENTE" else \
          f"Empleado: {datos_usuario[1]}" if tipo_usuario == "EMPLEADO" else \
          f"Comercio: {datos_usuario[1]}"
    tk.Label(menu, text=sub, font=("Helvetica", 14), bg="#f0f4f7").pack(pady=10)

    # Estilo común para botones
    def crear_boton(texto, comando):
        return tk.Button(menu, text=texto, font=("Helvetica", 12), bg="#004080", fg="white", width=30, pady=5, command=comando)

    if tipo_usuario == "CLIENTE":
        crear_boton("Consultar Saldo", lambda: consultar_saldo(datos_usuario)).pack(pady=5)
        crear_boton("Depósito", lambda: operacion_monto("deposito", datos_usuario)).pack(pady=5)
        crear_boton("Retiro", lambda: operacion_monto("retiro", datos_usuario)).pack(pady=5)
        crear_boton("Transferencia", lambda: transferencia(datos_usuario)).pack(pady=5)

    elif tipo_usuario == "EMPLEADO":
        crear_boton("Depósito a cliente", lambda: operacion_empleado("deposito")).pack(pady=5)
        crear_boton("Retiro de cliente", lambda: operacion_empleado("retiro")).pack(pady=5)
        crear_boton("Transferencia entre clientes", transferencia_empleado).pack(pady=5)
        crear_boton("Agregar cuenta empleado", lambda: agregar_cuenta_cliente_tipo("Empleado")).pack(pady=5)
        crear_boton("Agregar cuenta cliente", lambda: agregar_cuenta_cliente_tipo("Cliente")).pack(pady=5)
        crear_boton("Agregar cuenta comercio", lambda: agregar_cuenta_cliente_tipo("Comercio")).pack(pady=5)

    elif tipo_usuario == "COMERCIO":
        crear_boton("Registrar venta", lambda: registrar_venta(datos_usuario)).pack(pady=5)
        crear_boton("Reporte de ventas", lambda: mostrar_reporte(datos_usuario)).pack(pady=5)
        crear_boton("Reporte de compras", lambda: mostrar_reporte2(datos_usuario)).pack(pady=5)

    # Botón salir
    tk.Button(menu, text="Salir", font=("Helvetica", 11), bg="lightgray", width=20, command=menu.destroy).pack(pady=25)

    menu.mainloop()


def ventana_login(tabla):
    login = tk.Tk()
    login.title("Login")

    entradas = {}

    if tabla == "COMERCIO":
        tk.Label(login, text="Nombre del comercio:").pack()
        nombre_entry = tk.Entry(login)
        nombre_entry.pack()
        entradas["NomComercio"] = nombre_entry

        tk.Label(login, text="Dirección del comercio:").pack()
        dir_entry = tk.Entry(login)
        dir_entry.pack()
        entradas["DirComercio"] = dir_entry
    else:
        tk.Label(login, text="Usuario:").pack()
        user_entry = tk.Entry(login)
        user_entry.pack()
        entradas["Usuario"] = user_entry

        tk.Label(login, text="Contraseña:").pack()
        pass_entry = tk.Entry(login, show="*")
        pass_entry.pack()
        entradas["Contraseña"] = pass_entry

    def ingresar():
        if tabla == "COMERCIO":
            nombre = entradas["NomComercio"].get().strip()
            direccion = entradas["DirComercio"].get().strip()

            con = sqlite3.connect("BANCO_EL_BURRO_FELIZ.db")
            cur = con.cursor()
            cur.execute("""
                SELECT ClaveComercio, NomComercio 
                FROM COMERCIO 
                WHERE NomComercio = ? AND DirComercio = ?
            """, (nombre, direccion))
            datos = cur.fetchone()
            con.close()

        else:
            user = entradas["Usuario"].get().strip()
            password = entradas["Contraseña"].get().strip()
            datos = autenticar_credenciales(tabla, user, password)

        if datos:
            login.destroy()
            menu_operaciones(tabla, datos)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    tk.Button(login, text="Ingresar", command=ingresar).pack(pady=10)
    login.mainloop()

def main():
    root = tk.Tk()
    root.title("🐴 Banco El Burro Feliz")
    root.geometry("450x550")
    root.configure(bg="#e6f2ff")


    # --- Ventana emergente de bienvenida ---
    messagebox.showinfo("Bienvenido", "¡Bienvenido a Banco El Burro Feliz!\nTu confianza es nuestra mayor riqueza.")

    # --- Logo o imagen decorativa ---
    try:
        imagen = Image.open("logo_burro.png") 
        imagen = imagen.resize((150, 150), Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(imagen)
        img_label = tk.Label(root, image=logo, bg="#e6f2ff")
        img_label.image = logo  
        img_label.pack(pady=10)
    except Exception as e:
        print("No se pudo cargar la imagen:", e)

    titulo = tk.Label(root, text="🐴 Banco El Burro Feliz", font=("Helvetica", 20, "bold"), fg="#003366", bg="#e6f2ff")
    titulo.pack(pady=10)

    subtitulo = tk.Label(root, text="Seleccione tipo de acceso:", font=("Helvetica", 14), bg="#e6f2ff", fg="#003366")
    subtitulo.pack(pady=10)

    # --- Botones estilizados ---
    def crear_boton(texto, comando):
        return tk.Button(root, text=texto, font=("Helvetica", 12), bg="#0066cc", fg="white", width=25, pady=5, command=comando)

    crear_boton("Cliente", lambda: [root.destroy(), ventana_login("CLIENTE")]).pack(pady=8)
    crear_boton("Empleado", lambda: [root.destroy(), ventana_login("EMPLEADO")]).pack(pady=8)
    crear_boton("Comercio", lambda: [root.destroy(), ventana_login("COMERCIO")]).pack(pady=8)

    tk.Button(root, text="Salir", font=("Helvetica", 11), bg="lightgray", fg="black", width=20, command=root.quit).pack(pady=25)

    root.mainloop()

main()
