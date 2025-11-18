"""
Teste da Fase 2: Models, Storage e Cache
"""

import sys
import os

# Adiciona src ao path
projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(projeto_dir, 'src')
sys.path.insert(0, src_dir)

from config import config, configurar_logging
from core import Paciente, Medico, Consulta, cache_manager
from storage import JSONStorage


def teste_models():
    """Testa criação e serialização dos models"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 1: Models")
    print("=" * 60)

    # Testa Paciente
    print("\n📋 Testando Paciente...")
    paciente = Paciente(
        nome="João Silva",
        cpf="123.456.789-00",
        telefone="(85) 99999-9999",
        email="joao@email.com"
    )
    print(f"   Criado: {paciente}")

    # Testa serialização
    paciente_dict = paciente.to_dict()
    paciente_recuperado = Paciente.from_dict(paciente_dict)
    assert paciente_recuperado.nome == paciente.nome, "Erro na serialização"
    print("   ✅ Serialização OK")

    # Testa Médico
    print("\n👨‍⚕️ Testando Médico...")
    medico = Medico(
        nome="Maria Santos",
        crm="12345-CE",
        especialidade="Cardiologia",
        horarios_disponiveis=["08:00", "09:00", "10:00"]
    )
    print(f"   Criado: {medico}")
    medico.adicionar_horario("11:00")
    assert "11:00" in medico.horarios_disponiveis, "Erro ao adicionar horário"
    print("   ✅ Horários OK")

    # Testa Consulta
    print("\n📅 Testando Consulta...")
    consulta = Consulta(
        paciente_id=paciente.id,
        medico_id=medico.id,
        data="2025-11-20",
        hora="09:00",
        observacoes="Consulta de rotina"
    )
    print(f"   Criada: {consulta}")

    # Testa mudança de status
    assert consulta.status == Consulta.STATUS_AGENDADA, "Status inicial incorreto"
    consulta.atualizar_status(Consulta.STATUS_CONFIRMADA)
    assert consulta.status == Consulta.STATUS_CONFIRMADA, "Erro ao atualizar status"
    print("   ✅ Status OK")

    print("\n✅ TESTE 1 PASSOU!")
    return paciente, medico, consulta


def teste_storage(paciente, medico, consulta):
    """Testa persistência em JSON"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 2: JSON Storage")
    print("=" * 60)

    # Inicializa storage
    storage = JSONStorage(config.get_consultas_dir())

    # Testa salvamento de pacientes
    print("\n💾 Testando salvamento...")
    pacientes = [paciente.to_dict()]
    assert storage.salvar('pacientes', pacientes), "Erro ao salvar pacientes"
    print("   ✅ Pacientes salvos")

    medicos = [medico.to_dict()]
    assert storage.salvar('medicos', medicos), "Erro ao salvar médicos"
    print("   ✅ Médicos salvos")

    consultas = [consulta.to_dict()]
    assert storage.salvar('consultas', consultas), "Erro ao salvar consultas"
    print("   ✅ Consultas salvas")

    # Testa carregamento
    print("\n📂 Testando carregamento...")
    pacientes_carregados = storage.carregar('pacientes')
    assert len(pacientes_carregados) == 1, "Erro ao carregar pacientes"
    print(f"   ✅ {len(pacientes_carregados)} pacientes carregados")

    medicos_carregados = storage.carregar('medicos')
    assert len(medicos_carregados) == 1, "Erro ao carregar médicos"
    print(f"   ✅ {len(medicos_carregados)} médicos carregados")

    consultas_carregadas = storage.carregar('consultas')
    assert len(consultas_carregadas) == 1, "Erro ao carregar consultas"
    print(f"   ✅ {len(consultas_carregadas)} consultas carregadas")

    # Testa operações CRUD
    print("\n✏️  Testando operações CRUD...")

    # CREATE (adicionar)
    novo_paciente = Paciente("Maria Oliveira", "987.654.321-00", "(85) 88888-8888", "maria@email.com")
    assert storage.adicionar('pacientes', novo_paciente.to_dict()), "Erro ao adicionar paciente"
    assert storage.contar('pacientes') == 2, "Contagem incorreta"
    print("   ✅ CREATE OK")

    # READ (buscar)
    paciente_encontrado = storage.buscar_por_id('pacientes', paciente.id)
    assert paciente_encontrado is not None, "Erro ao buscar paciente"
    assert paciente_encontrado['nome'] == paciente.nome, "Dados incorretos"
    print("   ✅ READ OK")

    # UPDATE (atualizar)
    paciente.telefone = "(85) 77777-7777"
    assert storage.atualizar('pacientes', paciente.id, paciente.to_dict()), "Erro ao atualizar"
    paciente_atualizado = storage.buscar_por_id('pacientes', paciente.id)
    assert paciente_atualizado['telefone'] == "(85) 77777-7777", "Atualização não persistiu"
    print("   ✅ UPDATE OK")

    # DELETE (remover)
    assert storage.remover('pacientes', novo_paciente.id), "Erro ao remover"
    assert storage.contar('pacientes') == 1, "Remoção não funcionou"
    print("   ✅ DELETE OK")

    # Testa informações do arquivo
    print("\n📊 Testando info do arquivo...")
    info = storage.get_file_info('pacientes')
    assert info['exists'], "Arquivo não existe"
    print(f"   Tamanho: {info['size_kb']} KB")
    print(f"   Modificado: {info['modified']}")
    print("   ✅ Info OK")

    # Testa backup
    print("\n💾 Testando backup...")
    backup_dir = config.get_backups_dir()
    assert storage.fazer_backup('pacientes', backup_dir), "Erro ao fazer backup"
    backups = storage.listar_backups(backup_dir, 'pacientes')
    assert len(backups) > 0, "Backup não criado"
    print(f"   ✅ {len(backups)} backup(s) criado(s)")

    print("\n✅ TESTE 2 PASSOU!")
    return storage


