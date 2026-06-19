import threading
import time
import random
from collections import deque

TAMANHO_BUFFER = 5
# buffer: deque = deque()
buffer = []

# vazios: quantas posições livres existem no buffer
# cheios:  quantos itens estão disponíveis para consumo
vazios = threading.Semaphore(TAMANHO_BUFFER)
cheios = threading.Semaphore(0)
mutex  = threading.Semaphore(1)   # protege o acesso ao buffer

def produtor_sem_semaforo(n_itens: int) -> None:
    for i in range(n_itens):
        item = random.randint(1, 100)
        buffer.append(item)
        print(f"[Produtor] produziu {item:3d} | buffer={list(buffer)}")
        time.sleep(random.uniform(0.1, 0.3))

def produtor(n_itens: int) -> None:
    for i in range(n_itens):
        item = random.randint(1, 100)
        vazios.acquire()           # espera haver espaço
        with mutex: # mutex.acquire()
            buffer.append(item)
            print(f"[Produtor] produziu {item:3d} | buffer={list(buffer)}")
        # mutex.release()
        cheios.release()           # sinaliza novo item disponível
        time.sleep(random.uniform(0.1, 0.3))

def consumidor_sem_semaforo(n_itens: int) -> None:
    for _ in range(n_itens):
        item = buffer.popleft()
        print(f"[Consumidor] consumiu {item:3d} | buffer={list(buffer)}")
        time.sleep(random.uniform(0.2, 0.5))

def consumidor(n_itens: int) -> None:
    for _ in range(n_itens):
        cheios.acquire()           # espera haver item
        with mutex:
            # item = buffer.popleft()
            item = buffer.pop()
            print(f"[Consumidor] consumiu {item:3d} | buffer={list(buffer)}")
        vazios.release()           # sinaliza espaço livre
        time.sleep(random.uniform(0.2, 0.5))


N = 10
# t_prod = threading.Thread(target=produtor_sem_semaforo,   args=(N,))
# t_cons = threading.Thread(target=consumidor_sem_semaforo, args=(N,))
t_prod = threading.Thread(target=produtor,   args=(N,))
t_cons = threading.Thread(target=consumidor, args=(N,))

t_prod.start()
t_cons.start()
t_prod.join()
t_cons.join()