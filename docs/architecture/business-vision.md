# Documento de Modelagem de Negócio e Visão do Produto: Wedding Management System

Plataforma SaaS B2B de Gestão e Governança Operacional de Casamentos
**Marco de Definição da Necessidade (DefNec) e Consenso de Escopo (ConEsc)**

---

## 1. Declaração do Problema (Domínio do Problema)

### Contexto Atual

O mercado de casamentos no Brasil é caracterizado por alta sofisticação, demandas personalizadas e elevado valor financeiro agregado. A realização de um evento de casamento envolve, em média, de 20 a 45 contratos com fornecedores especializados (espaço de eventos, buffet, decoração, fotografia, som, iluminação, trajes, cerimonial e logística de itens).

Nesse ecossistema, os **cerimonialistas e assessores de eventos** atuam como o elo central de orquestração entre os noivos e os prestadores de serviço. Historicamente, a operação da assessoria cerimonial depende de instrumentos informais e fragmentados: planilhas eletrônicas desconexas, troca massiva de mensagens instantâneas (WhatsApp), anotações físicas de checklist e guarda descentralizada de minutas e recibos em pastas locais ou e-mails pessoais.

### A Dor do Negócio

A ausência de uma plataforma centralizada e de alta fidelidade contábil provoca gargalos críticos na rotina das assessorias:

1. **Descontrole Orçamentário e Ruptura de Confiança:** Divergências de centavos acumuladas ao longo de dezenas de parcelas entre o contrato formal do fornecedor e o controle interno da assessoria geram desgaste na prestação de contas aos noivos e risco financeiro.
2. **Disputas Contratuais por Aditivos Informais:** Alterações de escopo (horas extras de buffet, acréscimo de arranjos florais, extensão do baile) frequentemente são combinadas verbalmente ou por mensagem, sem a formalização de Termos Aditivos amarrados ao contrato principal, resultando em litígios na prestação de contas final.
3. **Falhas Logísticas no Dia do Evento:** A gestão de itens físicos (bebidas consignadas, mobiliário, lembrancinhas, doces finos) sem um checklist de status de entrega (`PENDING` $\to$ `IN_PROGRESS` $\to$ `DONE`) provoca atrasos na montagem e estresse severo para os noivos e equipes de campo.
4. **Sobrecarga Operacional e Retrabalho do Assessor:** O tempo que o profissional deveria dedicar ao planejamento estratégico e à experiência humana dos noivos é consumido na digitação repetitiva de datas, montagem manual de cronogramas em planilhas e cobrança manual de prazos de fornecedores.
5. **Vulnerabilidade e Vazamento de Dados Pessoais (LGPD):** Dados sensíveis de contratos, valores de despesas pessoais, documentos de identidade e listas de convidados circulam desprotegidos em aplicativos de mensagens, expondo a assessoria e os clientes a riscos jurídicos.

### A Oportunidade

Estabelecer uma **Plataforma SaaS B2B Multi-tenant especializada em casamentos**, que unifique a gestão de ponta a ponta: orçamentos com Tolerância Zero contábil, custódia digital de contratos no Cloudflare R2, máquina de estados de aditivos, checklist de entregáveis logísticos e cronograma inteligente com detecção preditiva de conflitos e relatórios executivos em tempo real.

---

## 2. Objetivo de Negócio e Metas Mensuráveis de Sucesso (Critérios SMART)

### Objetivo Primário

Centralizar, automatizar e conferir integridade operacional, financeira e logística à gestão de casamentos para assessorias e cerimonialistas profissionais, mitigando erros contábeis, eliminando retrabalho e elevando o padrão de atendimento ao cliente final.

### Metas Mensuráveis de Sucesso (KPIs Operacionais):

