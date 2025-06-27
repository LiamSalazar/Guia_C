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

            # ✅ Consultar saldo actualizado
            cur.execute("SELECT Saldo FROM CLIENTE WHERE NumeroCliente=?", (datos_usuario[0],))
            saldo = cur.fetchone()[0]

            if tipo == "deposito":
                saldo += monto
            elif monto <= saldo:
                saldo -= monto
            else:
                raise ValueError("Saldo insuficiente")

            # ✅ Actualizar saldo
            cur.execute("UPDATE CLIENTE SET Saldo=? WHERE NumeroCliente=?", (saldo, datos_usuario[0]))

            # ✅ Registrar operación
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
    
