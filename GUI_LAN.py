import tkinter as tk
from tkinter import messagebox, scrolledtext
import ipaddress
import math

# --- LÓGICA DE NEGOCIO (Tu código adaptado) ---

def binario_con_puntos(valor_int):
    """Convierte un entero a formato binario de 32 bits con puntos."""
    bits = f"{valor_int:032b}"
    return ".".join([bits[i:i+8] for i in range(0, 32, 8)])

def calcular():
    # Limpiamos el área de texto antes de escribir
    txt_output.config(state=tk.NORMAL)
    txt_output.delete(1.0, tk.END)
    
    try:
        # 1. OBTENER DATOS DE LA INTERFAZ
        entrada_red = entry_red.get()
        if not entrada_red: raise ValueError("Falta la Red Original")
        
        n_subred = int(entry_n_subred.get())
        hosts_requeridos = int(entry_hosts.get())
        
        # El aumento es opcional, si está vacío asumimos 0
        aumento_str = entry_aumento.get()
        aumento = int(aumento_str) if aumento_str else 0

        # 2. CÁLCULOS (Tu lógica exacta)
        hosts_aumentados = math.ceil(hosts_requeridos * (1 + aumento/100))
        # +3 para red, broadcast y gateway (según tu código)
        bits_host = math.ceil(math.log2(hosts_aumentados + 3))  
        
        # Procesamiento Red Principal
        red_principal = ipaddress.ip_network(entrada_red, strict=False)
        
        nuevo_prefijo = 32 - bits_host
        
        # Validaciones
        if nuevo_prefijo < red_principal.prefixlen:
            messagebox.showerror("Error", "La subred pedida es más grande que la red original.")
            return

        bits_prestados = nuevo_prefijo - red_principal.prefixlen
        max_subredes = 2 ** bits_prestados
        
        if n_subred >= max_subredes:
            messagebox.showerror("Error", f"La subred #{n_subred} no existe. El máximo es {max_subredes - 1}.")
            return

        tamano_bloque = 2 ** bits_host
        desplazamiento = n_subred * tamano_bloque
        
        ip_base_int = int(red_principal.network_address)
        ip_subred_int = ip_base_int + desplazamiento
        
        subred_final = ipaddress.ip_network(f"{ipaddress.IPv4Address(ip_subred_int)}/{nuevo_prefijo}")
        
        # 3. CONSTRUCCIÓN DEL REPORTE (Acumulamos el texto en una variable)
        r = "" # 'r' será nuestro string de reporte
        r += "="*60 + "\n\n"
        
        # --- SECCIÓN RED PRINCIPAL ---
        r += "--- RED PRINCIPAL ---\n"
        r += f"Base de origen:      {red_principal.network_address}/{red_principal.prefixlen}\n"
        r += f"Red base binario:    {binario_con_puntos(int(red_principal.network_address))}\n"
        r += f"Máscara (Decimal):   {red_principal.netmask}\n"
        r += f"Mascara (Binario):   {binario_con_puntos(int(red_principal.netmask))}\n"
        r += "\n" + "-" * 40 + "\n\n"

        # --- SECCIÓN SUBRED #N ---
        r += f"--- SUBRED #{n_subred} ---\n"
        r += f"direccion de subred:      {subred_final.network_address}/{32-bits_host}\n"
        r += f"red subred binario:       {binario_con_puntos(int(subred_final.network_address))}\n"
        r += "\n"
        r += f"numero de subred:         {n_subred}\n"
        r += f"bits de host:             {bits_host}\n"
        
        bin_subred = f"{n_subred:0{bits_prestados}b}" if bits_prestados > 0 else "0"
        r += f"numero de subred binario: {bin_subred} (Bits prestados: {bits_prestados})\n"
        r += "\n"
        r += f"Hosts base:               {hosts_requeridos}\n"
        r += f"Hosts aumentados:         {hosts_requeridos * (1 + aumento/100)} => {hosts_aumentados}\n"
        r += f"Hosts necesarios totales: {hosts_aumentados} + 3 (Red, BC, GW) = {hosts_aumentados + 3} total\n"
        r += "\n"
        r += f"mascara (decimal):        {subred_final.netmask}\n"
        r += f"mascara (binario):        {binario_con_puntos(int(subred_final.netmask))}\n"
        r += f"direccion de broadcast:   {subred_final.broadcast_address}\n"
        r += f"Default gateway:          {subred_final.broadcast_address - 1} (Asignado al ultimo host util)\n"
        r += "\n"   
        r += f"primer host util:         {subred_final.network_address + 1}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + 1))}\n"
        r += f"ultimo host util:         {subred_final.broadcast_address - 2}\n"
        r += f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}\n"
        r += "\n" + "-" * 40 + "\n\n"
        
        r += f"Hosts sin ampliar:\n"
        r += f"Primer host usado:        {subred_final.network_address + 1}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + 1))}\n"
        r += f"ultimo host usado:        {subred_final.network_address + hosts_requeridos}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos))}\n"
        r += "\n"
        
        """
        r += f"Hosts vacantes (Gap Hosts):\n"
        r += f"Primer host libre:        {subred_final.network_address + hosts_requeridos + 1}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos + 1))}\n"
        r += f"ultimo host libre:        {subred_final.broadcast_address - 2}\n"
        r += f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}\n"
        """
        r += "\n" + "-" * 40 + "\n\n"                
        
        r += f"Hosts ampliados (Buffer):\n"
        r += f"Primer host usado:        {subred_final.network_address + hosts_requeridos + 1}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos + 1))}\n"
        r += f"ultimo host usado:        {subred_final.network_address + int(hosts_aumentados)}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + int(hosts_aumentados)))}\n"
        r += "\n"
        
        """
        r += f"Hosts vacantes Finales (Físicos):\n"
        r += f"Primer host libre:        {subred_final.network_address + int(hosts_aumentados) + 1}\n"
        r += f"                          {binario_con_puntos(int(subred_final.network_address + int(hosts_aumentados) + 1))}\n"
        r += f"ultimo host libre:        {subred_final.broadcast_address - 2}\n"
        r += f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}\n"
        r += "\n" + "="*60
        """
        # 4. MOSTRAR RESULTADO EN PANTALLA
        txt_output.insert(tk.END, r)
        
    except ValueError as e:
        messagebox.showerror("Error de Datos", f"Revisa que los números sean correctos.\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")
    finally:
        txt_output.config(state=tk.DISABLED) # Bloquear edición

