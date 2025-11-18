"""
Modelos de Dados do Sistema
🔹 Conceito SO: Estruturas de dados em memória
"""

from datetime import datetime
from typing import List, Optional
import uuid


class Paciente:
    """
    Modelo de dados para Paciente
    🔹 Conceito SO: Alocação de objetos em memória
    """

    def __init__(self, nome: str, cpf: str, telefone: str, email: str, id: str = None):
        self.id = id or f"P{str(uuid.uuid4())[:8]}"
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email
        self.data_cadastro = datetime.now().isoformat()

    def to_dict(self):
        """Serializa para dicionário (para salvar em JSON)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'email': self.email,
            'data_cadastro': self.data_cadastro
        }

    @staticmethod
    def from_dict(data: dict):
        """Deserializa de dicionário (carregar de JSON)"""
        paciente = Paciente(
            nome=data['nome'],
            cpf=data['cpf'],
            telefone=data['telefone'],
            email=data['email'],
            id=data.get('id')
        )
        paciente.data_cadastro = data.get('data_cadastro', datetime.now().isoformat())
        return paciente

    def __repr__(self):
        return f"<Paciente {self.id}: {self.nome}>"

    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"


class Medico:
    """
    Modelo de dados para Médico
    🔹 Conceito SO: Estruturas complexas em memória
    """

    def __init__(self, nome: str, crm: str, especialidade: str,
                 horarios_disponiveis: List[str] = None, id: str = None):
        self.id = id or f"M{str(uuid.uuid4())[:8]}"
        self.nome = nome
        self.crm = crm
        self.especialidade = especialidade
        self.horarios_disponiveis = horarios_disponiveis or []
        self.data_cadastro = datetime.now().isoformat()

    def to_dict(self):
        """Serializa para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'crm': self.crm,
            'especialidade': self.especialidade,
            'horarios_disponiveis': self.horarios_disponiveis,
            'data_cadastro': self.data_cadastro
        }

    @staticmethod
    def from_dict(data: dict):
        """Deserializa de dicionário"""
        medico = Medico(
            nome=data['nome'],
            crm=data['crm'],
            especialidade=data['especialidade'],
            horarios_disponiveis=data.get('horarios_disponiveis', []),
            id=data.get('id')
        )
        medico.data_cadastro = data.get('data_cadastro', datetime.now().isoformat())
        return medico

    def adicionar_horario(self, horario: str):
        """Adiciona horário disponível"""
        if horario not in self.horarios_disponiveis:
            self.horarios_disponiveis.append(horario)
            return True
        return False

    def remover_horario(self, horario: str):
        """Remove horário disponível"""
        if horario in self.horarios_disponiveis:
            self.horarios_disponiveis.remove(horario)
            return True
        return False

    def __repr__(self):
        return f"<Medico {self.id}: Dr(a). {self.nome} - {self.especialidade}>"

    def __str__(self):
        return f"Dr(a). {self.nome} - {self.especialidade} (CRM: {self.crm})"


class Consulta:
    """
    Modelo de dados para Consulta
    🔹 Conceito SO: Gerenciamento de estado em memória
    """

    # Estados possíveis da consulta
    STATUS_AGENDADA = 'agendada'
    STATUS_CONFIRMADA = 'confirmada'
    STATUS_REALIZADA = 'realizada'
    STATUS_CANCELADA = 'cancelada'

    def __init__(self, paciente_id: str, medico_id: str, data: str,
                 hora: str, observacoes: str = "", id: str = None):
        self.id = id or f"C{str(uuid.uuid4())[:8]}"
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.data = data  # Formato: YYYY-MM-DD
        self.hora = hora  # Formato: HH:MM
        self.observacoes = observacoes
        self.status = self.STATUS_AGENDADA
        self.data_criacao = datetime.now().isoformat()
        self.data_atualizacao = datetime.now().isoformat()

    def to_dict(self):
        """Serializa para dicionário"""
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'medico_id': self.medico_id,
            'data': self.data,
            'hora': self.hora,
            'observacoes': self.observacoes,
            'status': self.status,
            'data_criacao': self.data_criacao,
            'data_atualizacao': self.data_atualizacao
        }

    @staticmethod
    def from_dict(data: dict):
        """Deserializa de dicionário"""
        consulta = Consulta(
            paciente_id=data['paciente_id'],
            medico_id=data['medico_id'],
            data=data['data'],
            hora=data['hora'],
            observacoes=data.get('observacoes', ''),
            id=data.get('id')
        )
        consulta.status = data.get('status', Consulta.STATUS_AGENDADA)
        consulta.data_criacao = data.get('data_criacao', datetime.now().isoformat())
        consulta.data_atualizacao = data.get('data_atualizacao', datetime.now().isoformat())
        return consulta

    def atualizar_status(self, novo_status: str) -> bool:
        """
        Atualiza status da consulta
        🔹 Conceito SO: Modificação de estado com timestamp
        """
        if novo_status in [self.STATUS_AGENDADA, self.STATUS_CONFIRMADA,
                           self.STATUS_REALIZADA, self.STATUS_CANCELADA]:
            self.status = novo_status
            self.data_atualizacao = datetime.now().isoformat()
            return True
        return False

    def get_datetime_str(self) -> str:
        """Retorna data e hora formatados"""
        return f"{self.data} às {self.hora}"

    def __repr__(self):
        return f"<Consulta {self.id}: {self.data} {self.hora} - Status: {self.status}>"

    def __str__(self):
        return f"Consulta {self.id} em {self.get_datetime_str()} ({self.status})"


if __name__ == "__main__":
    # Testes rápidos dos models
    print("\n" + "=" * 60)
    print("🧪 TESTE DOS MODELS")
    print("=" * 60)

    # Teste Paciente
    print("\n1️⃣ Testando Paciente:")
    paciente = Paciente(
        nome="João Silva",
        cpf="123.456.789-00",
        telefone="(85) 99999-9999",
        email="joao@email.com"
    )
    print(f"   Criado: {paciente}")
    print(f"   Dict: {paciente.to_dict()}")

    # Teste Médico
    print("\n2️⃣ Testando Médico:")
    medico = Medico(
        nome="Maria Santos",
        crm="12345-CE",
        especialidade="Cardiologia",
        horarios_disponiveis=["08:00", "09:00", "10:00"]
    )
    print(f"   Criado: {medico}")
    medico.adicionar_horario("11:00")
    print(f"   Horários: {medico.horarios_disponiveis}")

    # Teste Consulta
    print("\n3️⃣ Testando Consulta:")
    consulta = Consulta(
        paciente_id=paciente.id,
        medico_id=medico.id,
        data="2025-11-20",
        hora="09:00",
        observacoes="Consulta de rotina"
    )
    print(f"   Criada: {consulta}")
    print(f"   Status inicial: {consulta.status}")
    consulta.atualizar_status(Consulta.STATUS_CONFIRMADA)
    print(f"   Status atualizado: {consulta.status}")

    print("\n✅ Todos os models funcionando!")