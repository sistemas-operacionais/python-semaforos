import threading
import time
import random

N = 5  # número de filósofos (e de garfos)

# Cada garfo é um semáforo binário
garfos = [threading.Semaphore(1) for _ in range(N)]

# No máximo N-1 filósofos podem tentar pegar garfos simultaneamente
mesa = threading.Semaphore(N - 1)


def pensar(filosofo_id: int) -> None:
    duracao = random.uniform(1, 3)
    print(f"Filósofo {filosofo_id} está PENSANDO por {duracao:.1f}s")
    time.sleep(duracao)


def comer(filosofo_id: int) -> None:
    duracao = random.uniform(1, 2)
    print(f"Filósofo {filosofo_id} está COMENDO  por {duracao:.1f}s")
    time.sleep(duracao)


def filosofo(filosofo_id: int, rodadas: int) -> None:
    esquerdo = filosofo_id
    direito  = (filosofo_id + 1) % N

    for rodada in range(1, rodadas + 1):
        pensar(filosofo_id)

        print(f"Filósofo {filosofo_id} (rodada {rodada}): quer comer, aguardando garfos...")
        mesa.acquire()                  # "senta à mesa" (limita concorrência)

        garfos[esquerdo].acquire()      # pega garfo esquerdo
        print(f"Filósofo {filosofo_id}: pegou garfo esquerdo ({esquerdo})")
        time.sleep(0.9)
        garfos[direito].acquire()       # pega garfo direito
        print(f"Filósofo {filosofo_id}: pegou garfo direito  ({direito})")

        comer(filosofo_id)

        garfos[direito].release()       # devolve garfo direito
        garfos[esquerdo].release()      # devolve garfo esquerdo
        mesa.release()                  # "levanta da mesa"
        print(f"Filósofo {filosofo_id}: devolveu os garfos")


RODADAS = 3

threads = [
    threading.Thread(target=filosofo, args=(i, RODADAS), name=f"Filósofo-{i}")
    for i in range(N)
]

print("=== Jantar dos Filósofos iniciado ===\n")
for t in threads:
    t.start()
for t in threads:
    t.join()
print("\n=== Jantar encerrado ===")