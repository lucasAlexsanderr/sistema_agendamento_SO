"""
Serviço de Geração de Relatórios
🔹 Conceito SO: Operações de I/O, Escrita em Arquivos
"""

import csv
import logging
import os
from datetime import datetime
from typing import List, Dict
from io import StringIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab não disponível. Relatórios PDF desabilitados.")


class RelatorioService:
    """
    Serviço para geração de relatórios
    🔹 Conceito SO: Operações de I/O em arquivos
    """

    def __init__(self, relatorios_dir: str):
        self.relatorios_dir = relatorios_dir

        # 🔹 Conceito SO: Criação de diretório
        os.makedirs(relatorios_dir, exist_ok=True)

        logging.info(f"RelatorioService inicializado: {relatorios_dir}")

    def gerar_csv_consultas(self, consultas: List, pacientes: Dict, medicos: Dict) -> str:
        """
        Gera relatório CSV de consultas
        🔹 Conceito SO: Escrita sequencial em arquivo CSV

        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"consultas_{timestamp}.csv"
            filepath = os.path.join(self.relatorios_dir, filename)

            # 🔹 Conceito SO: Abertura de arquivo para escrita
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Paciente', 'CPF', 'Médico', 'Especialidade',
                              'Data', 'Hora', 'Status', 'Observações']

                # 🔹 Conceito SO: Escrita estruturada em CSV
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for consulta in consultas:
                    paciente = pacientes.get(consulta.paciente_id)
                    medico = medicos.get(consulta.medico_id)

                    writer.writerow({
                        'ID': consulta.id,
                        'Paciente': paciente.nome if paciente else 'Desconhecido',
                        'CPF': paciente.cpf if paciente else '-',
                        'Médico': medico.nome if medico else 'Desconhecido',
                        'Especialidade': medico.especialidade if medico else '-',
                        'Data': consulta.data,
                        'Hora': consulta.hora,
                        'Status': consulta.status,
                        'Observações': consulta.observacoes or '-'
                    })

                # 🔹 Conceito SO: Flush para garantir escrita
                csvfile.flush()
                os.fsync(csvfile.fileno())

            # 🔹 Conceito SO: Obter informações do arquivo
            file_size = os.path.getsize(filepath)

            logging.info(f"Relatório CSV gerado: {filename} ({file_size} bytes)")
            return filepath

        except Exception as e:
            logging.error(f"Erro ao gerar CSV: {str(e)}")
            raise

    def gerar_csv_pacientes(self, pacientes: List) -> str:
        """
        Gera relatório CSV de pacientes
        🔹 Conceito SO: I/O de arquivo
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pacientes_{timestamp}.csv"
            filepath = os.path.join(self.relatorios_dir, filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Nome', 'CPF', 'Telefone', 'Email', 'Data Cadastro']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for paciente in pacientes:
                    writer.writerow({
                        'ID': paciente.id,
                        'Nome': paciente.nome,
                        'CPF': paciente.cpf,
                        'Telefone': paciente.telefone,
                        'Email': paciente.email,
                        'Data Cadastro': paciente.data_cadastro[:10]
                    })

                csvfile.flush()
                os.fsync(csvfile.fileno())

            logging.info(f"Relatório de pacientes gerado: {filename}")
            return filepath

        except Exception as e:
            logging.error(f"Erro ao gerar CSV de pacientes: {str(e)}")
            raise

    def gerar_csv_medicos(self, medicos: List) -> str:
        """
        Gera relatório CSV de médicos
        🔹 Conceito SO: I/O de arquivo
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"medicos_{timestamp}.csv"
            filepath = os.path.join(self.relatorios_dir, filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Nome', 'CRM', 'Especialidade', 'Horários']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for medico in medicos:
                    writer.writerow({
                        'ID': medico.id,
                        'Nome': medico.nome,
                        'CRM': medico.crm,
                        'Especialidade': medico.especialidade,
                        'Horários': ', '.join(medico.horarios_disponiveis)
                    })

                csvfile.flush()
                os.fsync(csvfile.fileno())

            logging.info(f"Relatório de médicos gerado: {filename}")
            return filepath

        except Exception as e:
            logging.error(f"Erro ao gerar CSV de médicos: {str(e)}")
            raise

    def gerar_pdf_consultas(self, consultas: List, pacientes: Dict, medicos: Dict) -> str:
        """
        Gera relatório PDF de consultas
        🔹 Conceito SO: I/O complexo, geração de documento binário

        Returns:
            Caminho do arquivo gerado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab não está instalado. Use: pip install reportlab")

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_consultas_{timestamp}.pdf"
            filepath = os.path.join(self.relatorios_dir, filename)

            # 🔹 Conceito SO: Criação de arquivo PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Título
            title = Paragraph("<b>Relatório de Consultas</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Data de geração
            data_geracao = Paragraph(
                f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                styles['Normal']
            )
            elements.append(data_geracao)
            elements.append(Spacer(1, 12))

            # Tabela de dados
            data = [['ID', 'Paciente', 'Médico', 'Data', 'Hora', 'Status']]

            for consulta in consultas:
                paciente = pacientes.get(consulta.paciente_id)
                medico = medicos.get(consulta.medico_id)

                data.append([
                    consulta.id[:8],
                    paciente.nome if paciente else 'N/A',
                    medico.nome if medico else 'N/A',
                    consulta.data,
                    consulta.hora,
                    consulta.status
                ])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)

            # 🔹 Conceito SO: Build do PDF (escrita em disco)
            doc.build(elements)

            file_size = os.path.getsize(filepath)
            logging.info(f"Relatório PDF gerado: {filename} ({file_size} bytes)")
            return filepath

        except Exception as e:
            logging.error(f"Erro ao gerar PDF: {str(e)}")
            raise

    def listar_relatorios(self) -> List[Dict]:
        """
        Lista todos os relatórios gerados
        🔹 Conceito SO: Listagem de diretório
        """
        try:
            relatorios = []

            # 🔹 Conceito SO: Leitura de diretório
            for filename in os.listdir(self.relatorios_dir):
                if filename.endswith(('.csv', '.pdf')):
                    filepath = os.path.join(self.relatorios_dir, filename)

                    # 🔹 Conceito SO: stat() - metadados do arquivo
                    stat = os.stat(filepath)

                    relatorios.append({
                        'nome': filename,
                        'caminho': filepath,
                        'tamanho_bytes': stat.st_size,
                        'tamanho_kb': round(stat.st_size / 1024, 2),
                        'data_criacao': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'data_modificacao': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

            # Ordena por data de criação (mais recente primeiro)
            relatorios.sort(key=lambda x: x['data_criacao'], reverse=True)

            return relatorios

        except Exception as e:
            logging.error(f"Erro ao listar relatórios: {str(e)}")
            return []

    def remover_relatorio(self, filename: str) -> bool:
        """
        Remove um relatório
        🔹 Conceito SO: Exclusão de arquivo
        """
        try:
            filepath = os.path.join(self.relatorios_dir, filename)

            if os.path.exists(filepath):
                # 🔹 Conceito SO: Remoção de arquivo
                os.remove(filepath)
                logging.info(f"Relatório removido: {filename}")
                return True

            return False

        except Exception as e:
            logging.error(f"Erro ao remover relatório: {str(e)}")
            return False


if __name__ == "__main__":
    # Teste rápido
    import tempfile
    from core.models import Paciente, Medico, Consulta

    print("\n" + "=" * 60)
    print("🧪 TESTE DO SERVIÇO DE RELATÓRIOS")
    print("=" * 60)

    # Cria diretório temporário
    temp_dir = tempfile.mkdtemp()
    service = RelatorioService(temp_dir)

    # Dados de teste
    paciente = Paciente("João Teste", "123", "(85) 99999-9999", "joao@teste.com")
    medico = Medico("Dr. Teste", "12345", "Clínico", ["08:00", "09:00"])
    consulta = Consulta(paciente.id, medico.id, "2025-11-25", "09:00")

    pacientes_dict = {paciente.id: paciente}
    medicos_dict = {medico.id: medico}

    # Testa CSV
    print("\n1️⃣ Gerando CSV...")
    csv_path = service.gerar_csv_consultas([consulta], pacientes_dict, medicos_dict)
    print(f"   ✅ CSV gerado: {csv_path}")

    # Testa PDF (se disponível)
    if REPORTLAB_AVAILABLE:
        print("\n2️⃣ Gerando PDF...")
        pdf_path = service.gerar_pdf_consultas([consulta], pacientes_dict, medicos_dict)
        print(f"   ✅ PDF gerado: {pdf_path}")
    else:
        print("\n2️⃣ PDF não disponível (ReportLab não instalado)")

    # Lista relatórios
    print("\n3️⃣ Listando relatórios...")
    relatorios = service.listar_relatorios()
    print(f"   Total: {len(relatorios)} relatório(s)")
    for rel in relatorios:
        print(f"   - {rel['nome']} ({rel['tamanho_kb']} KB)")

    print(f"\n✅ Relatórios salvos em: {temp_dir}")