import sys
import random
import sqlite3
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from supabase import create_client, Client

# Use as credenciais que você já tem no código
SUPABASE_URL = "https://nbruivedpqeqycgkaegi.supabase.co"
SUPABASE_KEY = "sb_publishable_RiM6NG2oO2PqxYfCM33MWg_IxTXMOG3"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    supabase = None

# ---------------- ESTILO CSS MODERNO DA FOTO 2 ----------------
ESTILO_CSS = """
    QMainWindow { background-color: #020617; }
    
    QFrame#Card {
        background-color: rgba(15, 23, 42, 0.85);
        border: 1px solid #1e293b;
        border-radius: 15px;
    }

    QLabel { color: white; background: transparent; font-family: 'Segoe UI'; }
    QLabel#TituloPrincipal { font-size: 45px; font-weight: bold; text-shadow: 2px 2px #000; }
    QLabel#Missao { color: #38bdf8; font-size: 15px; letter-spacing: 2px; font-weight: bold; }

    QLabel#TituloSecao { color: #f8fafc; font-size: 18px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
    QLabel#TituloSorteio { color: #f8fafc; font-size: 22px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }

    QTableWidget { background: transparent; color: white; border: none; gridline-color: #1e293b; }
    QHeaderView::section { background: #1e293b; color: #38bdf8; padding: 10px; border: none; font-weight: bold; }

    /* Cores dos Botões da Foto 2 */
    QPushButton#BtnNovo { background: #16a34a; color: white; border-radius: 8px; font-weight: bold; height: 35px; }
    QPushButton#BtnSalvar { background: #2563eb; color: white; border-radius: 8px; font-weight: bold; height: 35px; }
    QPushButton#BtnGerenciar { background: #f59e0b; color: white; border-radius: 8px; font-weight: bold; height: 35px; }
    QPushButton#BtnLimpar { background: #a855f7; color: white; border-radius: 8px; font-weight: bold; height: 35px; }
    
    QPushButton#BtnSorteio { background: #3b82f6; color: white; border-radius: 10px; font-weight: bold; font-size: 14px; height: 40px; }
    QPushButton#BtnSorteioTrio { background: #a855f7; color: white; border-radius: 10px; font-weight: bold; font-size: 14px; height: 40px; }

    QListWidget { background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 10px; color: #e2e8f0; font-size: 16px; padding: 10px; outline: 0; }
    QListWidget::item { padding: 8px 5px; border-bottom: 1px solid #334155; }
"""

