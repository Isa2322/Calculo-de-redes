import tkinter as tk
from tkinter import messagebox, scrolledtext
import ipaddress
import math

# --- LÓGICA DEL PROGRAMA (Backend) ---

def binario_con_puntos(valor_int):
    """Convierte un entero a formato binario de 32 bits con puntos."""
    bits = f"{valor_int:032b}"
    return ".".join([bits[i:i+8] for i in range(0, 32, 8)])

def calcular():
    # Borrar el texto anterior
    txt_resultado.config(state=tk.NORMAL)
    txt_resultado.delete(1.0, tk.END)
    
    try:
        # 1. INPUTS (Obtener de las cajas de texto)
        entrada_red = entry_red.get()
        if not entrada_red:
            raise ValueError("Debes ingresar una Red Original")
            
        n_subred = int(entry_n_subred.get())
        hosts_requeridos = int(entry_hosts.get())
        
        # 2. PROCESAMIENTO
        # Lógica exacta de tu código
        bits_host = math.ceil(math.log2(hosts_requeridos + 2))  # +2 para red y broadcast
        
        # strict=False permite corregir si el usuario mete una IP de host
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

        # Calcular desplazamiento
        tamano_bloque = 2 ** bits_host
        desplazamiento = n_subred * tamano_bloque
        
        # Calcular dirección nueva subred
        ip_base_int = int(red_principal.network_address)
        ip_subred_int = ip_base_int + desplazamiento
        
        subred_final = ipaddress.ip_network(f"{ipaddress.IPv4Address(ip_subred_int)}/{nuevo_prefijo}")
        
        # 3. GENERAR REPORTE (Acumulamos el texto en la variable 'r')
        r = "" 
        r += "--- CALCULADORA DE SUBREDES (GUI) ---\n"
        r += "\n" + "="*40 + "\n\n"
        
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
        
        # Formateamos el numero de subred en binario usando solo los bits prestados
        bin_subred = f"{n_subred:0{bits_prestados}b}" if bits_prestados > 0 else "0"
        r += f"numero de subred binario: {bin_subred} (Bits prestados: {bits_prestados})\n"
        r += "\n"
        r += f"Hosts base:               {hosts_requeridos} + 2 (Red y Broadcast)\n"
        r += "\n"
        r += f"mascara (decimal):        {subred_final.netmask}\n"
        r += f"mascara (binario):        {binario_con_puntos(int(subred_final.netmask))}\n"
        r += f"direccion de broadcast:   {subred_final.broadcast_address}\n"
        r += "\n"   
        r += f"primer host :             {subred_final.network_address + 1}\n"
        r += f"ultimo host :             {subred_final.broadcast_address - 1}\n"
        r += "\n" + "-" * 40 + "\n\n"
        r += "="*40

        # 4. MOSTRAR EN PANTALLA
        txt_resultado.insert(tk.END, r)
        
    except ValueError as e:
        messagebox.showerror("Error de Valor", f"Revisa los datos numéricos.\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")
    finally:
        # Bloquear edición para que sea solo lectura
        txt_resultado.config(state=tk.DISABLED)

# --- INTERFAZ GRÁFICA (Frontend) ---

ventana = tk.Tk()
ventana.title("Calculadora IP")
ventana.geometry("600x700")

# Estilos
font_lbl = ("Arial", 10, "bold")
font_ent = ("Arial", 10)
font_con = ("Consolas", 10) # Importante para alinear binarios

# Frame Inputs
frame_in = tk.Frame(ventana, padx=20, pady=20)
frame_in.pack(fill="x")

# Red Original
tk.Label(frame_in, text="Red Original (ej: 172.16.192.0/18):", font=font_lbl).grid(row=0, column=0, sticky="w", pady=5)
entry_red = tk.Entry(frame_in, width=25, font=font_ent)
entry_red.grid(row=0, column=1, padx=10)

# Numero Subred
tk.Label(frame_in, text="Subred Input (Nº Subred):", font=font_lbl).grid(row=1, column=0, sticky="w", pady=5)
entry_n_subred = tk.Entry(frame_in, width=25, font=font_ent)
entry_n_subred.grid(row=1, column=1, padx=10)

# Hosts Requeridos
tk.Label(frame_in, text="Hosts Requeridos:", font=font_lbl).grid(row=2, column=0, sticky="w", pady=5)
entry_hosts = tk.Entry(frame_in, width=25, font=font_ent)
entry_hosts.grid(row=2, column=1, padx=10)

# Boton
btn = tk.Button(ventana, text="CALCULAR", command=calcular, bg="#2196F3", fg="white", font=("Arial", 11, "bold"))
btn.pack(fill="x", padx=20, pady=5)

# Area de Texto
tk.Label(ventana, text="Resultado:", font=font_lbl).pack(anchor="w", padx=20, pady=(15,0))
txt_resultado = scrolledtext.ScrolledText(ventana, width=60, height=30, font=font_con, padx=10, pady=10)
txt_resultado.pack(fill="both", expand=True, padx=20, pady=10)
txt_resultado.config(state=tk.DISABLED)

ventana.mainloop()
