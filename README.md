# Notas de aula de 2026.1 - Python Semáforos

## Informações gerais

- **Público alvo**: alunos da disciplina de **Sistemas operacionais** do curso de [ADS](https://diatinf.ifrn.edu.br/cursos/tecnologia-em-analise-e-desenvolvimento-de-sistemas/) na [DIATINF](https://diatinf.ifrn.edu.br/) no [CNAT-IFRN](https://diatinf.ifrn.edu.br/).
- **Professor**: [L A Minora](https://github.com/leonardo-minora/)
- **Objetivo**:
  1. Apresentar implementação de semáforos em python

---

## Sumário

1. [O que é um Semáforo?](#1-o-que-é-um-semáforo)
2. [Semáforos em Python](#2-semáforos-em-python)
3. [Exemplo 1 – Exclusão mútua (mutex)](#3-exemplo-1--exclusão-mútua-mutex)
4. [Exemplo 2 – Semáforo contador](#4-exemplo-2--semáforo-contador)
5. [Exemplo 3 – Produtor e Consumidor](#5-exemplo-3--produtor-e-consumidor)
6. [Problema Clássico: Jantar dos Filósofos](#6-problema-clássico-jantar-dos-filósofos)

---

## 1. O que é um Semáforo?

Um **semáforo** é um mecanismo de sincronização utilizado em sistemas operacionais para controlar o acesso concorrente a recursos compartilhados entre múltiplas _threads_ ou processos.

O conceito foi proposto por **Edsger Dijkstra** em 1965. Um semáforo é, essencialmente, uma variável inteira não-negativa associada a duas operações atômicas:

| Operação | Nome original (Dijkstra) | Nome em Python     | Efeito                                                                 |
|----------|--------------------------|--------------------|------------------------------------------------------------------------|
| Adquirir | **P** (_proberen_)       | `acquire()` / `wait()` | Decrementa o contador; bloqueia se o valor for 0                   |
| Liberar  | **V** (_verhogen_)       | `release()` / `signal()` | Incrementa o contador; acorda uma thread bloqueada, se houver    |

### Tipos de semáforo

| Tipo               | Valor inicial | Uso típico                                      |
|--------------------|---------------|-------------------------------------------------|
| **Binário (mutex)**| 1             | Garantir que apenas uma thread acessa um recurso |
| **Contador**       | N > 1         | Limitar o número de acessos simultâneos          |

---

## 2. Semáforos em Python

Python disponibiliza semáforos no módulo `threading`:

```python
import threading

# Semáforo contador (valor inicial = N)
sem = threading.Semaphore(N)

# Semáforo binário (valor inicial = 1)
mutex = threading.Semaphore(1)

# Versão que lança ValueError se release() for chamado além do valor inicial
mutex_seguro = threading.BoundedSemaphore(1)
```

### Métodos principais

```python
sem.acquire()          # bloqueia até o semáforo estar disponível (P)
sem.acquire(blocking=False)  # tenta adquirir sem bloquear; retorna True/False
sem.release()          # libera o semáforo (V)

# Uso com gerenciador de contexto (recomendado)
with sem:
    # seção crítica
    ...
```

---

## 3. Exemplo 1 – Exclusão mútua (mutex)

Quando duas ou mais threads precisam escrever em um recurso compartilhado (ex.: um arquivo ou uma variável), usamos um semáforo binário para garantir que apenas uma thread execute a **seção crítica** por vez.

```python
import threading
import time

contador = 0
mutex = threading.Semaphore(1)  # semáforo binário


def incrementar(nome: str) -> None:
    global contador
    for _ in range(5):
        with mutex:               # acquire() implícito
            valor_atual = contador
            time.sleep(0.01)      # simula processamento
            contador = valor_atual + 1
            print(f"[{nome}] contador = {contador}")


t1 = threading.Thread(target=incrementar, args=("Thread-1",))
t2 = threading.Thread(target=incrementar, args=("Thread-2",))

t1.start()
t2.start()
t1.join()
t2.join()

print(f"\nValor final: {contador}")  # deve ser 10
```

**O que aconteceria sem o mutex?**  
Sem sincronização, ambas as threads poderiam ler `contador` ao mesmo tempo, incrementar cópias locais e sobrescrever o resultado uma da outra — produzindo um valor final menor que 10 (_race condition_).

---

## 4. Exemplo 2 – Semáforo contador

Um semáforo contador limita quantas threads podem acessar um recurso simultaneamente. O exemplo abaixo simula um banco de dados que suporta no máximo **3 conexões** simultâneas.

```python
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
```

**Resultado esperado**: nunca mais de 3 linhas "CONECTADO" aparecem ao mesmo tempo na saída.

---

## 5. Exemplo 3 – Produtor e Consumidor

O problema clássico **Produtor-Consumidor** usa dois semáforos para coordenar threads que produzem e consomem itens de um _buffer_ de tamanho fixo.

```python
import threading
import time
import random
from collections import deque

TAMANHO_BUFFER = 5
buffer: deque = deque()

# vazios: quantas posições livres existem no buffer
# cheios:  quantos itens estão disponíveis para consumo
vazios = threading.Semaphore(TAMANHO_BUFFER)
cheios = threading.Semaphore(0)
mutex  = threading.Semaphore(1)   # protege o acesso ao buffer


def produtor(n_itens: int) -> None:
    for i in range(n_itens):
        item = random.randint(1, 100)
        vazios.acquire()           # espera haver espaço
        with mutex:
            buffer.append(item)
            print(f"[Produtor] produziu {item:3d} | buffer={list(buffer)}")
        cheios.release()           # sinaliza novo item disponível
        time.sleep(random.uniform(0.1, 0.3))


def consumidor(n_itens: int) -> None:
    for _ in range(n_itens):
        cheios.acquire()           # espera haver item
        with mutex:
            item = buffer.popleft()
            print(f"[Consumidor] consumiu {item:3d} | buffer={list(buffer)}")
        vazios.release()           # sinaliza espaço livre
        time.sleep(random.uniform(0.2, 0.5))


N = 10
t_prod = threading.Thread(target=produtor,   args=(N,))
t_cons = threading.Thread(target=consumidor, args=(N,))

t_prod.start()
t_cons.start()
t_prod.join()
t_cons.join()
```

---

## 6. Problema Clássico: Jantar dos Filósofos

### Descrição do problema

Cinco filósofos sentam ao redor de uma mesa circular. Entre cada par de filósofos há um garfo — totalmente 5 garfos. Cada filósofo alterna entre **pensar** e **comer**. Para comer, ele precisa pegar os **dois garfos** adjacentes (esquerdo e direito).

O desafio é evitar:

- **Deadlock**: todos pegam o garfo da esquerda ao mesmo tempo e ficam esperando o da direita indefinidamente.
- **Starvation**: um filósofo nunca consegue comer porque os vizinhos monopolizam os garfos.

### Solução com semáforos

A estratégia adotada abaixo usa:

1. Um semáforo binário por garfo (`garfos[i]`).
2. Um **semáforo limitador** (`mesa`) que permite no máximo **N-1** filósofos tentando sentar ao mesmo tempo. Isso quebra a condição de espera circular e previne deadlock.

```python
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
```

### Por que o semáforo `mesa` evita deadlock?

| Cenário sem `mesa`                           | Cenário com `mesa` (N-1 = 4)                       |
|----------------------------------------------|----------------------------------------------------|
| Os 5 filósofos pegam o garfo esquerdo ao mesmo tempo | No máximo 4 filósofos tentam pegar garfos ao mesmo tempo |
| Todos ficam esperando o garfo direito → **deadlock** | Pelo menos 1 filósofo consegue pegar os dois garfos e comer |
| Nenhum progride                              | Após comer, ele libera os garfos e os vizinhos progridem |

### Exemplo de saída

```
=== Jantar dos Filósofos iniciado ===

Filósofo 0 está PENSANDO por 2.3s
Filósofo 1 está PENSANDO por 1.1s
Filósofo 2 está PENSANDO por 2.8s
Filósofo 3 está PENSANDO por 1.7s
Filósofo 4 está PENSANDO por 0.9s
Filósofo 4 (rodada 1): quer comer, aguardando garfos...
Filósofo 4: pegou garfo esquerdo (4)
Filósofo 4: pegou garfo direito  (0)
Filósofo 4 está COMENDO  por 1.4s
...
=== Jantar encerrado ===
```

---

> **Referências**
> - Dijkstra, E. W. (1965). *Cooperating Sequential Processes*.
> - Silberschatz, A.; Galvin, P. B.; Gagne, G. *Operating System Concepts*, 10ª ed.
> - Documentação oficial Python – [`threading.Semaphore`](https://docs.python.org/3/library/threading.html#semaphore-objects)
