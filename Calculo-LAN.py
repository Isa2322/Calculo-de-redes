import ipaddress
import math

def binario_con_puntos(valor_int):
    """Convierte un entero a formato binario de 32 bits con puntos."""
    bits = f"{valor_int:032b}"
    return ".".join([bits[i:i+8] for i in range(0, 32, 8)])

def calcular_red_consola():
    print("--- CALCULADORA DE SUBREDES (Modo Consola) ---")
    
    # 1. INPUTS
    try:
        entrada_red = input("red original (Ej: 172.16.192.0/18): ")
        n_subred = int(input("subred input (número de subred): "))
        #bits_host = int(input("hosts necesarios (bits de host): "))
        hosts_requeridos = int(input("hosts requeridos (número de hosts): "))
        aumento = int(input("aumento de hosts (opcional, 0 si no): "))
        
        hosts_aumentados = math.ceil(hosts_requeridos * (1 + aumento/100))
        
        bits_host = math.ceil(math.log2(hosts_aumentados + 3))  # +3 para red, broadcast y default gateway
        
        # 2. PROCESAMIENTO RED PRINCIPAL
        red_principal = ipaddress.ip_network(entrada_red, strict=False)
        
        # 3. CÁLCULOS PARA LA SUBRED
        nuevo_prefijo = 32 - bits_host
        
        # Validaciones de lógica de redes
        if nuevo_prefijo < red_principal.prefixlen:
            print("\n[ERROR] La subred pedida es más grande que la red original.")
            return

        # Calcular bits prestados (para mostrar el número de subred en binario correctamente)
        bits_prestados = nuevo_prefijo - red_principal.prefixlen
        max_subredes = 2 ** bits_prestados
        
        if n_subred >= max_subredes:
            print(f"\n[ERROR] La subred #{n_subred} no existe. El máximo es {max_subredes - 1}.")
            return

        # Calcular el desplazamiento (Offset)
        tamano_bloque = 2 ** bits_host
        desplazamiento = n_subred * tamano_bloque
        
        # Calcular la dirección de la nueva subred
        ip_base_int = int(red_principal.network_address)
        ip_subred_int = ip_base_int + desplazamiento
        
        # Crear objeto de la subred final
        subred_final = ipaddress.ip_network(f"{ipaddress.IPv4Address(ip_subred_int)}/{nuevo_prefijo}")
        
        # Definir Gateway (Convención: Primera IP útil)
        gateway = subred_final.network_address + 1

        # 4. OUTPUT (FORMATO SOLICITADO)
        print("\n" + "="*40)
        print("")
        
        # --- SECCIÓN RED PRINCIPAL ---
        print("--- RED PRINCIPAL ---")
        print(f"Base de origen:      {red_principal.network_address}/{red_principal.prefixlen}")
        print(f"Red base binario:    {binario_con_puntos(int(red_principal.network_address))}")
        print(f"Máscara (Decimal):   {red_principal.netmask}")
        print(f"Mascara (Binario):   {binario_con_puntos(int(red_principal.netmask))}")
        print("")
        print("-" * 40)
        print("")

        # --- SECCIÓN SUBRED #N ---
        print(f"--- SUBRED #{n_subred} ---")
        print(f"direccion de subred:      {subred_final.network_address}/{32-bits_host}")
        print(f"red subred binario:       {binario_con_puntos(int(subred_final.network_address))}")
        print("")
        print(f"numero de subred:         {n_subred}")
        print(f"bits de host:             {bits_host}")
        bin_subred = f"{n_subred:0{bits_prestados}b}" if bits_prestados > 0 else "0"
        print(f"numero de subred binario: {bin_subred} (Bits prestados: {bits_prestados})")
        print("")
        print(f"Hosts base:               {hosts_requeridos}")
        print(f"Hosts aumentados:         {hosts_requeridos * (1 + aumento/100)} => {hosts_aumentados}")
        print(f"Hosts necesarios totales: {hosts_aumentados} + 3 (Red, Broadcast, Gateway) = {hosts_aumentados + 3} total")
        print("")
        print(f"mascara (decimal):        {subred_final.netmask}")
        print(f"mascara (binario):        {binario_con_puntos(int(subred_final.netmask))}")
        print(f"direccion de broadcast:   {subred_final.broadcast_address}")
        print(f"Default gateway:          {subred_final.broadcast_address - 1} (Asignado al ultimo host util)")
        print("")   
        print(f"primer host util:         {subred_final.network_address + 1}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + 1))}")
        print(f"ultimo host util:         {subred_final.broadcast_address - 2}")
        print(f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}")
        print("")
        print("-" * 40)
        print("")
        print(f"Hosts sin ampliar:")
        print(f"Primer host usado:        {subred_final.network_address + 1}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + 1))}")
        print(f"ultimo host usado:        {subred_final.network_address + hosts_requeridos}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos))}")
        print("")
        print(f"Hosts vacantes:")
        print(f"Primer host libre:        {subred_final.network_address + hosts_requeridos + 1}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos + 1))}")
        print(f"ultimo host libre:        {subred_final.broadcast_address - 2}")
        print(f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}")
        print("")
        print("-" * 40)
        print("")                
        print(f"Hosts ampliados:")
        print(f"Primer host usado:        {subred_final.network_address + hosts_requeridos + 1}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + hosts_requeridos + 1))}")
        print(f"ultimo host usado:        {subred_final.network_address + int(hosts_aumentados)}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + int(hosts_aumentados)))}")
        print("")
        print(f"Hosts vacantes:")
        print(f"Primer host libre:        {subred_final.network_address + int(hosts_aumentados) + 1}")
        print(f"                          {binario_con_puntos(int(subred_final.network_address + int(hosts_aumentados) + 1))}")
        print(f"ultimo host libre:        {subred_final.broadcast_address - 2}")
        print(f"                          {binario_con_puntos(int(subred_final.broadcast_address - 2))}")
        print("")
        
        print("="*40)

    except ValueError as e:
        print(f"\n[ERROR] Datos inválidos. Asegúrate de ingresar números enteros y formato CIDR correcto. \nDetalle: {e}")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió algo inesperado: {e}")

# Main
if __name__ == "__main__":
    while True:
        calcular_red_consola()
        print("\n")
        continuar = input("¿Calcular otra? (s/n): ")
        if continuar.lower() != 's':
            break
        print("\n")
