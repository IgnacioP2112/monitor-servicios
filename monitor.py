

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import URLS, CHECK_INTERVAL, MAX_FAILURES
from checker import check_service
from logger import log_result

failure_counts = {url: 0 for url in URLS} # Este diccionario lleva la cuenta de fallos consecutivos por sitio.



def check_and_log(url):
    """
    Consulta un solo sitio y registra el resultado.
    
    Esta función es la unidad de trabajo que cada thread va a ejecutar.
    Devuelve la url para que podamos identificar el resultado después.
    """
    result = check_service(url)
    log_result(result)
    return result


def run_cycle():
    
    #Ejecuta un ciclo completo de monitoreo de forma concurrente.
    #Todos los sitios se consultan en paralelo. Cuando todos terminan,
    #procesamos los resultados para actualizar contadores y generar alertas.
   
    
    # ThreadPoolExecutor crea un "pool" de threads listos para trabajar.
    # max_workers=len(URLS) significa: un thread por sitio.
    # Si tienes 5 sitios, crea hasta 5 threads simultáneos.

    with ThreadPoolExecutor(max_workers=len(URLS)) as executor:
        
        # executor.submit(función, argumento) envía una tarea al pool.
        # No la ejecuta ahora mismo — la encola para que un thread la tome.
        # Devuelve un objeto Future: una "promesa" de resultado futuro.
        #
        # Creamos un diccionario: {future: url}
        # Esto nos permite saber QUÉ url corresponde a cada future.
        futures = {
            executor.submit(check_and_log, url): url
            for url in URLS
        }
        
        # as_completed(futures) es un generador que nos entrega cada future
        # EN EL ORDEN EN QUE VAN TERMINANDO (no en el orden original).
        # Esto es importante: el sitio más rápido aparece primero.
       
        for future in as_completed(futures):
            url = futures[future]  # Recuperamos la url de este future
            
            try:
                # future.result() obtiene el valor que retornó check_and_log.
                # Si check_and_log lanzó una excepción, aquí se re-lanza.
                result = future.result()
                
                # Lógica de contadores (igual que antes, pero ahora
                # la aplicamos sobre el resultado que ya llegó)

                CODIGOS_OK = [200, 403, 301, 302]
                if result["error"] or result["status"] not in CODIGOS_OK:
                    failure_counts[url] += 1
                else:
                    failure_counts[url] = 0  # Reset si el sitio volvió
                
                if failure_counts[url] >= MAX_FAILURES:
                    # Generamos la alerta de servicio caído
                    alert = {
                        "url": url,
                        "status": None,
                        "response_time": None,
                        "error": "SERVICE DOWN"
                    }
                    log_result(alert)
                    failure_counts[url] = 0  # Reset para no spamear alertas
                    
            except Exception as e:
                # Si algo inesperado falla dentro del thread, lo capturamos
                # aquí para que NO mate todo el programa.
                print(f"[ERROR INESPERADO] {url}: {e}")


def main():
    
    #Bucle principal: ejecuta ciclos indefinidamente con pausa entre cada uno.
    
    print("Monitor iniciado (modo concurrente)")
    print(f"Monitoreando {len(URLS)} sitios cada {CHECK_INTERVAL} segundos\n")
    
    while True:
        run_cycle()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()