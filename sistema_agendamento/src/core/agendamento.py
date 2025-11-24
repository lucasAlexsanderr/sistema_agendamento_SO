"""
Serviço de Agendamento com Verificação de Conflitos
🔹 Conceito SO: Concorrência, Sincronização, Race Conditions
"""

import logging
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .models import Paciente, Medico, Consulta
from .cache import cache_manager
from storage import JSONStorage


class AgendamentoService:
    """
    Serviço principal de agendamento
    🔹 Conceito SO: Controle de concorrência com locks
    """

    def __init__(self, storage: JSONStorage):
        self.storage = storage

        # 🔹 Conceito SO: Lock para operações críticas
        # Evita race conditions quando múltiplas threads tentam agendar o mesmo horário
        self.agendamento_lock = threading.Lock()

        logging.info("AgendamentoService inicializado")

    # ==================== PACIENTES ====================

    def criar_paciente(self, nome: str, cpf: str, telefone: str, email: str) -> Tuple[bool, str, Optional[Paciente]]:
        """
        Cria novo paciente
        Returns: (sucesso, mensagem, paciente)
        """
        try:
            # Verifica se CPF já existe
            pacientes = self.listar_pacientes()
            if any(p.cpf == cpf for p in pacientes):
                return False, "CPF já cadastrado", None

            paciente = Paciente(nome, cpf, telefone, email)

            if self.storage.adicionar('pacientes', paciente.to_dict()):
                # Invalida cache
                cache_manager.invalidate_pattern('pacientes')
                logging.info(f"Paciente criado: {paciente.id}")
                return True, "Paciente cadastrado com sucesso", paciente

            return False, "Erro ao salvar paciente", None

        except Exception as e:
            logging.error(f"Erro ao criar paciente: {str(e)}")
            return False, f"Erro: {str(e)}", None

    def listar_pacientes(self) -> List[Paciente]:
        """Lista todos os pacientes"""
        # Tenta buscar do cache primeiro
        cache_key = 'pacientes:all'
        cached = cache_manager.get(cache_key)

        if cached:
            logging.debug("Pacientes recuperados do cache")
            return [Paciente.from_dict(p) for p in cached]

        # Se não está em cache, busca do storage
        dados = self.storage.carregar('pacientes')
        pacientes = [Paciente.from_dict(p) for p in dados]

        # Coloca no cache
        cache_manager.set(cache_key, dados)

        return pacientes

    def buscar_paciente(self, paciente_id: str) -> Optional[Paciente]:
        """Busca paciente por ID"""
        cache_key = f'paciente:{paciente_id}'
        cached = cache_manager.get(cache_key)

        if cached:
            return Paciente.from_dict(cached)

        dados = self.storage.buscar_por_id('pacientes', paciente_id)
        if dados:
            cache_manager.set(cache_key, dados)
            return Paciente.from_dict(dados)

        return None

    def atualizar_paciente(self, paciente_id: str, nome: str, cpf: str,
                           telefone: str, email: str) -> Tuple[bool, str]:
        """Atualiza dados do paciente"""
        try:
            paciente = self.buscar_paciente(paciente_id)
            if not paciente:
                return False, "Paciente não encontrado"

            # Atualiza dados
            paciente.nome = nome
            paciente.cpf = cpf
            paciente.telefone = telefone
            paciente.email = email

            if self.storage.atualizar('pacientes', paciente_id, paciente.to_dict()):
                # Invalida cache
                cache_manager.delete(f'paciente:{paciente_id}')
                cache_manager.invalidate_pattern('pacientes')
                logging.info(f"Paciente atualizado: {paciente_id}")
                return True, "Paciente atualizado com sucesso"

            return False, "Erro ao atualizar paciente"

        except Exception as e:
            logging.error(f"Erro ao atualizar paciente: {str(e)}")
            return False, f"Erro: {str(e)}"

    def remover_paciente(self, paciente_id: str) -> Tuple[bool, str]:
        """Remove paciente"""
        try:
            # Verifica se tem consultas
            consultas = self.listar_consultas_paciente(paciente_id)
            consultas_ativas = [c for c in consultas if c.status not in
                                [Consulta.STATUS_CANCELADA, Consulta.STATUS_REALIZADA]]

            if consultas_ativas:
                return False, "Paciente possui consultas ativas"

            if self.storage.remover('pacientes', paciente_id):
                cache_manager.delete(f'paciente:{paciente_id}')
                cache_manager.invalidate_pattern('pacientes')
                logging.info(f"Paciente removido: {paciente_id}")
                return True, "Paciente removido com sucesso"

            return False, "Erro ao remover paciente"

        except Exception as e:
            logging.error(f"Erro ao remover paciente: {str(e)}")
            return False, f"Erro: {str(e)}"

    # ==================== MÉDICOS ====================

    def criar_medico(self, nome: str, crm: str, especialidade: str,
                     horarios: List[str]) -> Tuple[bool, str, Optional[Medico]]:
        """Cria novo médico"""
        try:
            # Verifica se CRM já existe
            medicos = self.listar_medicos()
            if any(m.crm == crm for m in medicos):
                return False, "CRM já cadastrado", None

            medico = Medico(nome, crm, especialidade, horarios)

            if self.storage.adicionar('medicos', medico.to_dict()):
                cache_manager.invalidate_pattern('medicos')
                logging.info(f"Médico criado: {medico.id}")
                return True, "Médico cadastrado com sucesso", medico

            return False, "Erro ao salvar médico", None

        except Exception as e:
            logging.error(f"Erro ao criar médico: {str(e)}")
            return False, f"Erro: {str(e)}", None

    def listar_medicos(self) -> List[Medico]:
        """Lista todos os médicos"""
        cache_key = 'medicos:all'
        cached = cache_manager.get(cache_key)

        if cached:
            return [Medico.from_dict(m) for m in cached]

        dados = self.storage.carregar('medicos')
        medicos = [Medico.from_dict(m) for m in dados]
        cache_manager.set(cache_key, dados)

        return medicos

    def buscar_medico(self, medico_id: str) -> Optional[Medico]:
        """Busca médico por ID"""
        cache_key = f'medico:{medico_id}'
        cached = cache_manager.get(cache_key)

        if cached:
            return Medico.from_dict(cached)

        dados = self.storage.buscar_por_id('medicos', medico_id)
        if dados:
            cache_manager.set(cache_key, dados)
            return Medico.from_dict(dados)

        return None

    # ==================== CONSULTAS ====================

    def verificar_conflito(self, medico_id: str, data: str, hora: str,
                           consulta_id: str = None) -> Tuple[bool, str]:
        """
        Verifica se existe conflito de agendamento
        🔹 Conceito SO: Seção crítica protegida por lock

        Returns: (tem_conflito, mensagem)
        """
        consultas = self.listar_consultas()

        for consulta in consultas:
            # Ignora a própria consulta (para updates)
            if consulta_id and consulta.id == consulta_id:
                continue

            # Ignora consultas canceladas
            if consulta.status == Consulta.STATUS_CANCELADA:
                continue

            # Verifica conflito
            if (consulta.medico_id == medico_id and
                    consulta.data == data and
                    consulta.hora == hora):
                return True, "Horário já ocupado para este médico"

        return False, "Horário disponível"

    def agendar_consulta(self, paciente_id: str, medico_id: str,
                         data: str, hora: str, observacoes: str = "") -> Tuple[bool, str, Optional[Consulta]]:
        """
        Agenda nova consulta
        🔹 Conceito SO: Lock exclusivo para evitar race condition
        """
        try:
            # 🔹 SEÇÃO CRÍTICA: Lock para evitar agendamentos simultâneos
            with self.agendamento_lock:
                logging.info(f"Thread {threading.current_thread().name}: Tentando agendar {data} {hora}")

                # Verifica se paciente existe
                paciente = self.buscar_paciente(paciente_id)
                if not paciente:
                    return False, "Paciente não encontrado", None

                # Verifica se médico existe
                medico = self.buscar_medico(medico_id)
                if not medico:
                    return False, "Médico não encontrado", None

                # Verifica se horário está disponível para o médico
                if hora not in medico.horarios_disponiveis:
                    return False, "Horário não disponível para este médico", None

                # 🔹 VERIFICAÇÃO DE CONFLITO (seção crítica)
                tem_conflito, msg = self.verificar_conflito(medico_id, data, hora)
                if tem_conflito:
                    logging.warning(f"Conflito detectado: {msg}")
                    return False, msg, None

                # Cria consulta
                consulta = Consulta(paciente_id, medico_id, data, hora, observacoes)

                if self.storage.adicionar('consultas', consulta.to_dict()):
                    cache_manager.invalidate_pattern('consultas')
                    logging.info(f"Consulta agendada: {consulta.id}")
                    return True, "Consulta agendada com sucesso", consulta

                return False, "Erro ao salvar consulta", None

        except Exception as e:
            logging.error(f"Erro ao agendar consulta: {str(e)}")
            return False, f"Erro: {str(e)}", None

    def listar_consultas(self) -> List[Consulta]:
        """Lista todas as consultas"""
        cache_key = 'consultas:all'
        cached = cache_manager.get(cache_key)

        if cached:
            return [Consulta.from_dict(c) for c in cached]

        dados = self.storage.carregar('consultas')
        consultas = [Consulta.from_dict(c) for c in dados]
        cache_manager.set(cache_key, dados)

        return consultas

    def listar_consultas_paciente(self, paciente_id: str) -> List[Consulta]:
        """Lista consultas de um paciente"""
        consultas = self.listar_consultas()
        return [c for c in consultas if c.paciente_id == paciente_id]

    def listar_consultas_medico(self, medico_id: str) -> List[Consulta]:
        """Lista consultas de um médico"""
        consultas = self.listar_consultas()
        return [c for c in consultas if c.medico_id == medico_id]

    def buscar_consulta(self, consulta_id: str) -> Optional[Consulta]:
        """Busca consulta por ID"""
        dados = self.storage.buscar_por_id('consultas', consulta_id)
        if dados:
            return Consulta.from_dict(dados)
        return None

    def atualizar_status_consulta(self, consulta_id: str, novo_status: str) -> Tuple[bool, str]:
        """Atualiza status da consulta"""
        try:
            consulta = self.buscar_consulta(consulta_id)
            if not consulta:
                return False, "Consulta não encontrada"

            if consulta.atualizar_status(novo_status):
                if self.storage.atualizar('consultas', consulta_id, consulta.to_dict()):
                    cache_manager.invalidate_pattern('consultas')
                    logging.info(f"Status atualizado: {consulta_id} -> {novo_status}")
                    return True, f"Status atualizado para {novo_status}"

            return False, "Status inválido"

        except Exception as e:
            logging.error(f"Erro ao atualizar status: {str(e)}")
            return False, f"Erro: {str(e)}"

    def cancelar_consulta(self, consulta_id: str) -> Tuple[bool, str]:
        """Cancela consulta"""
        return self.atualizar_status_consulta(consulta_id, Consulta.STATUS_CANCELADA)

    def get_estatisticas(self) -> Dict:
        """
        Retorna estatísticas do sistema
        🔹 Conceito SO: Agregação de dados em memória
        """
        try:
            pacientes = self.listar_pacientes()
            medicos = self.listar_medicos()
            consultas = self.listar_consultas()

            consultas_por_status = {}
            for status in [Consulta.STATUS_AGENDADA, Consulta.STATUS_CONFIRMADA,
                           Consulta.STATUS_REALIZADA, Consulta.STATUS_CANCELADA]:
                consultas_por_status[status] = len([c for c in consultas if c.status == status])

            return {
                'total_pacientes': len(pacientes),
                'total_medicos': len(medicos),
                'total_consultas': len(consultas),
                'consultas_por_status': consultas_por_status,
                'cache_stats': cache_manager.get_stats()
            }

        except Exception as e:
            logging.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}


