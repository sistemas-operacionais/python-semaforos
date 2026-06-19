import threading
import time
import random

MAX_CONEXOES = 3
pool = threading.Semaphore(MAX_CONEXOES)


def usar_banco(cliente_id: int) -> None:
    print(f"Cliente {cliente_id}: aguardando conexão...")
    with pool:
        print(f"Cliente {cliente_id}: CONECTADO  (conexões disponíveis reduzidas)")
        time.sleep(random.uniform(0.5, 1.5))  # simula consulta
        print(f"Cliente {cliente_id}: desconectado")


threads = [
    threading.Thread(target=usar_banco, args=(i,))
    for i in range(1, 8)          # 7 clientes competindo por 3 vagas
]

for t in threads:
    t.start()
for t in threads:
    t.join()