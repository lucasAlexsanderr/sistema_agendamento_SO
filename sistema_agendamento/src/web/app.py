"""
Aplicação Web Flask
🔹 Conceito SO: Servidor web como processo
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import logging
import os

from config import config, configurar_logging
from storage import JSONStorage
from core.agendamento import AgendamentoService
from core.cache import cache_manager

# Inicializa Flask
app = Flask(__name__)
app.secret_key = 'sistema-agendamento-2025'  # Para flash messages

# Configura logging
configurar_logging(config.get_logs_dir())

# Inicializa storage e serviço
storage = JSONStorage(config.get_consultas_dir())
agendamento = AgendamentoService(storage)

logging.info("🌐 Aplicação Flask inicializada")


# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
def index():
    """Página inicial com dashboard"""
    stats = agendamento.get_estatisticas()
    return render_template('index.html', stats=stats)


# ==================== PACIENTES ====================

@app.route('/pacientes')
def pacientes():
    """Lista todos os pacientes"""
    lista_pacientes = agendamento.listar_pacientes()
    return render_template('pacientes.html', pacientes=lista_pacientes)


@app.route('/pacientes/novo', methods=['GET', 'POST'])
def novo_paciente():
    """Cria novo paciente"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')
        email = request.form.get('email')

        sucesso, msg, _ = agendamento.criar_paciente(nome, cpf, telefone, email)

        if sucesso:
            flash(msg, 'success')
            return redirect(url_for('pacientes'))
        else:
            flash(msg, 'error')

    return render_template('paciente_form.html', paciente=None)