1. **Integridade Financeira (Tolerância Zero):** Garantir **100% de paridade centesimal** na divisão de parcelas e conciliação de contratos em relação ao valor nominal de despesas (\(\sum \text{parcelas} \equiv \text{valor total}\)), erradicando furos cumulativos de arredondamento.
2. **Agilidade em Alinhamentos e Prestação de Contas:** Reduzir em pelo menos **40% o tempo consumido pela assessoria** na preparação de dados e confecção de relatórios financeiros e de cronograma para reuniões executivas com os noivos.
3. **Conformidade Documental Auditada:** Assegurar que **100% dos contratos assinados e termos aditivos** possuam custódia digital em nuvem com links seguros efêmeros e validação algorítmica obrigatória de CNPJ (Módulo 11) dos fornecedores.
4. **Eficiência Logística de Campo:** Atingir **zero ocorrências de itens críticos esquecidos ou não entregues** na data da cerimônia por meio do checklist sincronizado de suprimentos.
5. **Timebox e Confiabilidade de Engenharia:** Disponibilização da **Release 1.0 (MVP Web)** em ambiente de nuvem serverless de baixo custo (Cloud Run + Neon PostgreSQL), com 100% dos testes de isolamento multi-tenant e integridade aprovados.

---

## 3. Partes Interessadas (Stakeholders) e Perfis de Usuários

| Perfil                                        | Papel no Ecossistema                                      | Interação de Negócio com a Plataforma                                                                                                                                                        |
| :-------------------------------------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cerimonialista Titular / Gestor (`ADMIN`)** | Proprietário da empresa de assessoria cerimonial (Tenant) | Gerencia a conta corporativa da empresa, cadastra os casamentos contratados, aprova orçamentos gerais, monitora a saúde financeira consolidada e exporta relatórios executivos em PDF/Excel. |
| **Assessor Operacional (`STAFF`)**            | Membro da equipe da assessoria responsável pela execução  | Alimenta o checklist logístico de itens, atualiza o status de entrega no dia do evento, acompanha tarefas do cronograma e registra comprovantes de pagamento.                                |
| **Noivos / Casal (Consumidores)**             | Clientes contratantes da assessoria                       | Destinatários dos relatórios executivos de prestação de contas (PDF e planilhas formatadas), usufruindo da tranquilidade de um evento gerido com governança e transparência.                 |
| **Fornecedores Credenciados**                 | Prestadores de serviço (buffet, espaço, som, etc.)        | Cadastro auditado (CNPJ verificado), parceiros em contratos formais e termos aditivos, com histórico reutilizável entre casamentos da mesma assessoria.                                      |
| **Administrador da Plataforma SaaS**          | Mantenedor da infraestrutura e do produto                 | Monitora a disponibilidade global do serviço, orquestra rotinas diárias de background (crons de auditoria de parcelas) e garante a conformidade com as diretrizes de segurança.              |

---

## 4. Benefícios e Impacto Esperado

- **Visão Descomplicada dos Dados:** Interface visual coesa e amigável que consolida em dashboards instantâneos os principais eixos do casamento: saúde do orçamento, prazos de pagamento, pendências de contratos e contagem regressiva para o evento.
- **Flexibilidade e Previsibilidade de Caixa:** Gestão inteligente de parcelamento permitindo ajustes individuais, renegociação global de cronogramas de desembolso e controle automático de vencimentos (`PENDING`, `PAID`, `OVERDUE`).
- **Segurança Jurídica e Transparência:** Eliminação de perdas documentais mediante a digitalização de contratos assinados e encadeamento rigoroso de termos aditivos com recálculo automático de saldos devidos.
- **Isolamento e Governança Multi-Tenant:** Proteção total dos segredos de negócio e precificação de cada assessoria, assegurando que uma empresa não tenha visibilidade sobre casamentos, orçamentos ou contratos de concorrentes.
- **Conformidade com a LGPD:** Armazenamento seguro de dados pessoais e transacionais, eliminando planilhas desprotegidas e preservando o sigilo dos clientes.

---

## 5. Premissas e Restrições de Negócio

### 5.1. Premissas do Negócio

- A assessoria cerimonial e seus membros operam a plataforma a partir de navegadores modernos em desktops, tablets ou smartphones conectados à internet.
- Os fornecedores parceiros possuem registro formal (CNPJ ou identificação civil idônea) para homologação no catálogo da assessoria.
- A contratação do casamento pela assessoria estabelece um teto financeiro estimado e uma data futura definida para a celebração da cerimônia.

### 5.2. Restrições de Negócio, Fiscais e Regulatórias