def teste_cache():
    """Testa sistema de cache"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 3: Cache")
    print("=" * 60)

    # Limpa cache antes do teste
    cache_manager.clear()

    # Testa SET
    print("\n💾 Testando SET...")
    cache_manager.set('paciente:P001', {'nome': 'João', 'cpf': '123'})
    cache_manager.set('medico:M001', {'nome': 'Maria', 'crm': '12345'})
    print("   ✅ 2 itens adicionados")

    # Testa GET (HIT)
    print("\n📂 Testando GET (HIT)...")
    resultado = cache_manager.get('paciente:P001')
    assert resultado is not None, "Cache miss inesperado"
    assert resultado['nome'] == 'João', "Dados incorretos"
    print(f"   ✅ Cache HIT: {resultado}")

    # Testa GET (MISS)
    print("\n❌ Testando GET (MISS)...")
    resultado = cache_manager.get('paciente:P999')
    assert resultado is None, "Deveria ser None"
    print("   ✅ Cache MISS correto")

    # Testa estatísticas
    print("\n📊 Testando estatísticas...")
    stats = cache_manager.get_stats()
    assert stats['hits'] > 0, "Nenhum hit registrado"
    assert stats['misses'] > 0, "Nenhum miss registrado"
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate_percent']}%")
    print("   ✅ Estatísticas OK")

    # Testa DELETE
    print("\n🗑️  Testando DELETE...")
    assert cache_manager.delete('paciente:P001'), "Erro ao deletar"
    resultado = cache_manager.get('paciente:P001')
    assert resultado is None, "Item não foi deletado"
    print("   ✅ DELETE OK")

    # Testa invalidação por padrão
    print("\n🔄 Testando invalidação por padrão...")
    cache_manager.set('consulta:C001', {'data': '2025-11-20'})
    cache_manager.set('consulta:C002', {'data': '2025-11-21'})
    cache_manager.set('medico:M002', {'nome': 'Pedro'})

    removidos = cache_manager.invalidate_pattern('consulta')
    assert removidos == 2, f"Deveria remover 2, removeu {removidos}"
    print(f"   ✅ {removidos} itens invalidados")

    # Testa CLEAR
    print("\n🧹 Testando CLEAR...")
    cache_manager.clear()
    stats = cache_manager.get_stats()
    assert stats['size'] == 0, "Cache não foi limpo"
    print("   ✅ Cache limpo")

    print("\n✅ TESTE 3 PASSOU!")


def teste_integracao(storage, paciente, medico):
    """Testa integração entre módulos"""
    print("\n" + "=" * 60)
    print("🧪 TESTE 4: Integração Storage + Cache")
    print("=" * 60)

    print("\n🔗 Testando fluxo completo...")

    # 1. Salva no storage
    print("   1. Salvando no storage...")
    storage.salvar('pacientes', [paciente.to_dict()])

    # 2. Carrega do storage
    print("   2. Carregando do storage...")
    pacientes = storage.carregar('pacientes')

    # 3. Coloca no cache
    print("   3. Colocando no cache...")
    cache_key = f"paciente:{paciente.id}"
    cache_manager.set(cache_key, pacientes[0])

    # 4. Recupera do cache (rápido)
    print("   4. Recuperando do cache...")
    paciente_cached = cache_manager.get(cache_key)
    assert paciente_cached is not None, "Erro ao recuperar do cache"
    assert paciente_cached['nome'] == paciente.nome, "Dados inconsistentes"

    # 5. Atualiza no storage
    print("   5. Atualizando no storage...")
    paciente.email = "novo_email@email.com"
    storage.atualizar('pacientes', paciente.id, paciente.to_dict())

    # 6. Invalida cache
    print("   6. Invalidando cache...")
    cache_manager.delete(cache_key)

    # 7. Próxima leitura vem do storage
    print("   7. Próxima leitura do storage...")
    pacientes_atualizados = storage.carregar('pacientes')
    assert pacientes_atualizados[0]['email'] == "novo_email@email.com", "Atualização não persistiu"

    print("\n   ✅ Fluxo completo funcionando!")
    print("\n✅ TESTE 4 PASSOU!")


def executar_todos_testes():
    """Executa todos os testes da Fase 2"""
    print("\n" + "🚀" * 30)
    print("INICIANDO TESTES DA FASE 2")
    print("🚀" * 30)

    # Configura logging
    configurar_logging(config.get_logs_dir())

    testes_passaram = []
    paciente = medico = consulta = storage = None

    try:
        paciente, medico, consulta = teste_models()
        testes_passaram.append(True)
    except Exception as e:
        print(f"\n❌ TESTE 1 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        testes_passaram.append(False)

    try:
        storage = teste_storage(paciente, medico, consulta)
        testes_passaram.append(True)
    except Exception as e:
        print(f"\n❌ TESTE 2 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        testes_passaram.append(False)

    try:
        teste_cache()
        testes_passaram.append(True)
    except Exception as e:
        print(f"\n❌ TESTE 3 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        testes_passaram.append(False)

    try:
        teste_integracao(storage, paciente, medico)
        testes_passaram.append(True)
    except Exception as e:
        print(f"\n❌ TESTE 4 FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
        testes_passaram.append(False)

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES DA FASE 2")
    print("=" * 60)

    total = len(testes_passaram)
    passou = sum(testes_passaram)

    print(f"✅ Testes passaram: {passou}/{total}")
    print(f"❌ Testes falharam: {total - passou}/{total}")

    if passou == total:
        print("\n🎉 TODOS OS TESTES DA FASE 2 PASSARAM!")
        print("✅ Pronto para avançar para Fase 3 (Interface Web)!")
        return True
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    sucesso = executar_todos_testes()
    sys.exit(0 if sucesso else 1)