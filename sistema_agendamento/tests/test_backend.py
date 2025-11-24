"""
Teste do Backend: Agendamento + Threads
"""

import sys
import os
import threading
import time

# Adiciona src ao path
projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(projeto_dir, 'src')
sys.path.insert(0, src_dir)

from config import config, configurar_logging
from storage import JSONStorage
from core.agendamento import AgendamentoService
from concorrencia import thread_manager


def teste_agendamento_concorrente():
    """
    Testa agendamento simultâneo (deve detectar conflito)
    🔹 Conceito SO: Race condition + Lock
    """
    print("\n" + "=" * 60)
    print("🧪 TESTE: Agendamento Concorrente")
    print("=" * 60)

    storage = JSONStorage(config.get_consultas_dir())
    service = AgendamentoService(storage)

    # Gera CPFs únicos usando timestamp
    import uuid
    cpf1 = f"test_{uuid.uuid4().hex[:8]}"
    cpf2 = f"test_{uuid.uuid4().hex[:8]}"
    crm = f"CRM_{uuid.uuid4().hex[:6]}"

    # Cria pacientes
    print("\n📋 Criando pacientes...")
    sucesso1, msg1, paciente1 = service.criar_paciente("João 1", cpf1, "(85) 1", "j1@test.com")
    if not sucesso1:
        print(f"   ⚠️  Paciente 1: {msg1}")
        return False

    sucesso2, msg2, paciente2 = service.criar_paciente("João 2", cpf2, "(85) 2", "j2@test.com")
    if not sucesso2:
        print(f"   ⚠️  Paciente 2: {msg2}")
        return False

    # Cria médico
    print("👨‍⚕️ Criando médico...")
    sucesso3, msg3, medico = service.criar_medico("Dr. Teste Concorrente", crm, "Clínico", ["14:00"])
    if not sucesso3:
        print(f"   ⚠️  Médico: {msg3}")
        return False

    print(f"\n🎯 Paciente 1: {paciente1.id}")
    print(f"🎯 Paciente 2: {paciente2.id}")
    print(f"🎯 Médico: {medico.id}")
    print(f"🎯 Horário alvo: 2025-11-25 14:00")

    # Resultados das threads
    resultados = []

    def agendar(paciente_id, numero):
        """Tenta agendar consulta"""
        print(f"\n🔵 Thread {numero}: Iniciando agendamento...")
        sucesso, msg, consulta = service.agendar_consulta(
            paciente_id, medico.id, "2025-11-25", "14:00", f"Paciente {numero}"
        )
        resultados.append((numero, sucesso, msg))

        if sucesso:
            print(f"✅ Thread {numero}: {msg}")
        else:
            print(f"❌ Thread {numero}: {msg}")

    # 🔹 Cria threads que tentarão agendar simultaneamente
    print("\n🚀 Iniciando threads simultâneas...")
    thread1 = threading.Thread(target=agendar, args=(paciente1.id, 1))
    thread2 = threading.Thread(target=agendar, args=(paciente2.id, 2))

    # Inicia ao mesmo tempo
    thread1.start()
    thread2.start()

    # Aguarda conclusão
    thread1.join()
    thread2.join()

    # Análise dos resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADO:")
    print("=" * 60)

    sucessos = [r for r in resultados if r[1]]
    falhas = [r for r in resultados if not r[1]]

    print(f"✅ Agendamentos bem-sucedidos: {len(sucessos)}")
    print(f"❌ Agendamentos bloqueados: {len(falhas)}")

    if len(sucessos) == 1 and len(falhas) == 1:
        print("\n🎉 TESTE PASSOU!")
        print("✅ Lock funcionou: Apenas 1 agendamento foi aceito")
        print("✅ Conflito detectado: O segundo foi bloqueado")
        return True
    else:
        print("\n⚠️  TESTE FALHOU!")
        print("❌ Lock não funcionou corretamente")
        return False


def teste_thread_manager():
    """Testa o gerenciador de threads"""
    print("\n" + "=" * 60)
    print("🧪 TESTE: Thread Manager")
    print("=" * 60)

    def tarefa_teste(n):
        time.sleep(0.1)
        return n * 2

    print(f"\n⚙️  Workers disponíveis: {thread_manager.max_workers}")
    print("🚀 Submetendo 10 tarefas...")

    futures = []
    for i in range(10):
        future = thread_manager.submit_task(tarefa_teste, i)
        futures.append(future)

    # Aguarda resultados
    resultados = [f.result() for f in futures]

    print(f"✅ Resultados: {resultados}")

    stats = thread_manager.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"   Tarefas submetidas: {stats['tasks_submitted']}")
    print(f"   Tarefas completadas: {stats['tasks_completed']}")
    print(f"   Tarefas falhadas: {stats['tasks_failed']}")

    if stats['tasks_completed'] == 10:
        print("\n🎉 TESTE PASSOU!")
        return True
    else:
        print("\n⚠️  TESTE FALHOU!")
        return False


def executar_todos_testes():
    """Executa todos os testes do backend"""
    print("\n" + "🚀" * 30)
    print("INICIANDO TESTES DO BACKEND")
    print("🚀" * 30)

    # Configura logging
    configurar_logging(config.get_logs_dir())

    resultados = []

    try:
        resultados.append(teste_thread_manager())
    except Exception as e:
        print(f"\n❌ Teste Thread Manager falhou: {e}")
        import traceback
        traceback.print_exc()
        resultados.append(False)

    try:
        resultados.append(teste_agendamento_concorrente())
    except Exception as e:
        print(f"\n❌ Teste Agendamento Concorrente falhou: {e}")
        import traceback
        traceback.print_exc()
        resultados.append(False)

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)

    total = len(resultados)
    passou = sum(resultados)

    print(f"✅ Testes passaram: {passou}/{total}")
    print(f"❌ Testes falharam: {total - passou}/{total}")

    if passou == total:
        print("\n🎉 BACKEND COMPLETO E FUNCIONANDO!")
        print("✅ Pronto para criar a interface web!")
        return True
    else:
        print("\n⚠️  Alguns testes falharam.")
        return False


if __name__ == "__main__":
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)