- **Restrição de Isolamento Lógico (Multi-Tenancy Mandatório):** O sistema deve operar como um SaaS compartilhado, porém cada assessoria (`Company`) possui uma fronteira lógica de dados intransponível no banco de dados.
- **Restrição Contábil de Tolerância Zero:** Nenhuma discrepância matemática de centavos é tolerada no parcelamento. Em caso de dízimas periódicas na divisão de cotas, a diferença centesimal é compulsoriamente absorvida pela última parcela.
- **Restrição Temporal do Ciclo de Vida:** Um casamento não pode ser encerrado (`CONCLUIDO`) em data prévia à celebração oficial, resguardando a integridade das auditorias.
- **Restrição Orçamentária de Infraestrutura (OpEx Mínimo):** O sistema deve ser hospedado com arquitetura serverless em nuvem elástica (Google Cloud Run + Neon DB Serverless + Cloudflare R2), garantindo custo operacional praticamente nulo quando ocioso e escalabilidade instantânea sob demanda.

---

## 6. Escopo em Alto Nível e Fronteiras da Solução

```mermaid
flowchart TD
    subgraph IN_SCOPE["No Escopo da Solução (Release 1.0 - MVP Web)"]
        direction TB
        E1["Gestão Multi-Tenant & Onboarding de Assessorias"]
        E2["Gestão Centralizada de Clientes (SSOT) & Papéis"]
        E3["Ciclo de Vida do Casamento & Templates de Cronograma"]
        E4["Orçamento, Categorias & Parcelas com Tolerância Zero"]
        E5["Custódia Digital de Contratos (PDF no R2) & Aditivos 1:N"]
        E6["Catálogo Corporativo de Fornecedores com Validação CNPJ (Módulo 11)"]
        E7["Checklist Multidimensional de Suprimentos (SupplyItem)"]
        E8["Agenda, Conflitos (Soft Overlap) e Checklist Operacional"]
        E9["Dashboard Executivo em 4 Eixos e Relatórios PDF/Excel"]
        E10["Alertas In-App e Rotinas Diárias de Auditoria (Cron)"]
    end

    subgraph OUT_SCOPE["Não-Escopo / Requisitos Inversos (Fronteiras Deliberadas)"]
        direction TB
        NE1["Intermediação Financeira Direta (Gateway de Pagamentos)"]
        NE2["Assinatura Digital com Certificado ICP-Brasil Integrado"]
        NE3["Notificações Externas via WhatsApp ou SMS no MVP"]
        NE4["Portal Público / Área de Acesso Exclusiva dos Noivos"]
        NE5["Marketplace Aberto de Fornecedores B2C"]
        NE6["Despacho Físico ou Frota Própria de Transporte"]
    end
```

### 6.1. No Escopo da Solução

- **Módulo de Identidade e Multi-tenancy (`apps.tenants` & `apps.users`):** Onboarding de empresas de assessoria, autenticação JWT stateless e integração com Google OAuth2.
- **Módulo de Clientes e Participantes (`apps.clients` & `WeddingClient`):** Única Fonte da Verdade (SSOT) cadastral para pessoas físicas (nome, CPF, e-mail, telefone) e vinculação estruturada ao casamento com papéis específicos (`RoleChoices`: Noiva, Noivo, Pagador Financeiro, etc.) e identificação do signatário principal.
- **Módulo de Casamentos (`apps.weddings`):** Ciclo de vida estendido em 4 estados canônicos (`PROPOSTA` $\to$ `PLANEJAMENTO` $\to$ `EM_ANDAMENTO` $\to$ `CONCLUIDO`), vinculação de contrato de assessoria via modelo unificado (`Contract` do tipo `PLANNER`), simulação orçamentária prévia e conversão com templates de cronograma.
- **Módulo Financeiro (`apps.finances`):** Definição de teto orçamentário mestre (`Budget` com linha de base congelada a partir do planejamento), centros de custo categorizados dinamicamente, ancoragem contratual e parcelamento com centavos ajustados na última parcela (Tolerância Zero).
- **Módulo de Fornecedores (`apps.suppliers`):** Catálogo corporativo compartilhado com validação algorítmica de CNPJ (Módulo 11) e histórico de contratações reutilizável entre casamentos.
- **Módulo de Contratações (`apps.contracts`):** Instrumentos jurídicos com fornecedores terceiros e contrato de assessoria, upload de minutas em PDF diretamente para Cloudflare R2 via presigned URLs e gestão de termos aditivos via entidade filha dedicada (`ContractAddendum` 1:N).
- **Módulo de Gestão de Suprimentos (`apps.logistics`):** Mapeamento multidimensional de materiais (`SupplyItem`), contemplando escopo (com justificativa obrigatória em caso de descarte), cotação/compra e conferência física de entrega no dia do evento.
- **Módulo de Agenda, Cronograma e Checklist (`apps.scheduler`):** Planejamento de compromissos com detecção inteligente de conflitos de horário (_soft overlap_), checklist operacional de pendências (`ChecklistItem`) e sincronização read-only com parcelas a vencer.
- **Módulo de Relatórios e Inteligência (`apps.dashboard` & `apps.reporting`):** Dashboards consolidados em 4 eixos analíticos sem N+1 (*Anti-Data-Stitching*) e exportação binária em PDF profissional diagramado em 2 passos (ReportLab) e planilhas Excel (.xlsx) para prestação de contas sob demanda em qualquer fase.

