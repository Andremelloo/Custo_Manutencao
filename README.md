# 📊 Dashboard de Gestão Estratégica de Custos de Manutenção :: TCP
> **Terminal de Contêineres de Paranaguá (TCP)**  
> Gestão Orçamentária, Inteligência Semanal de Frotas e Análise Comparativa (2025 vs 2026 &bull; Posição Week 44).

---

## 🌐 Publicação no GitHub Pages

Este dashboard foi desenvolvido para rodar **100% no navegador** (client-side), sem necessidade de servidores backend ou bancos de dados adicionais.

🔗 **Link de Acesso Web:**  
👉 **[https://andremelloo.github.io/Custo_Manutencao/](https://andremelloo.github.io/Custo_Manutencao/)**

---

## 🔒 Senha de Acesso ao Painel

Para proteger as informações gerenciais e dados confidenciais de orçamento, o painel conta com autenticação por tela de segurança:

- **Senha de Acesso:** `tcp@2026`

---

## 🚀 Como Ativar o GitHub Pages (Passo a Passo)

1. Acesse o seu repositório no GitHub: **[https://github.com/Andremelloo/Custo_Manutencao](https://github.com/Andremelloo/Custo_Manutencao)**.
2. Clique na aba **Settings** (Configurações) no menu superior do repositório.
3. No menu lateral esquerdo, clique em **Pages**.
4. Na seção **Build and deployment**:
   - **Source**: selecione `Deploy from a branch`.
   - **Branch**: selecione `main` e a pasta `/ (root)`.
   - Clique em **Save**.
5. Em 1 a 2 minutos, o GitHub disponibilizará o link público em `https://andremelloo.github.io/Custo_Manutencao/` para você e seu parceiro navegarem de qualquer lugar (computador, tablet ou smartphone).

---

## 📑 Principais Módulos do Dashboard

1. **📊 Visão Geral Executiva**:
   - Curva S acumulada (Forecast vs Realizado até a Semana 44).
   - Diagnóstico do desvio de **-R$ 9,76 M (-31,7%)**.
   - Balanço consolidado de todas as contas e famílias orçamentárias.

2. **🚜 Análise Semanal por Frota (W01 a W44)**:
   - **Resumo Geral das Frotas**: Quadro comparativo de todas as 6 famílias operacionais (**TT, RTG, STS, RS, EH e MHC**).
   - **Evolução Semanal**: Gráficos de queima semanal com divisão visual de Pré-Inflexão (W01-W21) vs Pós-Inflexão (W22-W44).
   - **Decomposição por Componente**: Subdivisão por sistemas mecânicos e elétricos de cada frota.
   - **Ranking de Máquinas com Top 3 Peças**: Detalhamento por equipamento individual mostrando quantidade (Qtd), descrição da peça e valor financeiro no Pré-WK22 e Pós-WK22.

3. **🚨 Diagnóstico da Inflexão (WK 22)**:
   - Investigação técnica e contábil do motivo pelo qual a curva empinou a partir da Semana 22.
   - Comparação da taxa de queima semanal (+84,4% de aceleração pós-Semana 22).
   - Principais vilões: descarte de ativos (Asset Disposal), ciclo concentrado de pneus Michelin e tandem de carretas, freios de gantry e esteiras Brevetti de RTGs, cabos Bridon de portêineres STS.

4. **⚖️ Comparativo 2025 vs 2026**:
   - Comparação item a item dos materiais e serviços.
   - Diagnóstico de inflação unitária de preços nos mesmos itens.
   - Identificação de itens novos em 2026 e itens descontinuados em relação a 2025.

5. **📋 Resumo Todas as Frotas (Deep-Dive Cards)**:
   - Cards executivos detalhados para cada conta e família da manutenção.

6. **🔍 Base Transacional & Exportação**:
   - Mais de 25.000 lançamentos contábeis auditáveis com filtros por frota, semana, conta e busca em tempo real.
   - Botão para exportação completa dos dados filtrados para Excel (`.xlsx`).

---

## 📁 Estrutura dos Arquivos

```
Custo_Manutencao/
├── index.html                   # Estrutura principal do Dashboard com tela de login
├── styles.css                   # Estilização moderna, responsiva e identidade visual TCP
├── app.js                       # Lógica de negócio, autenticação, filtros e renderizadores
├── dashboard_data.js            # Base de dados analítica pré-processada (Curva S, frotas, transações)
├── chart.umd.min.js             # Biblioteca Chart.js offline
├── xlsx.full.min.js             # Biblioteca SheetJS offline para exportação Excel
├── generate_dashboard_data.py   # Script gerador da base analítica
├── abrir_dashboard.bat          # Inicializador local em 1 clique
├── .nojekyll                    # Configuração para publicação sem restrições no GitHub Pages
└── README.md                    # Documentação do projeto
```

---

*Terminal de Contêineres de Paranaguá &bull; Gestão Estratégica da Manutenção*

