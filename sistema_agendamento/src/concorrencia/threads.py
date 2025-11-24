"""
Gerenciador de Threads e Processamento Concorrente
🔹 Conceito SO: Threads, Escalonamento, Paralelismo
"""

import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, List
from queue import Queue, Empty
import os


class ThreadManager:
    """
    Gerenciador de threads para processamento paralelo
    🔹 Conceito SO: Thread pool, escalonamento de threads
    """

    def __init__(self, max_workers: int = None):
        """
        Inicializa gerenciador de threads

        Args:
            max_workers: Número máximo de threads (padrão: núcleos do CPU)
        """
        # 🔹 Conceito SO: Detecta número de CPUs disponíveis
        if max_workers is None:
            max_workers = os.cpu_count() or 4

        self.max_workers = max_workers

        # 🔹 Conceito SO: Thread Pool Executor
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="Worker"
        )

        # Estatísticas
        self.tasks_submitted = 0
        self.tasks_completed = 0
        self.tasks_failed = 0

        # Lock para estatísticas
        self.stats_lock = threading.Lock()

        logging.info(f"ThreadManager inicializado: {max_workers} workers (CPUs: {os.cpu_count()})")

    def submit_task(self, func: Callable, *args, **kwargs) -> Future:
        """
        Submete tarefa para execução em thread
        🔹 Conceito SO: Escalonamento de tarefas

        Args:
            func: Função a ser executada
            *args, **kwargs: Argumentos da função

        Returns:
            Future object para acompanhar execução
        """
        with self.stats_lock:
            self.tasks_submitted += 1

        logging.debug(f"Tarefa submetida: {func.__name__} (total: {self.tasks_submitted})")

        # Wrapper para capturar estatísticas
        def wrapped_func():
            try:
                result = func(*args, **kwargs)
                with self.stats_lock:
                    self.tasks_completed += 1
                logging.debug(f"Tarefa concluída: {func.__name__}")
                return result
            except Exception as e:
                with self.stats_lock:
                    self.tasks_failed += 1
                logging.error(f"Tarefa falhou: {func.__name__} - {str(e)}")
                raise

        return self.executor.submit(wrapped_func)

    def map_parallel(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        Executa função para múltiplos itens em paralelo
        🔹 Conceito SO: Paralelismo de dados

        Args:
            func: Função a aplicar
            items: Lista de itens

        Returns:
            Lista de resultados
        """
        logging.info(f"Processamento paralelo: {len(items)} itens com {self.max_workers} workers")

        futures = [self.submit_task(func, item) for item in items]
        results = [future.result() for future in futures]

        return results

    def get_stats(self) -> dict:
        """
        Retorna estatísticas das threads
        🔹 Conceito SO: Monitoramento de threads
        """
        with self.stats_lock:
            return {
                'max_workers': self.max_workers,
                'tasks_submitted': self.tasks_submitted,
                'tasks_completed': self.tasks_completed,
                'tasks_failed': self.tasks_failed,
                'tasks_pending': self.tasks_submitted - self.tasks_completed - self.tasks_failed
            }

    def shutdown(self, wait: bool = True):
        """
        Finaliza thread pool
        🔹 Conceito SO: Término de threads
        """
        logging.info("Finalizando ThreadManager...")
        self.executor.shutdown(wait=wait)
        logging.info("ThreadManager finalizado")


class BackgroundWorker:
    """
    Worker para tarefas em background
    🔹 Conceito SO: Daemon threads
    """

    def __init__(self, name: str, interval: int = 60):
        """
        Args:
            name: Nome do worker
            interval: Intervalo entre execuções (segundos)
        """
        self.name = name
        self.interval = interval
        self.running = False
        self.thread = None

        logging.info(f"BackgroundWorker '{name}' criado (intervalo: {interval}s)")

    def start(self, task: Callable):
        """
        Inicia worker em background
        🔹 Conceito SO: Daemon thread que roda em background
        """
        if self.running:
            logging.warning(f"Worker '{self.name}' já está rodando")
            return

        self.running = True

        def worker_loop():
            logging.info(f"Worker '{self.name}' iniciado")

            while self.running:
                try:
                    logging.debug(f"Worker '{self.name}': Executando tarefa")
                    task()

                    # Aguarda intervalo
                    for _ in range(self.interval):
                        if not self.running:
                            break
                        time.sleep(1)

                except Exception as e:
                    logging.error(f"Worker '{self.name}' falhou: {str(e)}")
                    time.sleep(5)  # Aguarda antes de tentar novamente

            logging.info(f"Worker '{self.name}' finalizado")

        # 🔹 Conceito SO: Cria thread daemon (não bloqueia saída do programa)
        self.thread = threading.Thread(
            target=worker_loop,
            name=f"BgWorker-{self.name}",
            daemon=True
        )
        self.thread.start()

    def stop(self):
        """Para o worker"""
        if not self.running:
            return

        logging.info(f"Parando worker '{self.name}'...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=5)


class TaskQueue:
    """
    Fila de tarefas thread-safe
    🔹 Conceito SO: Producer-Consumer pattern
    """

    def __init__(self, max_size: int = 0):
        """
        Args:
            max_size: Tamanho máximo da fila (0 = ilimitado)
        """
        # 🔹 Conceito SO: Queue thread-safe
        self.queue = Queue(maxsize=max_size)
        self.processed = 0
        self.lock = threading.Lock()

        logging.info(f"TaskQueue criada (max_size: {max_size if max_size > 0 else 'ilimitado'})")

    def enqueue(self, task: Any, block: bool = True, timeout: float = None):
        """
        Adiciona tarefa na fila
        🔹 Conceito SO: Producer
        """
        try:
            self.queue.put(task, block=block, timeout=timeout)
            logging.debug(f"Tarefa enfileirada (tamanho: {self.queue.qsize()})")
        except Exception as e:
            logging.error(f"Erro ao enfileirar: {str(e)}")
            raise

    def dequeue(self, block: bool = True, timeout: float = None) -> Any:
        """
        Remove e retorna tarefa da fila
        🔹 Conceito SO: Consumer
        """
        try:
            task = self.queue.get(block=block, timeout=timeout)
            with self.lock:
                self.processed += 1
            self.queue.task_done()
            logging.debug(f"Tarefa desenfileirada (processadas: {self.processed})")
            return task
        except Empty:
            return None

    def size(self) -> int:
        """Retorna tamanho atual da fila"""
        return self.queue.qsize()

    def wait_completion(self):
        """
        Aguarda todas as tarefas serem processadas
        🔹 Conceito SO: Sincronização
        """
        self.queue.join()
        logging.info("Todas as tarefas foram processadas")


# Instância global do gerenciador de threads
thread_manager = ThreadManager()

if __name__ == "__main__":
    # Teste do sistema de threads
    print("\n" + "=" * 60)
    print("🧪 TESTE DO SISTEMA DE THREADS")
    print("=" * 60)

    # Configura logging
    logging.basicConfig(level=logging.INFO)

    # Teste 1: ThreadManager
    print("\n1️⃣ Testando ThreadManager...")


    def task_exemplo(n):
        """Tarefa de exemplo que simula processamento"""
        print(f"   Thread {threading.current_thread().name}: Processando {n}")
        time.sleep(0.5)  # Simula trabalho
        return n * 2


    manager = ThreadManager(max_workers=3)

    # Submete tarefas
    futures = []
    for i in range(5):
        future = manager.submit_task(task_exemplo, i)
        futures.append(future)

    # Aguarda resultados
    resultados = [f.result() for f in futures]
    print(f"   Resultados: {resultados}")

    stats = manager.get_stats()
    print(f"   Estatísticas: {stats}")

    # Teste 2: BackgroundWorker
    print("\n2️⃣ Testando BackgroundWorker...")

    contador = [0]


    def tarefa_periodica():
        contador[0] += 1
        print(f"   Execução #{contador[0]} do worker")


    worker = BackgroundWorker("teste", interval=2)
    worker.start(tarefa_periodica)

    print("   Worker rodando por 5 segundos...")
    time.sleep(5)
    worker.stop()

    # Teste 3: TaskQueue
    print("\n3️⃣ Testando TaskQueue...")

    fila = TaskQueue(max_size=10)

    # Producer
    for i in range(5):
        fila.enqueue(f"tarefa_{i}")

    print(f"   Fila criada com {fila.size()} tarefas")

    # Consumer
    while fila.size() > 0:
        tarefa = fila.dequeue()
        print(f"   Processando: {tarefa}")

    manager.shutdown()
    print("\n✅ Todos os testes passaram!")