### 6.2. Não-Escopo (Requisitos Inversos)

- **Intermediação Financeira:** A plataforma atua como sistema de controle, planejamento e conciliação contábil, não atuando como instituição financeira, emissor de boletos bancários ou intermediador de Pix no MVP.
- **Autoridade Certificadora de Assinatura Digital:** O sistema gerencia o upload de documentos assinados e a máquina de estados jurídica, mas não oferece integração nativa com certificadoras ICP-Brasil (e.g., Clicksign, DocuSign) no MVP.
- **Disparo Externo de WhatsApp / SMS:** As notificações da Release 1.0 operam na central de notificações in-app e por e-mail transacional, evitando custos de mensageria externa no estágio inicial.
- **Portal de Autoatendimento do Noivo:** Os noivos recebem relatórios consolidados em PDF e planilhas fornecidos pelo assessor; a área de login exclusiva do cliente final faz parte da evolução futura.
- **Marketplace Aberto:** A plataforma não é um catálogo de compras público B2C; cada assessoria mantém seu catálogo privado e homologado de fornecedores parceiros.

---

## 7. Estratégia de Evolução e Faseamento

### Release 1.0 (MVP Web Responsivo — Versão Atual em Produção)

Foco completo na entrega de valor para a **assessoria cerimonial**:

- Arquitetura multi-tenant B2B completa com isolamento de dados no PostgreSQL;
- Gestão centralizada de clientes (SSOT em `apps.clients`) e vinculação estruturada de participantes (`WeddingClient`);
- Ciclo de vida completo desde captação (`PROPOSTA`) e contrato da assessoria (`Contract` tipo `PLANNER` via interface pública);
- Controle orçamentário rígido com linha de base congelada e Tolerância Zero contábil;
- Catálogo corporativo de fornecedores com validação Módulo 11 de CNPJ (`apps.suppliers`);
- Custódia de contratos em nuvem (Cloudflare R2) com gestão de termos aditivos (`ContractAddendum` 1:N);
- Checklist multidimensional de suprimentos logísticos (`SupplyItem`) com motivo de recusa;
- Cronograma com motor de conflitos suaves (_soft overlap_) e checklist operacional (`ChecklistItem`);
- Dashboards analíticos em tempo real e exportação de relatórios em PDF e Excel;
- Rotinas de auditoria diária em nuvem via Cloud Scheduler e tarefas assíncronas coordenadas (`django.tasks`).

### Release 2.0 (Pós-MVP)

Expansão do ecossistema e agregação de novos canais:

- **Portal do Noivo (Área do Cliente):** Acesso restrito para o casal acompanhar o progresso dos preparativos, consultar despesas pagas e visualizar o cronograma do grande dia.
- **Portal do Fornecedor:** Canal para prestadores de serviço visualizarem prazos de entrega e anexarem notas fiscais e comprovantes de entrega de itens.
- **Assinatura Digital Integrada:** Coleta eletrônica de assinaturas diretamente pela plataforma com validade jurídica reconhecida.
- **Notificações Operacionais via WhatsApp:** Disparo de lembretes automáticos de vencimento e alertas de reuniões para os noivos e assessores via API oficial de mensageria.
- **Conciliação Bancária Automatizada:** Conexão via Open Finance para verificação automática de liquidação de parcelas bancárias.

---

## 8. Homologação e Transição Metodológica

Este documento consolida a linha de base estratégica e a modelagem conceitual do **Wedding Management System**, servindo como insumo formal e fundamento direto para a [Especificação de Requisitos de Software (SRS)](requirements.md).
