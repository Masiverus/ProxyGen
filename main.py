import requests
import threading
import time
from colorama import Fore, Style, init

# Inicializa colorama
init(autoreset=True)

# URL de prueba (puedes cambiarla según tus necesidades)
test_url = "https://www.google.com/"

# Número de hilos para verificar los proxies de manera paralela
num_threads = 100

# Límite de tiempo para las solicitudes de prueba (en segundos)
timeout = 5

# URL de la API que proporciona proxies
proxy_api_url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"

# Archivo de salida para proxies que funcionan bien
output_file = "generated.txt"

# Bloqueo para imprimir de manera ordenada
print_lock = threading.Lock()

# Función para verificar un proxy y medir su velocidad
def check_proxy(proxy):
    start_time = time.time()
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=timeout)
        elapsed_time = time.time() - start_time
        if response.status_code == 200:
            result = f"[{proxy}] {Fore.GREEN}VÁLIDO{Style.RESET_ALL} ({elapsed_time:.2f} segundos)"
            save_good_proxy(proxy)
        else:
            result = f"[{proxy}] {Fore.RED}INVÁLIDO{Style.RESET_ALL} (Código de estado: {response.status_code})"
        with print_lock:
            print(result)
    except (requests.exceptions.ProxyError, requests.exceptions.RequestException):
        result = f"[{proxy}] {Fore.RED}INVÁLIDO{Style.RESET_ALL} (Error al conectar)"
        with print_lock:
            print(result)
    except Exception as e:
        pass  # Ignora otros errores

# Función para guardar un proxy que funciona bien en el archivo "good.txt"
def save_good_proxy(proxy):
    with open(output_file, "a") as f:
        f.write(proxy + "\n")

# Limpia el archivo "good.txt" antes de comenzar
open(output_file, "w").close()

# Obtiene los proxies de la URL de la API y elimina espacios en blanco
response = requests.get(proxy_api_url)
proxies = [line.strip() for line in response.text.splitlines()]

# Crea y ejecuta los hilos
threads = []
for proxy in proxies:
    thread = threading.Thread(target=check_proxy, args=(proxy,))
    threads.append(thread)
    thread.start()

# Espera a que todos los hilos terminen
for thread in threads:
    thread.join()

print("Verificación de proxies completada.")