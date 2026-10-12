# 🖥️ Conexão Jovem — Módulo Administrativo Desktop

Painel administrativo desktop desenvolvido em Python com interface estilizada via QSS, projetado para gerenciamento dinâmico de gincanas, controle de pontuação de equipes e transmissão de dados em tempo real para o aplicativo mobile dos participantes.

---

### 🌐 O Ecossistema Conexão Jovem
Este software atua como a **Central de Controle** do evento:
1. **Desktop (Este repositório):** Operado pela equipe organizadora para cadastrar equipes, lançar pontos, controlar rodadas e gerenciar o placar geral.
2. **Mobile (App dos participantes):** Recebe as atualizações instantaneamente em tempo real na palma da mão de cada líder e membro.

---

### 💡 Problema & Solução
* **Problema:** Gincanas e eventos com múltiplas equipes sofrem com contagem manual de pontos em papéis ou quadros brancos, gerando atrasos, contestações de pontuação e falta de visibilidade imediata para os participantes.
* **Solução:** Uma suíte integrada onde a pontuação é inserida no computador da mesa organizadora e sincronizada instantaneamente na nuvem, mantendo o placar atualizado em tempo real para todos no celular.

---

### 🚀 Funcionalidades Principais
* **Painel de Lançamento Ágil:** Interface desenvolvida para operação rápida durante dinâmicas e provas ao vivo.
* **Estilização Visual Avançada:** UI personalizada com folha de estilos dedicada (`style.qss`), entregando um tema visual moderno, escuro e coeso com a identidade visual do evento.
* **Sincronização em Tempo Real:** Comunicação direta com banco de dados em nuvem para atualização imediata do módulo mobile.
* **Gestão de Equipes e Rodadas:** Controle categorizado de atividades, penalidades, bônus e histórico de alterações.
* **Executável Standalone:** Empacotamento com PyInstaller (`pg_conexao_pro.spec`) para distribuição e execução simplificada em ambientes Windows sem necessidade de instalar interpretador Python.

---

### 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python
* **Interface Gráfica:** PyQt / PySide com estilização via Qt Style Sheets (`QSS`)
* **Arquitetura:** Desktop-to-Mobile Real-time Sync
* **Compilação:** PyInstaller (.spec)

---


### 📱 Ecossistema Integrado (Módulo Mobile)
Este painel desktop atua como a central de controle e sincroniza dados em tempo real com o aplicativo mobile utilizado pelos participantes do evento.

* 📲 **Repositório do App Mobile:** [pgconexaomobile](https://github.com/Lihvinii7/pgconexaomobile)

> 💡 **Solução sob medida e adaptável:** Toda a estrutura (regras de pontuação, provas, categorias e visual) pode ser customizada para qualquer formato de evento, conferência, gincana ou controle interno de equipes.

---

### 👨‍💻 Autor & Contato
Desenvolvido por **Lisandro Vinicios**  
* WhatsApp para projetos e soluções sob medida: [Entrar em contato](https://wa.me/5581991781052?text=Ol%C3%A1!%20Vi%20o%20ecossistema%20Conex%C3%A3o%20Jovem%20no%20GitHub%20e%20gostaria%20de%20conversar.)