if __name__ == "__main__":
    # Teste rápido
    from config import config, configurar_logging

    print("\n" + "=" * 60)
    print("🧪 TESTE DO SERVIÇO DE AGENDAMENTO")
    print("=" * 60)

    configurar_logging(config.get_logs_dir())
    storage = JSONStorage(config.get_consultas_dir())
    service = AgendamentoService(storage)

    # Cria paciente
    print("\n1️⃣ Criando paciente...")
    sucesso, msg, paciente = service.criar_paciente(
        "João Teste", "111.111.111-11", "(85) 99999-9999", "joao@teste.com"
    )
    print(f"   {msg}")

    # Cria médico
    print("\n2️⃣ Criando médico...")
    sucesso, msg, medico = service.criar_medico(
        "Dr. Teste", "12345-CE", "Clínico Geral",
        ["08:00", "09:00", "10:00", "11:00"]
    )
    print(f"   {msg}")

    # Agenda consulta
    print("\n3️⃣ Agendando consulta...")
    sucesso, msg, consulta = service.agendar_consulta(
        paciente.id, medico.id, "2025-11-25", "09:00", "Consulta de rotina"
    )
    print(f"   {msg}")

    # Tenta agendar no mesmo horário (deve falhar)
    print("\n4️⃣ Tentando agendar no mesmo horário...")
    sucesso, msg, _ = service.agendar_consulta(
        paciente.id, medico.id, "2025-11-25", "09:00", "Outra consulta"
    )
    print(f"   {msg}")

    # Estatísticas
    print("\n5️⃣ Estatísticas:")
    stats = service.get_estatisticas()
    print(f"   Pacientes: {stats['total_pacientes']}")
    print(f"   Médicos: {stats['total_medicos']}")
    print(f"   Consultas: {stats['total_consultas']}")

    print("\n✅ Serviço testado com sucesso!")