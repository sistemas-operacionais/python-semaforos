import threading
import time

contador = 0
mutex = threading.Semaphore(1)  # semáforo binário


def incrementar(nome: str) -> None:
    global contador
    for _ in range(5):
        time.sleep(0.08)
        with mutex:               # acquire() implícito
            valor_atual = contador
            time.sleep(0.03)      # simula processamento
            contador = valor_atual + 1
            print(f"[{nome}] contador = {contador}")


t1 = threading.Thread(target=incrementar, args=("Thread-1",))
t2 = threading.Thread(target=incrementar, args=("Thread-2",))

t1.start()
t2.start()
t1.join()
t2.join()

print(f"\nValor final: {contador}")  # deve ser 10