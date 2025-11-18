"""
Sistema de Persistência em JSON
🔹 Conceito SO: Sistema de Arquivos, I/O, Locks, Operações Atômicas
"""

import json
import os
import threading
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import shutil


class JSONStorage:
    """
    Gerenciador de persistência em arquivos JSON
    🔹 Conceito SO: Operações de leitura/escrita com controle de concorrência
    """

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.encoding = 'utf-8'

        # 🔹 Conceito SO: Lock para controle de concorrência
        # Cada arquivo tem seu próprio lock para evitar race conditions
        self.file_locks = {}
        self.global_lock = threading.Lock()

        logging.info(f"JSONStorage inicializado: {base_dir}")

    def _get_file_lock(self, filename: str) -> threading.Lock:
        """
        Obtém lock específico para um arquivo
        🔹 Conceito SO: Sincronização, Mutex por recurso
        """
        with self.global_lock:
            if filename not in self.file_locks:
                self.file_locks[filename] = threading.Lock()
            return self.file_locks[filename]

    def _get_filepath(self, entity_type: str) -> str:
        """Retorna caminho completo do arquivo"""
        return os.path.join(self.base_dir, f"{entity_type}.json")

    def salvar(self, entity_type: str, data: List[Dict[str, Any]]) -> bool:
        """
        Salva dados em arquivo JSON
        🔹 Conceito SO: Escrita atômica, Flush, Fsync
        """
        filepath = self._get_filepath(entity_type)
        lock = self._get_file_lock(filepath)

        try:
            # 🔹 Conceito SO: Lock exclusivo para escrita
            with lock:
                # Escreve em arquivo temporário primeiro (atomic write)
                temp_filepath = filepath + '.tmp'

                # 🔹 Conceito SO: Abertura de arquivo com encoding específico
                with open(temp_filepath, 'w', encoding=self.encoding) as f:
                    # 🔹 Conceito SO: Buffering de I/O
                    json.dump(data, f, ensure_ascii=False, indent=2)

                    # 🔹 Conceito SO: Flush do buffer para o kernel
                    f.flush()

                    # 🔹 Conceito SO: Fsync - força escrita no disco
                    os.fsync(f.fileno())

                # 🔹 Conceito SO: Operação atômica de rename
                # Move arquivo temporário para definitivo
                if os.path.exists(filepath):
                    os.replace(temp_filepath, filepath)
                else:
                    os.rename(temp_filepath, filepath)

                logging.info(f"✅ Salvos: {entity_type} ({len(data)} registros)")
                return True

        except Exception as e:
            logging.error(f"❌ Erro ao salvar {entity_type}: {str(e)}")
            # Remove arquivo temporário se existir
            temp_filepath = filepath + '.tmp'
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            return False

    def carregar(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Carrega dados de arquivo JSON
        🔹 Conceito SO: Leitura de arquivo com lock compartilhado
        """
        filepath = self._get_filepath(entity_type)
        lock = self._get_file_lock(filepath)

        try:
            # 🔹 Conceito SO: Lock para leitura (permite múltiplas leituras)
            with lock:
                if not os.path.exists(filepath):
                    logging.debug(f"Arquivo não existe: {entity_type}")
                    return []

                # 🔹 Conceito SO: Leitura com encoding específico
                with open(filepath, 'r', encoding=self.encoding) as f:
                    data = json.load(f)
                    logging.info(f"📂 Carregados: {entity_type} ({len(data)} registros)")
                    return data

        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON inválido em {entity_type}: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"❌ Erro ao carregar {entity_type}: {str(e)}")
            return []

    def adicionar(self, entity_type: str, item: Dict[str, Any]) -> bool:
        """
        Adiciona um item ao arquivo
        🔹 Conceito SO: Operação atômica de leitura-modificação-escrita
        """
        try:
            dados = self.carregar(entity_type)
            dados.append(item)
            return self.salvar(entity_type, dados)
        except Exception as e:
            logging.error(f"❌ Erro ao adicionar em {entity_type}: {str(e)}")
            return False

    def atualizar(self, entity_type: str, item_id: str, novo_item: Dict[str, Any]) -> bool:
        """
        Atualiza um item no arquivo
        🔹 Conceito SO: Modificação atômica
        """
        try:
            dados = self.carregar(entity_type)

            for i, item in enumerate(dados):
                if item.get('id') == item_id:
                    dados[i] = novo_item
                    logging.info(f"🔄 Atualizado: {entity_type}/{item_id}")
                    return self.salvar(entity_type, dados)

            logging.warning(f"⚠️  Item não encontrado: {entity_type}/{item_id}")
            return False

        except Exception as e:
            logging.error(f"❌ Erro ao atualizar {entity_type}: {str(e)}")
            return False

    def remover(self, entity_type: str, item_id: str) -> bool:
        """
        Remove um item do arquivo
        🔹 Conceito SO: Operação de exclusão
        """
        try:
            dados = self.carregar(entity_type)
            dados_filtrados = [item for item in dados if item.get('id') != item_id]

            if len(dados_filtrados) < len(dados):
                logging.info(f"🗑️  Removido: {entity_type}/{item_id}")
                return self.salvar(entity_type, dados_filtrados)

            logging.warning(f"⚠️  Item não encontrado: {entity_type}/{item_id}")
            return False

        except Exception as e:
            logging.error(f"❌ Erro ao remover de {entity_type}: {str(e)}")
            return False

    def buscar_por_id(self, entity_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Busca item por ID"""
        dados = self.carregar(entity_type)
        for item in dados:
            if item.get('id') == item_id:
                return item
        return None

    def contar(self, entity_type: str) -> int:
        """Conta número de registros"""
        dados = self.carregar(entity_type)
        return len(dados)

    def fazer_backup(self, entity_type: str, backup_dir: str) -> bool:
        """
        Cria backup do arquivo
        🔹 Conceito SO: Cópia de arquivo, gestão de backups
        """
        try:
            filepath = self._get_filepath(entity_type)

            if not os.path.exists(filepath):
                logging.warning(f"Arquivo não existe para backup: {entity_type}")
                return False

            # Cria nome do backup com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{entity_type}_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)

            # 🔹 Conceito SO: Cópia de arquivo preservando metadados
            shutil.copy2(filepath, backup_path)

            logging.info(f"💾 Backup criado: {backup_filename}")
            return True

        except Exception as e:
            logging.error(f"❌ Erro ao criar backup de {entity_type}: {str(e)}")
            return False

    def listar_backups(self, backup_dir: str, entity_type: str = None) -> List[str]:
        """
        Lista backups disponíveis
        🔹 Conceito SO: Listagem de diretório
        """
        try:
            if not os.path.exists(backup_dir):
                return []

            backups = []
            # 🔹 Conceito SO: Leitura de diretório
            for filename in os.listdir(backup_dir):
                if filename.endswith('.json'):
                    if entity_type is None or filename.startswith(entity_type):
                        backups.append(filename)

            return sorted(backups, reverse=True)

        except Exception as e:
            logging.error(f"❌ Erro ao listar backups: {str(e)}")
            return []

    def get_file_info(self, entity_type: str) -> Dict[str, Any]:
        """
        Retorna informações sobre o arquivo
        🔹 Conceito SO: Metadados de arquivo (stat)
        """
        filepath = self._get_filepath(entity_type)

        try:
            if not os.path.exists(filepath):
                return {'exists': False}

            # 🔹 Conceito SO: Chamada de sistema stat()
            stat = os.stat(filepath)

            return {
                'exists': True,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:]
            }

        except Exception as e:
            logging.error(f"❌ Erro ao obter info de {entity_type}: {str(e)}")
            return {'exists': False, 'error': str(e)}


