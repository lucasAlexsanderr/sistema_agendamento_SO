"""
Sistema de Cache em Memória
🔹 Conceito SO: Gerência de Memória, Cache LRU
"""

import logging
import threading
import time
from typing import Any, Optional
from collections import OrderedDict


class CacheManager:
    """
    Gerenciador de cache LRU (Least Recently Used)
    🔹 Conceito SO: Alocação dinâmica de memória, política de substituição
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Inicializa cache

        Args:
            max_size: Número máximo de itens no cache
            ttl_seconds: Tempo de vida dos itens (Time To Live)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

        # 🔹 Conceito SO: Estrutura de dados em memória RAM
        self.cache = OrderedDict()
        self.timestamps = {}

        # Estatísticas de desempenho
        self.hits = 0  # Cache hits
        self.misses = 0  # Cache misses
        self.evictions = 0  # Itens removidos por falta de espaço

        # 🔹 Conceito SO: Lock para thread-safety
        self.lock = threading.Lock()

        logging.info(f"Cache inicializado: max_size={max_size}, ttl={ttl_seconds}s")

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera item do cache
        🔹 Conceito SO: Acesso à memória, cache hit/miss
        """
        with self.lock:
            # Verifica se existe no cache
            if key not in self.cache:
                self.misses += 1
                logging.debug(f"Cache MISS: {key}")
                return None

            # Verifica TTL (Time To Live)
            if self._is_expired(key):
                self._remove(key)
                self.misses += 1
                logging.debug(f"Cache MISS (expirado): {key}")
                return None

            # Move para o final (mais recentemente usado)
            # 🔹 Conceito SO: Política LRU
            self.cache.move_to_end(key)
            self.hits += 1
            logging.debug(f"Cache HIT: {key}")

            return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Armazena item no cache
        🔹 Conceito SO: Alocação de memória, eviction policy
        """
        with self.lock:
            # Se já existe, atualiza e move para o final
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache[key] = value
                self.timestamps[key] = time.time()
                logging.debug(f"Cache UPDATE: {key}")
                return

            # Se cache está cheio, remove o mais antigo (LRU)
            # 🔹 Conceito SO: Eviction - similar à substituição de páginas
            if len(self.cache) >= self.max_size:
                self._evict_oldest()

            # Adiciona novo item
            self.cache[key] = value
            self.timestamps[key] = time.time()
            logging.debug(f"Cache SET: {key} (total: {len(self.cache)})")

    def delete(self, key: str) -> bool:
        """
        Remove item do cache
        🔹 Conceito SO: Liberação explícita de memória
        """
        with self.lock:
            if key in self.cache:
                self._remove(key)
                logging.debug(f"Cache DELETE: {key}")
                return True
            return False

    def clear(self) -> None:
        """
        Limpa todo o cache
        🔹 Conceito SO: Liberação em massa de memória
        """
        with self.lock:
            size_before = len(self.cache)
            self.cache.clear()
            self.timestamps.clear()
            logging.info(f"Cache limpo: {size_before} itens removidos")

    def _is_expired(self, key: str) -> bool:
        """Verifica se item expirou baseado no TTL"""
        if key not in self.timestamps:
            return True

        age = time.time() - self.timestamps[key]
        return age > self.ttl_seconds

    def _evict_oldest(self) -> None:
        """
        Remove o item mais antigo do cache (LRU)
        🔹 Conceito SO: Política de substituição - similar a page replacement
        """
        if self.cache:
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)
            self.evictions += 1
            logging.debug(f"Cache EVICT: {oldest_key}")

    def _remove(self, key: str) -> None:
        """Remove item do cache e timestamp"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache
        🔹 Conceito SO: Monitoramento de uso de memória
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate_percent': round(hit_rate, 2),
                'memory_usage_percent': round((len(self.cache) / self.max_size) * 100, 2)
            }

    def print_stats(self) -> None:
        """Imprime estatísticas formatadas"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("📊 ESTATÍSTICAS DO CACHE")
        print("=" * 50)
        print(f"Tamanho: {stats['size']}/{stats['max_size']} ({stats['memory_usage_percent']}%)")
        print(f"Hits: {stats['hits']}")
        print(f"Misses: {stats['misses']}")
        print(f"Evictions: {stats['evictions']}")
        print(f"Hit Rate: {stats['hit_rate_percent']}%")
        print("=" * 50)

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida todos os itens que correspondem ao padrão
        🔹 Conceito SO: Invalidação de cache
        """
        with self.lock:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]

            for key in keys_to_remove:
                self._remove(key)

            if keys_to_remove:
                logging.info(f"Cache invalidado: {len(keys_to_remove)} itens com padrão '{pattern}'")

            return len(keys_to_remove)

    def cleanup_expired(self) -> int:
        """
        Remove todos os itens expirados
        🔹 Conceito SO: Garbage collection manual
        """
        with self.lock:
            expired_keys = [k for k in self.cache.keys() if self._is_expired(k)]

            for key in expired_keys:
                self._remove(key)

            if expired_keys:
                logging.info(f"Cleanup: {len(expired_keys)} itens expirados removidos")

            return len(expired_keys)


# Instância global do cache
cache_manager = CacheManager(max_size=100, ttl_seconds=300)

if __name__ == "__main__":
    # Teste rápido
    print("\n" + "=" * 60)
    print("🧪 TESTE DO CACHE")
    print("=" * 60)

    cache = CacheManager(max_size=5, ttl_seconds=2)

    # Testa adição
    print("\n1️⃣ Adicionando itens...")
    for i in range(7):
        cache.set(f"key_{i}", f"valor_{i}")
        print(f"   Adicionado: key_{i}")

    cache.print_stats()

    # Testa recuperação
    print("\n2️⃣ Recuperando itens...")
    print(f"   key_0: {cache.get('key_0')}")  # Deve ser None (foi removido)
    print(f"   key_5: {cache.get('key_5')}")  # Deve existir

    cache.print_stats()

    # Testa TTL
    print("\n3️⃣ Testando TTL (aguarde 3 segundos)...")
    time.sleep(3)
    print(f"   key_5 após TTL: {cache.get('key_5')}")  # Deve ser None (expirado)

    cache.print_stats()

    print("\n✅ Cache testado com sucesso!")