# ---------------- JANELA DE GERENCIAR MEMBROS (BLINDADA) ----------------
class JanelaMembros(QDialog):
    def __init__(self, callback_atualizar, parent=None):
        super().__init__(parent)
        self.callback_atualizar = callback_atualizar
        self.setWindowTitle("Gerenciar Membros")
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #0f172a; color: white;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Novo Membro:"))
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Digite o nome...")
        self.input_nome.setStyleSheet("padding: 10px; background: #1e293b; border: 1px solid #3b82f6; color: white;")
        layout.addWidget(self.input_nome)

        btn_add = QPushButton("ADICIONAR")
        btn_add.clicked.connect(self.adicionar)
        btn_add.setStyleSheet("background: #16a34a; font-weight: bold; padding: 10px; color: white; border-radius: 5px;")
        layout.addWidget(btn_add)

        layout.addWidget(QLabel("Cadastrados:"))
        self.lista_view = QListWidget()
        self.lista_view.setStyleSheet("background: #1e293b; color: white; border: none; border-radius: 5px;")
        layout.addWidget(self.lista_view)

        btn_del = QPushButton("REMOVER")
        btn_del.clicked.connect(self.remover)
        btn_del.setStyleSheet("background: #ef4444; font-weight: bold; padding: 10px; color: white; border-radius: 5px;")
        layout.addWidget(btn_del)

        self.carregar_lista()

    def carregar_lista(self):
        self.lista_view.clear()
        try:
            conn = sqlite3.connect("pg_conexao.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM membros ORDER BY nome ASC")
            for row in cursor.fetchall():
                self.lista_view.addItem(row[0])
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar lista: {e}")

    def adicionar(self):
        nome = self.input_nome.text().strip().title()
        if nome:
            try:
                conn = sqlite3.connect("pg_conexao.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO membros (nome) VALUES (?)", (nome,))
                cursor.execute("INSERT OR IGNORE INTO ranking (nome, pontos) VALUES (?, 0)", (nome,))
                conn.commit()
                conn.close()
                self.input_nome.clear()
                self.carregar_lista()
                self.callback_atualizar()
            except:
                QMessageBox.warning(self, "Erro", "Este membro já está cadastrado!")

    def remover(self):
        item = self.lista_view.currentItem()
        if not item: return
        nome = item.text()

        # Criamos um menu de opções para não poluir a tela principal
        msg = QMessageBox()
        msg.setWindowTitle("Opções do Membro")
        msg.setText(f"O que deseja fazer com {nome}?")
        btn_retirar = msg.addButton("Retirar Pontos", QMessageBox.ActionRole)
        btn_excluir = msg.addButton("Excluir Membro", QMessageBox.DestructiveRole)
        msg.addButton("Cancelar", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == btn_retirar:
            pontos, ok = QInputDialog.getInt(self, "Ajuste", f"Quantos pontos retirar de {nome}?", 5, 1, 1000, 1)
            if ok:
                conn = sqlite3.connect("pg_conexao.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE ranking SET pontos = MAX(0, pontos - ?) WHERE nome = ?", (pontos, nome))
                conn.commit(); conn.close()
                QMessageBox.information(self, "Sucesso", "Pontos retirados localmente!")
                self.callback_atualizar()

        elif msg.clickedButton() == btn_excluir:
            if QMessageBox.question(self, "Confirmar", f"Excluir {nome} permanentemente?") == QMessageBox.Yes:
                if supabase: supabase.table("membros").delete().eq("nome", nome).execute()
                conn = sqlite3.connect("pg_conexao.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM membros WHERE nome = ?",(nome,))
                cursor.execute("DELETE FROM ranking WHERE nome = ?",(nome,))
                conn.commit(); conn.close()
                self.carregar_lista()
                self.callback_atualizar()
                

                

# ---------------- OVERLAY DE SORTEIO (CORRIGIDO PARA TEXTOS LONGOS) ----------------
class OverlaySorteio(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Overlay")
        self.setStyleSheet("""
            QFrame#Overlay { background-color: rgba(2, 6, 23, 0.98); border: 2px solid #3b82f6; border-radius: 20px; }
            QLabel { color: white; font-family: 'Segoe UI'; }
            QPushButton#Fechar { background: #ef4444; color: white; border-radius: 5px; font-weight: bold; padding: 10px; }
            
            /* Novo estilo para a caixa de texto longa */
            QTextBrowser { background: transparent; color: white; border: none; font-size: 18px; }
            QScrollBar:vertical { border: none; background: #1e293b; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #3b82f6; border-radius: 4px; }
        """)
        self.setVisible(False)
        layout = QVBoxLayout(self)
        
        titulo = QLabel("🎯 RESULTADO DO SORTEIO")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b82f6;")
        layout.addWidget(titulo, alignment=Qt.AlignCenter)

        # Usando QTextBrowser no lugar do QLabel para criar rolagem infinita sem cortar
        self.caixa_texto = QTextBrowser()
        layout.addWidget(self.caixa_texto)

        btn_fechar = QPushButton("FECHAR"); btn_fechar.setObjectName("Fechar")
        btn_fechar.setFixedSize(120, 40); btn_fechar.clicked.connect(self.hide)
        layout.addWidget(btn_fechar, alignment=Qt.AlignCenter)

    def mostrar(self, texto):
        # O HTML garante que o texto fique centralizado dentro da caixa de rolagem
        self.caixa_texto.setHtml(f"<div style='text-align: center; font-family: Segoe UI;'>{texto}</div>")
        self.setFixedSize(600, 500)
        if self.parent(): self.move(self.parent().rect().center() - self.rect().center())
        self.show(); self.raise_()
        
# ---------------- APP PRINCIPAL ----------------
class PGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- LÓGICA DE CAMINHO PARA O .EXE ---
        if getattr(sys, 'frozen', False): 
            self.base_path = sys._MEIPASS
        else: 
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        # --- TRUQUE PARA O ÍCONE NA BARRA DE TAREFAS DO WINDOWS ---
        try:
            myappid = 'pgconexao.pro.v1' # Identificador único pro Windows não agrupar errado
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass # Se não for Windows, ele ignora e segue a vida

        self.setWindowTitle("PG Conexão Jovem - Pro")
        self.setStyleSheet(ESTILO_CSS)

        # --- CARREGANDO O ÍCONE DA JANELA ---
        icon_path = os.path.join(self.base_path, "logo pg.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # --- CRIAÇÃO SEGURA DO BANCO DE DADOS ---
        self.db_path = "pg_conexao.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ranking (nome TEXT PRIMARY KEY, pontos INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS membros (nome TEXT PRIMARY KEY)")
        conn.commit()
        conn.close()

        self.setup_ui()
        self.atualizar_tabela_membros()
        self.atualizar_rank()
        self.showMaximized()

    def setup_ui(self):
        self.central = QWidget(); self.setCentralWidget(self.central)
        main_layout = QVBoxLayout(self.central)
        
        # --- HEADER (IGUAL A FOTO 2) ---
        header = QHBoxLayout()
        
        # Logo Esquerda
        self.lbl_logo = QLabel()
        logo_p = os.path.join(self.base_path, "logo pg.png")
        if os.path.exists(logo_p):
            self.lbl_logo.setPixmap(QPixmap(logo_p).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(self.lbl_logo)

        # Títulos Centro
        vbox_tit = QVBoxLayout(); vbox_tit.setAlignment(Qt.AlignCenter)
        t = QLabel("PG CONEXÃO JOVEM"); t.setObjectName("TituloPrincipal")
        m = QLabel("BUSCAR, RESGATAR, AMAR E ACOLHER. ESSA É A NOSSA MISSÃO."); m.setObjectName("Missao")
        vbox_tit.addWidget(t); vbox_tit.addWidget(m); header.addLayout(vbox_tit)

        # Logo Direita (Cruz)
        self.lbl_cruz = QLabel()
        cruz_p = os.path.join(self.base_path, "cruz.png")
        if os.path.exists(cruz_p):
            self.lbl_cruz.setPixmap(QPixmap(cruz_p).scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(self.lbl_cruz)

        # Botões Empilhados na Direita (COMO NA FOTO 2)
        btns_top = QVBoxLayout()
        self.btn_novo = QPushButton("📅 NOVO DIA"); self.btn_novo.setObjectName("BtnNovo")
        self.btn_salv = QPushButton("💾 SALVAR"); self.btn_salv.setObjectName("BtnSalvar")
        self.btn_geren = QPushButton("👥 MEMBROS"); self.btn_geren.setObjectName("BtnGerenciar")
        
        # --- ADICIONE ESTAS DUAS LINHAS AQUI ---
        self.btn_sync = QPushButton("🔄 SINCRONIZAR"); self.btn_sync.setObjectName("BtnSync")
        # ---------------------------------------
        
        self.btn_limp = QPushButton("🧹 LIMPAR TUDO"); self.btn_limp.setObjectName("BtnLimpar")
        
        self.btn_pull = QPushButton("📥 ATUALIZAR PC")
        self.btn_pull.setObjectName("BtnSync") 
        btns_top.addWidget(self.btn_pull)
        self.btn_pull.clicked.connect(self.baixar_da_nuvem)
        
        btns_top.addWidget(self.btn_novo)
        btns_top.addWidget(self.btn_salv)
        btns_top.addWidget(self.btn_geren)
        
        # --- ADICIONE ESTE ADDWIDGET AQUI PARA ELE APARECER NA TELA ---
        btns_top.addWidget(self.btn_sync) 
        # --------------------------------------------------------------
        
        btns_top.addWidget(self.btn_limp)
        header.addLayout(btns_top)
        main_layout.addLayout(header)

        # --- CORPO ---
        corpo = QHBoxLayout()
        
        # Lado Esquerdo (Tabela)
        self.card_p = QFrame(); self.card_p.setObjectName("Card")
        lay_p = QVBoxLayout(self.card_p)
        self.tabela = QTableWidget(50, 8)
        self.tabela.verticalHeader().setVisible(False)
        lay_p.addWidget(self.tabela)
        
        self.lab_pres = QLabel("👥 PRESENTES: 0"); self.lab_tot = QLabel("⭐ TOTAL PONTOS: 0")
        stats = QHBoxLayout(); stats.addWidget(self.lab_pres); stats.addStretch(); stats.addWidget(self.lab_tot)
        lay_p.addLayout(stats)

        # Lado Direito (Ranking e Sorteio)
        col_dir = QVBoxLayout()
        self.card_r = QFrame(); self.card_r.setObjectName("Card")
        lay_r = QVBoxLayout(self.card_r); self.lista_rank = QListWidget()
        l_rank = QLabel("📊 RANKING"); l_rank.setObjectName("TituloSecao")
        lay_r.addWidget(l_rank); lay_r.addWidget(self.lista_rank)
        
        self.card_s = QFrame(); self.card_s.setObjectName("Card")
        lay_s = QVBoxLayout(self.card_s)
        lbl_s = QLabel("🎁 SORTEIO DE ORAÇÃO"); lbl_s.setObjectName("TituloSorteio"); lbl_s.setAlignment(Qt.AlignCenter)
        self.btn_dup = QPushButton("👥 DUPLAS"); self.btn_dup.setObjectName("BtnSorteio")
        self.btn_tri = QPushButton("👨‍👩‍👧‍👦 TRIOS"); self.btn_tri.setObjectName("BtnSorteioTrio")
        lay_s.addWidget(lbl_s); lay_s.addWidget(self.btn_dup); lay_s.addWidget(self.btn_tri)

        col_dir.addWidget(self.card_r, 3); col_dir.addWidget(self.card_s, 2)
        corpo.addWidget(self.card_p, 7); corpo.addLayout(col_dir, 3)
        main_layout.addLayout(corpo)

        self.overlay = OverlaySorteio(self.central)
        
        # --- CONEXÕES ---
        self.btn_novo.clicked.connect(self.novo)
        self.btn_salv.clicked.connect(self.salvar)
        self.btn_limp.clicked.connect(self.limpar_banco)
        self.btn_geren.clicked.connect(self.abrir_gerenciador)
        self.btn_dup.clicked.connect(lambda: self.sortear(2))
        self.btn_tri.clicked.connect(lambda: self.sortear(3))
        self.btn_sync.clicked.connect(self.sincronizar_nuvem)
        

    def abrir_gerenciador(self):
        try:
            self.janela_membros = JanelaMembros(self.atualizar_tabela_membros, self)
            self.janela_membros.exec()
        except Exception as e:
            print(f"Erro ao abrir janela: {e}")

    def atualizar_tabela_membros(self):
        self.tabela.setRowCount(0)
        
        # Busca no banco de dados com segurança
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM membros ORDER BY nome ASC")
            membros = cursor.fetchall()
            conn.close()
        except:
            membros = []
        
        rows = max(50, len(membros))
        self.tabela.setRowCount(rows)
        
        # As cores originais da Foto 2
        cores = { 2: "#f97316", 3: "#22c55e", 4: "#3b82f6", 5: "#eab308", 6: "#a855f7" }

        titulos = ["#", "NOME", "VISITANTE\n+20", "VOLTOU\n+10", "PRESENÇA\n+5", "PONTUAL\n+3", "DINÂMICA\n+2", "PONTOS\nTOTAL"]
        self.tabela.setHorizontalHeaderLabels(titulos)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setFixedHeight(50)
        
        for r in range(rows):
            self.tabela.setItem(r, 0, QTableWidgetItem(str(r+1)))
            nome = membros[r][0] if r < len(membros) else ""
            self.tabela.setItem(r, 1, QTableWidgetItem(nome))
            
            item_tot = QTableWidgetItem("0")
            item_tot.setForeground(QColor("#22c55e"))
            item_tot.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(r, 7, item_tot)

            # Checkboxes com as cores bonitas
            for c in range(2, 7):
                w = QWidget(); l = QHBoxLayout(w); cb = QCheckBox()
                cor = cores[c]
                cb.setStyleSheet(f"""
                    QCheckBox::indicator {{ border: 2px solid {cor}; border-radius: 4px; width: 18px; height: 18px; }}
                    QCheckBox::indicator:checked {{ background-color: {cor}; }}
                """)
                cb.stateChanged.connect(lambda _, row=r: self.calc(row))
                l.addWidget(cb); l.setAlignment(Qt.AlignCenter); l.setContentsMargins(0,0,0,0)
                self.tabela.setCellWidget(r, c, w)
        self.calc_presenca()

    def calc(self, row):
        pts = [20, 10, 5, 3, 2]; tot = 0
        for i, col in enumerate(range(2, 7)):
            w = self.tabela.cellWidget(row, col)
            if w and w.findChild(QCheckBox).isChecked(): tot += pts[i]
        
        item = self.tabela.item(row, 7)
        if item: item.setText(str(tot))
        self.calc_presenca()

    def calc_presenca(self):
        pres = 0; pts_totais = 0
        for r in range(self.tabela.rowCount()):
            item_nome = self.tabela.item(r, 1)
            item_tot = self.tabela.item(r, 7)
            if item_nome and item_nome.text().strip():
                # Se qualquer checkbox estiver marcado, conta presença
                presente = any(self.tabela.cellWidget(r, c).findChild(QCheckBox).isChecked() for c in range(2, 7) if self.tabela.cellWidget(r, c))
                if presente: pres += 1
                if item_tot: pts_totais += int(item_tot.text() or 0)
        self.lab_pres.setText(f"👥 PRESENTES: {pres}")
        self.lab_tot.setText(f"⭐ TOTAL PONTOS: {pts_totais}")

    def atualizar_rank(self):
        self.lista_rank.clear()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # MÁGICA AQUI: O 'WHERE pontos > 0' faz sumir quem não tem pontos!
            cursor.execute("SELECT nome, pontos FROM ranking WHERE pontos > 0 ORDER BY pontos DESC LIMIT 30")
            dados = cursor.fetchall()
            conn.close()
            
            for i, (n, p) in enumerate(dados, 1):
                item = QListWidgetItem()
                if i == 1: prefixo, cor, peso = "🥇 OURO:", "#FFD700", QFont.Bold
                elif i == 2: prefixo, cor, peso = "🥈 PRATA:", "#C0C0C0", QFont.Bold
                elif i == 3: prefixo, cor, peso = "🥉 BRONZE:", "#CD7F32", QFont.Bold
                else:
                    prefixo, cor, peso = f"{i}º {random.choice(['🏃‍♂️', '🔥', '💪', '🚀', '✨', '🎯'])}", "white", QFont.Normal

                item.setText(f"{prefixo} {n.upper()} - {p} pts")
                item.setForeground(QColor(cor))
                font = QFont("Segoe UI", 11); font.setWeight(peso); item.setFont(font)
                self.lista_rank.addItem(item)
        except Exception as e: print(f"Erro Ranking: {e}")

    def limpar_banco(self):
        if QMessageBox.question(self, "Zerar Ranking", "Isso vai zerar os pontos de todo mundo. Deseja continuar?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE ranking SET pontos = 0")
            conn.commit()
            conn.close()
            
            self.atualizar_rank() # Limpa os nomes do ranking na hora
            self.novo()           # Limpa as caixinhas marcadas da tabela
            QMessageBox.information(self, "Zerar", "Ranking zerado para um novo ciclo!")

    def salvar(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for r in range(self.tabela.rowCount()):
                item_nome = self.tabela.item(r, 1)
                item_total = self.tabela.item(r, 7)
                if item_nome and item_total:
                    nome = item_nome.text()
                    pontos = int(item_total.text() or 0)
                    if nome and pontos > 0:
                        cursor.execute("UPDATE ranking SET pontos = pontos + ? WHERE nome = ?", (pontos, nome))
            conn.commit()
            conn.close()
            self.atualizar_rank()
            QMessageBox.information(self, "Sucesso", "Pontos Salvos com sucesso!")
        except Exception as e:
            print(f"Erro salvar: {e}")

    def novo(self):
        # 1. Limpa as caixinhas da tabela (Checkboxes)
        for r in range(self.tabela.rowCount()):
            item = self.tabela.item(r, 7)
            if item: item.setText("0")
            for c in range(2, 7):
                w = self.tabela.cellWidget(r, c)
                if w:
                    cb = w.findChild(QCheckBox)
                    if cb: cb.setChecked(False)
        
        # 2. LIMPA O SORTEIO DE VERDADE (O que você precisa)
        if hasattr(self, 'overlay'):
            self.overlay.caixa_texto.setHtml("") # Apaga o texto do sorteio antigo
            self.overlay.hide()                  # Esconde a janela
        
        # 3. Zera os contadores visuais
        self.lab_pres.setText("👥 PRESENTES: 0")
        self.lab_tot.setText("⭐ TOTAL PONTOS: 0")

    def limpar_banco(self):
        if QMessageBox.question(self, "Zerar Ranking", "Isso vai zerar os pontos de todo mundo. Deseja continuar?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE ranking SET pontos = 0")
            conn.commit()
            conn.close()
            self.atualizar_rank()
            QMessageBox.information(self, "Zerar", "Ranking zerado!")

    def sortear(self, tam):
        # 1. FORÇAR A LIMPEZA: Garantimos que a lista comece vazia toda vez
        nomes_para_sorteio = []
        
        # 2. LER A TABELA: Pegar apenas quem está marcado como presente agora
        for r in range(self.tabela.rowCount()):
            item_nome = self.tabela.item(r, 1)
            if item_nome and item_nome.text().strip():
                # Verifica se há presença marcada (colunas 2 a 6)
                tem_presenca = False
                for c in range(2, 7):
                    w = self.tabela.cellWidget(r, c)
                    if w and w.findChild(QCheckBox).isChecked():
                        tem_presenca = True
                        break
                
                if tem_presenca:
                    nomes_para_sorteio.append(item_nome.text().strip())

        # 3. VALIDAÇÃO: Se não marcou ninguém, avisa e para
        if not nomes_para_sorteio:
            QMessageBox.warning(self, "Aviso", "Ninguém foi marcado como presente na tabela!")
            return

        # 4. RANDOM REAL: Resetar o gerador de números aleatórios
        random.seed()
        random.shuffle(nomes_para_sorteio)
        
        # 5. GERAR GRUPOS: Lógica inteligente para evitar pessoas sozinhas
        grupos = []
        copia_nomes = list(nomes_para_sorteio)
        
        while len(copia_nomes) > 0:
            # Se sobrar exatamente 3 e o tamanho for 2, cria um trio e encerra
            if len(copia_nomes) == 3 and tam == 2:
                grupos.append(copia_nomes[:]) # Pega os 3 que restam
                copia_nomes.clear()
            # Se sobrar apenas 1 e já tivermos grupos, junta esse 1 ao último grupo (vira trio)
            elif len(copia_nomes) == 1 and len(grupos) > 0:
                grupos[-1].append(copia_nomes.pop())
            # Caso contrário, segue o fluxo normal (pega o tamanho definido)
            else:
                fatia = []
                for _ in range(tam):
                    if copia_nomes:
                        fatia.append(copia_nomes.pop(0))
                if fatia:
                    grupos.append(fatia)

        # 6. LIMPAR O OVERLAY (Mantém igual)
        if hasattr(self, 'overlay'):
            self.overlay.caixa_texto.clear()
            self.overlay.caixa_texto.setHtml("")
        
        # 7. MONTAR O NOVO RESULTADO (Agora com nomes dinâmicos: Par ou Trio)
        txt = ""
        for i, g in enumerate(grupos):
            # Define o título baseado na quantidade de pessoas no grupo
            if len(g) == 3:
                titulo = "TRIO"
            elif len(g) == 2:
                titulo = "PAR"
            else:
                titulo = f"GRUPO {i+1}"
                
            txt += f"<b>{titulo}:</b> {' & '.join(g)}<br><br>"
        
        # 8. MOSTRAR: Exibir o resultado fresquinho
        self.overlay.mostrar(txt)

    def sincronizar_nuvem(self):
        if not supabase:
            QMessageBox.warning(self, "Erro", "Sem conexão com a nuvem.")
            return

        res = QMessageBox.question(self, "Sincronizar", "Deseja enviar os pontos para a nuvem preservando as fotos?")
        if res == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT nome, pontos FROM ranking")
                dados_locais = cursor.fetchall()
                conn.close()

                if dados_locais:
                    # O upsert atualiza pontos e ignora o campo da foto se ele já existir
                    lista_para_enviar = [{"nome": n, "pontos": p} for n, p in dados_locais]
                    supabase.table("membros").upsert(lista_para_enviar, on_conflict="nome").execute()

                QMessageBox.information(self, "Sucesso", "Nuvem atualizada! Fotos preservadas.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")
    
    def baixar_da_nuvem(self):
        if not supabase:
            QMessageBox.critical(self, "Erro", "Supabase não configurado!")
            return

        try:
            # 1. Busca os dados frescos da nuvem
            response = supabase.table("membros").select("nome, pontos").execute()
            dados_nuvem = response.data

            if dados_nuvem:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # --- O PULO DO GATO ---
                # Limpa as tabelas locais antes de inserir o que veio da nuvem
                # Isso garante que quem foi deletado no celular suma daqui também
                cursor.execute("DELETE FROM membros")
                cursor.execute("DELETE FROM ranking")

                for m in dados_nuvem:
                    nome = m['nome']
                    pts = m.get('pontos', 0)
                    cursor.execute("INSERT INTO membros (nome) VALUES (?)", (nome,))
                    cursor.execute("INSERT INTO ranking (nome, pontos) VALUES (?, ?)", (nome, pts))
                
                conn.commit()
                conn.close()

                # 2. Atualiza a tela para mostrar a lista limpa
                self.atualizar_tabela_membros()
                self.atualizar_rank()
                
                QMessageBox.information(self, "Sucesso", "Dados sincronizados! Membros removidos foram atualizados.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao baixar dados: {e}")           
                

# === FIM DA CLASSE PGApp ===

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PGApp()
    window.show()
    sys.exit(app.exec())