# --- INTERFAZ GRÁFICA (GUI) ---

ventana = tk.Tk()
ventana.title("Calculadora de Subredes Avanzada")
ventana.geometry("700x750")

# Estilos
fuente_label = ("Arial", 10, "bold")
fuente_entry = ("Arial", 10)
# IMPORTANTE: Usar fuente monoespaciada para que los binarios se alineen
fuente_consola = ("Consolas", 10) 

# Frame para los inputs
frame_form = tk.Frame(ventana, padx=20, pady=15)
frame_form.pack(fill="x")

# Grid de formulario
tk.Label(frame_form, text="Red Original (CIDR):", font=fuente_label).grid(row=0, column=0, sticky="w", pady=5)
entry_red = tk.Entry(frame_form, width=25, font=fuente_entry)
entry_red.grid(row=0, column=1, padx=10, pady=5)
entry_red.insert(0, "172.16.192.0/18") # Valor por defecto

tk.Label(frame_form, text="Nº de Subred:", font=fuente_label).grid(row=0, column=2, sticky="w", pady=5)
entry_n_subred = tk.Entry(frame_form, width=10, font=fuente_entry)
entry_n_subred.grid(row=0, column=3, padx=10, pady=5)

tk.Label(frame_form, text="Hosts Requeridos:", font=fuente_label).grid(row=1, column=0, sticky="w", pady=5)
entry_hosts = tk.Entry(frame_form, width=25, font=fuente_entry)
entry_hosts.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_form, text="% Aumento (0-100):", font=fuente_label).grid(row=1, column=2, sticky="w", pady=5)
entry_aumento = tk.Entry(frame_form, width=10, font=fuente_entry)
entry_aumento.grid(row=1, column=3, padx=10, pady=5)
entry_aumento.insert(0, "0")

# Botón Calcular
btn_calcular = tk.Button(ventana, text="CALCULAR SUBRED", command=calcular, 
                         bg="#0078D7", fg="white", font=("Arial", 11, "bold"), height=2)
btn_calcular.pack(fill="x", padx=20, pady=5)

# Área de Resultados (ScrolledText)
lbl_resultado = tk.Label(ventana, text="Reporte Detallado:", font=fuente_label)
lbl_resultado.pack(anchor="w", padx=20, pady=(10,0))

txt_output = scrolledtext.ScrolledText(ventana, height=30, font=fuente_consola, padx=10, pady=10)
txt_output.pack(fill="both", expand=True, padx=20, pady=10)
txt_output.config(state=tk.DISABLED)

ventana.mainloop()
