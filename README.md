# 📈 MarketPro

> **Monitoramento de Patrimônio e Estimativa de Renda Passiva**

O **MarketPro** é uma aplicação web moderna projetada para investidores que desejam acompanhar a performance de seus ativos na bolsa de valores (B3 e mercados internacionais), com foco especial em ativos geradores de renda, como FIIs (Fundos de Investimentos Imobiliários) e Ações pagadoras de dividendos.

A plataforma apresenta um design **Glassmorphism** premium, pensado para oferecer a melhor experiência do usuário (UX) com base no uso de *Toasts* assíncronos e interfaces limpas.

---

## 🚀 Funcionalidades Atuais

- **Busca Global de Tickers:** Encontre ações e FIIs em tempo real puxando os dados do Yahoo Finance (ex: `ITUB4.SA`, `MXRF11.SA`, `AAPL`).
- **Dashboard de Renda Passiva:** A carteira divide os ativos automaticamente entre "Geradores de Dividendos" e "Formatos de Crescimento", listando o patrimônio total e as projeções precisas de renda passiva (Mensal, Trimestral, Semestral e Anual) baseadas no histórico acumulado real de pagamentos.
- **Indicadores Fundamentalistas:** A página de detalhes do ativo calcula e exibe de forma harmoniosa indicadores vitais da empresa: `P/L`, `P/VP`, `LPA`, `VPA`, `Valor de Mercado` e `Mín/Máx (52s)`.
- **Feedback Interativo (Toasts):** Ações como favoritar ou adicionar ativos à carteira disparam notificações em tela de forma sutil e não-bloqueante.
- **Lógica Inteligente de Cotas:** O sistema soma as cotas adicionadas e permite subtração orgânica, removendo o ativo do banco de dados quando atinge saldo `0`.

---

## 🛠️ Stack Tecnológico e Bibliotecas

A filosofia fundamental deste projeto é prover máxima funcionalidade com o **mínimo de dependências externas** para garantir leveza e portabilidade:

**Backend:**
* **`Python 3.12`** - Linguagem central.
* **`Django 6.0`** - Framework Web robusto encarregado das requisições, Views, Templates e autenticação, permitindo escalabilidade MVC.
* **`yfinance (Yahoo Finance)`** - Biblioteca crítica do projeto, encarregada de buscar em tempo real os relatórios de dividendos, balanços, oscilações diárias e metadados das empresas sem necessidade de chaves de API restritas.
* **`pandas`** - Utilizado nos bastidores para agregação financeira precisa do histórico vetorial da *yfinance* (ex: soma de dividendos dos últimos 12 meses agrupados).
* **`SQLite3`** - Banco de dados embutido utilizado para armazenar Usuários, Cotas na Carteira e Favoritos.

**Frontend:**
* **`HTML5 + Vanilla JS`** - Sem dependência pesada de frameworks frontend. Scripts limpos gerenciando chamadas `fetch()` na API do Django e modificando o DOM.
* **`CSS3 (Glassmorphism UI)`** - Design system feito do zero focando em UI Moderna (borrados, translucidez, dark mode). 
* **`Chart.js`** - Biblioteca utilizada especificamente na tela de detalhes da ação para renderizar com alta perfomance o **histórico de oscilação temporal do preço**, incluindo linhas cruzadas (crosshair) customizadas, gradientes responsivos baseados em alta (verde) ou queda (vermelha) do ativo, e tooltips interativos usando *hover*.

---

## ⚙️ Como Funciona

1. **Pesquisa Básica:** Ao digitar "PETR4.SA" na barra, o Django captura o parâmetro via GET, invoca o módulo `services.py`, e realiza o webscraping limpo usando os métodos do `yfinance.Ticker()`.
2. **Cálculo de Proventos:** FIIs como o "MXRF11" ocasionalmente possuem falhas no provedor. Para corrigir isso, nosso motor ignora o dividendo sugerido pelo provedor e captura fisicamente a **série histórica** de pagamentos de 12 meses filtrada por fuso-horário UTC, fazendo a matemática do DY exato.
3. **Persistência Assíncrona:** Toda adição à carteira ou favorito envia dados via `Fetch API (JavaScript)` formatados em JSON usando tokens CSRF. A View do Django lê a carga, manipula via ORM (Object-Relational Mapping), atualiza as Decimais sem travar o tráfego do usuário e retorna uma promessa informando sucesso ao Toast, que então recarrega o modelo atualizado sob os panos.

---

## 🔮 Roadmap de Implementações Futuras

Esse projeto foi criado para constante evolução. O plano arquitetural possui 5 grandes implementações a curto e médio prazo:

1. **📊 Gráficos de Diversificação da Carteira:** Implementação de visualizações com o Chart.js diretamente no Dashboard mostrando o percentual do portfólio distribuído em "Setores" (Bancos, Energia, Papel) ou "Tipos de Ativos" (FIIs vs Ações).
2. **💰 Tracking de Transações e Preço Médio (PM):** Evolução da modelagem do Banco de Dados para registrar a data, cotas, e **Preço da Compra** de cada ação. Isso permitirá calcular a "Rentabilidade Total" do investidor baseada no deslocamento entre o Valor Pago e o Valor Atual de Mercado.
3. **📅 Calendário de Dividendos Dinâmico:** Utilização avançada do *yfinance* para criar uma aba exclusiva avisando ao usuário as próximas `Datas-Com` e as `Datas de Pagamento` dos ativos presentes unicamente na carteira dele.
4. **📰 Feed de Notícias Integrado:** Aproveitamento do vetor "notícias" do fundo extraído para injetar hiperlinks na tela de cada ação, permitindo ao usuário decidir aportes baseado nos relatórios atualizados do Globo/InfoMoney/G1 no mercado interno.
5. **🔍 Filtragem e Ordenação em Tabela:** Para carteiras robustas, criação da possibilidade de organizar dinamicamente a `portfolio.html` pelo maior Dividend Yield, ou Maior Aporte do dia, de forma instantânea através do JavaScript puro, elevando o sistema a nível institucional de Home Broker.

---

> Desenvolvido de forma autônoma como prova de conceito para construção estética Glassmorfista aliada a complexidade de rotinas financeiras.