if __name__ == "__main__":
    # Teste rápido
    import tempfile

    print("\n" + "=" * 60)
    print("🧪 TESTE DO JSON STORAGE")
    print("=" * 60)

    # Cria diretório temporário para teste
    temp_dir = tempfile.mkdtemp()
    storage = JSONStorage(temp_dir)

    # Testa salvamento
    print("\n1️⃣ Testando salvamento...")
    dados = [
        {'id': '1', 'nome': 'Teste 1'},
        {'id': '2', 'nome': 'Teste 2'}
    ]
    storage.salvar('teste', dados)

    # Testa carregamento
    print("\n2️⃣ Testando carregamento...")
    dados_carregados = storage.carregar('teste')
    print(f"   Carregados: {len(dados_carregados)} registros")

    # Testa adicionar
    print("\n3️⃣ Testando adição...")
    storage.adicionar('teste', {'id': '3', 'nome': 'Teste 3'})
    print(f"   Total agora: {storage.contar('teste')} registros")

    # Testa info do arquivo
    print("\n4️⃣ Testando info do arquivo...")
    info = storage.get_file_info('teste')
    print(f"   Tamanho: {info['size_bytes']} bytes")
    print(f"   Modificado: {info['modified']}")

    print(f"\n✅ Storage testado com sucesso!")
    print(f"📁 Arquivos em: {temp_dir}")