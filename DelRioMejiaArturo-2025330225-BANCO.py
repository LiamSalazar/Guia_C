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

            # ✅ Consultar saldos actualizados
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

            # ✅ Actualizar saldos
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_saldo_origen, datos_usuario[0]))
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (nuevo_saldo_destino, destino))

            # ✅ Registrar operación
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
    