@app.route('/pacientes/<paciente_id>/editar', methods=['GET', 'POST'])
def editar_paciente(paciente_id):
    """Edita paciente existente"""
    paciente = agendamento.buscar_paciente(paciente_id)

    if not paciente:
        flash('Paciente não encontrado', 'error')
        return redirect(url_for('pacientes'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')
        email = request.form.get('email')

        sucesso, msg = agendamento.atualizar_paciente(paciente_id, nome, cpf, telefone, email)

        if sucesso:
            flash(msg, 'success')
            return redirect(url_for('pacientes'))
        else:
            flash(msg, 'error')

    return render_template('paciente_form.html', paciente=paciente)


@app.route('/pacientes/<paciente_id>/remover', methods=['POST'])
def remover_paciente(paciente_id):
    """Remove paciente"""
    sucesso, msg = agendamento.remover_paciente(paciente_id)
    flash(msg, 'success' if sucesso else 'error')
    return redirect(url_for('pacientes'))


# ==================== MÉDICOS ====================

@app.route('/medicos')
def medicos():
    """Lista todos os médicos"""
    lista_medicos = agendamento.listar_medicos()
    return render_template('medicos.html', medicos=lista_medicos)


@app.route('/medicos/novo', methods=['GET', 'POST'])
def novo_medico():
    """Cria novo médico"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        crm = request.form.get('crm')
        especialidade = request.form.get('especialidade')
        horarios = request.form.get('horarios', '').split(',')
        horarios = [h.strip() for h in horarios if h.strip()]

        sucesso, msg, _ = agendamento.criar_medico(nome, crm, especialidade, horarios)

        if sucesso:
            flash(msg, 'success')
            return redirect(url_for('medicos'))
        else:
            flash(msg, 'error')

    return render_template('medico_form.html', medico=None)


# ==================== CONSULTAS ====================

@app.route('/consultas')
def consultas():
    """Lista todas as consultas"""
    lista_consultas = agendamento.listar_consultas()
    lista_pacientes = agendamento.listar_pacientes()
    lista_medicos = agendamento.listar_medicos()

    # Cria dicionários para lookup rápido
    pacientes_dict = {p.id: p for p in lista_pacientes}
    medicos_dict = {m.id: m for m in lista_medicos}

    return render_template('consultas.html',
                           consultas=lista_consultas,
                           pacientes=pacientes_dict,
                           medicos=medicos_dict)


@app.route('/consultas/nova', methods=['GET', 'POST'])
def nova_consulta():
    """Agenda nova consulta"""
    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        medico_id = request.form.get('medico_id')
        data = request.form.get('data')
        hora = request.form.get('hora')
        observacoes = request.form.get('observacoes', '')

        sucesso, msg, _ = agendamento.agendar_consulta(
            paciente_id, medico_id, data, hora, observacoes
        )

        if sucesso:
            flash(msg, 'success')
            return redirect(url_for('consultas'))
        else:
            flash(msg, 'error')

    lista_pacientes = agendamento.listar_pacientes()
    lista_medicos = agendamento.listar_medicos()

    return render_template('consulta_form.html',
                           consulta=None,
                           pacientes=lista_pacientes,
                           medicos=lista_medicos)


@app.route('/consultas/<consulta_id>/cancelar', methods=['POST'])
def cancelar_consulta(consulta_id):
    """Cancela consulta"""
    sucesso, msg = agendamento.cancelar_consulta(consulta_id)
    flash(msg, 'success' if sucesso else 'error')
    return redirect(url_for('consultas'))


@app.route('/consultas/<consulta_id>/confirmar', methods=['POST'])
def confirmar_consulta(consulta_id):
    """Confirma consulta"""
    from core.models import Consulta
    sucesso, msg = agendamento.atualizar_status_consulta(consulta_id, Consulta.STATUS_CONFIRMADA)
    flash(msg, 'success' if sucesso else 'error')
    return redirect(url_for('consultas'))


# ==================== API (JSON) ====================

@app.route('/api/stats')
def api_stats():
    """Retorna estatísticas em JSON"""
    stats = agendamento.get_estatisticas()
    return jsonify(stats)


@app.route('/api/cache/stats')
def api_cache_stats():
    """Retorna estatísticas do cache"""
    stats = cache_manager.get_stats()
    return jsonify(stats)


@app.route('/api/cache/clear', methods=['POST'])
def api_cache_clear():
    """Limpa o cache"""
    cache_manager.clear()
    return jsonify({'success': True, 'message': 'Cache limpo'})


# ==================== ERRO 404 ====================

@app.errorhandler(404)
def page_not_found(e):
    """Página não encontrada"""
    return render_template('404.html'), 404


# ==================== FUNÇÕES AUXILIARES ====================

@app.context_processor
def utility_processor():
    """Funções disponíveis nos templates"""
    return {
        'get_paciente_nome': lambda pid: next((p.nome for p in agendamento.listar_pacientes() if p.id == pid),
                                              'Desconhecido'),
        'get_medico_nome': lambda mid: next((m.nome for m in agendamento.listar_medicos() if m.id == mid),
                                            'Desconhecido')
    }


if __name__ == '__main__':
    # Cria diretórios necessários
    config.criar_diretorios()

    # 🔹 Conceito SO: Processo servidor rodando
    logging.info("🚀 Iniciando servidor Flask...")
    logging.info(f"🌐 Acesse: http://localhost:5000")

    # Modo de desenvolvimento
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Evita duplicação de threads
    )

# ==================== RELATÓRIOS ====================

from reports import RelatorioService
from flask import send_file

relatorio_service = RelatorioService(config.get_relatorios_dir())


@app.route('/relatorios')
def relatorios():
    """Lista relatórios gerados"""
    lista_relatorios = relatorio_service.listar_relatorios()
    return render_template('relatorios.html', relatorios=lista_relatorios)


@app.route('/relatorios/gerar/consultas/csv')
def gerar_csv_consultas():
    """Gera relatório CSV de consultas"""
    try:
        consultas = agendamento.listar_consultas()
        pacientes = {p.id: p for p in agendamento.listar_pacientes()}
        medicos = {m.id: m for m in agendamento.listar_medicos()}

        filepath = relatorio_service.gerar_csv_consultas(consultas, pacientes, medicos)
        flash('Relatório CSV gerado com sucesso!', 'success')
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('relatorios'))


@app.route('/relatorios/gerar/pacientes/csv')
def gerar_csv_pacientes():
    """Gera relatório CSV de pacientes"""
    try:
        pacientes = agendamento.listar_pacientes()
        filepath = relatorio_service.gerar_csv_pacientes(pacientes)
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('relatorios'))


@app.route('/relatorios/gerar/medicos/csv')
def gerar_csv_medicos():
    """Gera relatório CSV de médicos"""
    try:
        medicos = agendamento.listar_medicos()
        filepath = relatorio_service.gerar_csv_medicos(medicos)
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('relatorios'))