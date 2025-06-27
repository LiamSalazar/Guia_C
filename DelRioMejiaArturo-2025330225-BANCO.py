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
        
