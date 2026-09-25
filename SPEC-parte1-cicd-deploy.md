# Spec — Parte 1: primeiro assistente de IA no ar

> **Status:** proposta para aprovação. Esta especificação descreve o que será
> construído; ela ainda não implementa o aplicativo.

## Decisões e premissas já informadas

| Item | Decisão |
| --- | --- |
| Repositório GitHub | `Jmerenciano/analisededadosIA` |
| Conta Hugging Face | `Jmerenciano` (inferida do nome informado) |
| Space | `analisededadosIA` (a confirmar ao criar o Space) |
| Hardware do Space | ZeroGPU |
| Idioma da interface | Português do Brasil |

Os modelos, identidade visual e perguntas sugeridas ainda serão escolhidos na
configuração, sem alterar código. Enquanto não houver uma logo, a configuração
aceitará uma imagem padrão local do projeto.

---

## 1. Objetivo, público e escopo

### Objetivo

Publicar gratuitamente um chat acessível por link, no Hugging Face Spaces, para
responder dúvidas de **engenharia de dados e Inteligência Artificial** de forma
didática, como um professor. O dono do projeto poderá personalizá-lo por um
único arquivo versionado no GitHub.

### Público

Alunos iniciantes ou intermediários que desejam tirar dúvidas sobre engenharia
de dados e IA, em português.

### Entra nesta parte

- Chat público, sem conta de usuário.
- Cabeçalho com logo, nome e descrição do assistente.
- Tema configurável (uma ou duas cores), respostas e mensagens de interface em
  português.
- Perguntas sugeridas clicáveis.
- Configuração declarativa única em `config/assistente.yaml`.
- Uso opcional de chaves OpenRouter, Anthropic e OpenAI, com tentativa em ordem
  configurável e troca automática antes de qualquer resposta ser retornada.
- Validação da configuração, testes e bloqueio de deploy inseguro ou inválido.
- Deploy automático do GitHub para o Hugging Face Space, somente após o portão
  de qualidade passar.

### Fica fora desta parte

- **Parte 2:** busca em documentos próprios, base de conhecimento, RAG,
  upload/indexação de arquivos e citações de documentos.
- **Parte 3:** domínio e hospedagem próprios, site institucional e identidade
  visual totalmente sob medida.
- Login, perfis, histórico de conversas, banco de dados e moderação por usuário.

---

## 2. Stack escolhida e restrições

### Tecnologias

| Camada | Escolha | Motivo |
| --- | --- | --- |
| Interface e servidor | Python + Gradio | Permite hospedar chat e interface no Space com pouca infraestrutura. |
| Provedor Anthropic | SDK oficial `anthropic` | Requisito do projeto. |
| Provedores OpenAI e OpenRouter | SDK `openai` | Requisito do projeto; para OpenRouter será usado `base_url=https://openrouter.ai/api/v1`. |
| Configuração | YAML validado por modelo Python | Simples de editar pela web do GitHub e capaz de fornecer erros claros. |
| Testes | `pytest` | Testes automáticos da configuração e da troca de provedores. |
| Qualidade/segredos | `ruff`, `gitleaks` e `detect-secrets` | Evita erros simples e bloqueia vazamento acidental de chave. |
| CI/CD | GitHub Actions + API do Hugging Face Hub | Valida primeiro e só então atualiza o Space. |

### Chaves e seleção de provedores

O aplicativo reconhecerá exclusivamente estas variáveis de ambiente:

| Provedor | Secret no Hugging Face | Cliente |
| --- | --- | --- |
| OpenRouter | `OPENROUTER_API_KEY` | `openai` com URL base do OpenRouter |
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic` |
| OpenAI | `OPENAI_API_KEY` | `openai` |

Não é obrigatório cadastrar as três. Na inicialização, o app considera apenas
as entradas da configuração cujo secret correspondente exista e não esteja
vazio. A ordem de `provedores` decide as tentativas. Se uma chamada falhar
**antes de produzir resposta**, o app passa ao próximo provedor disponível. Se
todos falharem, o chat apresenta uma mensagem em português com o nome de cada
provedor/modelo tentado e um motivo sanitizado (por exemplo, limite de uso,
crédito, indisponibilidade ou erro de autenticação), sem mostrar chaves ou
corpo sensível da requisição.

Depois que o primeiro trecho de uma resposta já tiver sido enviado ao usuário,
não haverá troca de modelo no meio da resposta: o app exibirá uma falha clara,
pois misturar respostas de modelos diferentes seria confuso.

### Restrições conhecidas do Hugging Face Spaces / ZeroGPU

- O Space precisa ser criado manualmente como Space Gradio e configurado com
  hardware ZeroGPU pela conta dona. A disponibilidade de GPU pode ter fila e
  não é garantia de resposta instantânea.
- O Space é público, portanto **nenhuma chave** pode ser colocada em arquivo,
  commit, log, mensagem de erro ou variável exposta ao navegador. As chaves são
  cadastradas como *Secrets* nas configurações do Space.
- O GitHub Action precisa de um token de escrita do Hugging Face, guardado no
  segredo do repositório `HF_TOKEN`; ele não será salvo no código.
- Spaces podem reiniciar ou reconstruir após uma atualização. Enquanto o Action
  falha antes do envio, a revisão anterior do Space permanece publicada.
- ZeroGPU acelera a aplicação, não substitui nem fornece créditos para APIs de
  OpenRouter, Anthropic ou OpenAI.

---

## 3. Estrutura de arquivos do projeto

```text
.
├── .github/
│   └── workflows/
│       └── validar-e-publicar.yml    # valida e, se aprovado, envia ao Space
├── config/
│   └── assistente.yaml               # único arquivo editável de personalização
├── assets/
│   └── logo-padrao.svg               # usado se a configuração apontar para ele
├── app.py                             # ponto de entrada exigido pelo Space
├── src/
│   ├── app.py                        # inicialização do Gradio
│   ├── config.py                     # leitura e validação do YAML
│   ├── providers.py                  # clientes e fallback dos três provedores
│   └── ui.py                         # componentes e textos da tela
├── tests/
│   ├── test_config.py
│   ├── test_providers.py
│   └── test_ui.py
├── .gitleaks.toml                    # regras de varredura de segredos
├── .gitignore
├── README.md                          # instalação, secrets e operação
├── requirements.txt
└── SPEC-parte1-cicd-deploy.md
```

Não haverá arquivo `.env` versionado. Um `.env.example`, se necessário para
desenvolvimento local, conterá somente nomes de variáveis e valores vazios.

---

## 4. Contrato do arquivo de configuração

O único arquivo de personalização será `config/assistente.yaml`. Ele terá esta
estrutura conceitual; comentários e documentação explicarão cada campo.

| Campo | Obrigatório | Valores aceitos | Padrão | Regra de validação |
| --- | --- | --- | --- | --- |
| `assistente.nome` | Sim | Texto de 2 a 80 caracteres | — | Não pode ser vazio. |
| `assistente.descricao` | Sim | Texto de 10 a 220 caracteres | — | Não pode ser vazia. |
| `assistente.idioma` | Não | `pt-BR` | `pt-BR` | Nesta parte, somente `pt-BR`. |
| `tema.cor_primaria` | Sim | Hex `#RRGGBB` | — | Cor CSS hexadecimal válida. |
| `tema.cor_secundaria` | Não | Hex `#RRGGBB` | cor primária | Cor CSS hexadecimal válida. |
| `tema.modo` | Não | `claro` ou `escuro` | `claro` | Define contraste base do chat. |
| `logo.caminho` | Sim | Caminho relativo em `assets/` | `assets/logo-padrao.svg` | Arquivo deve existir, não pode sair de `assets/` e deve ser SVG/PNG/JPG/WEBP. |
| `logo.largura_px` | Não | Inteiro de 32 a 320 | `96` | Limita tamanho visual da logo. |
| `provedores` | Sim | Lista ordenada de 1 a 3 entradas | — | Ao menos uma entrada; um tipo por vez, sem duplicatas. |
| `provedores[].tipo` | Sim | `openrouter`, `anthropic`, `openai` | — | Determina qual secret e SDK são usados. |
| `provedores[].modelo` | Sim | Identificador não vazio de até 200 caracteres | — | Enviado ao provedor selecionado. Para OpenRouter, pode terminar em `:free`. |
| `provedores[].max_tokens` | Não | Inteiro de 64 a 4.096 | `1024` | Limite de geração por tentativa; o provedor ainda pode impor limite menor. |
| `comportamento.instrucoes_sistema` | Sim | Texto de 40 a 8.000 caracteres | — | Define papel, público, limites e didática do assistente. |
| `comportamento.aviso_escopo` | Não | Texto de até 500 caracteres | aviso padrão | Mostrado quando a pergunta fugir do tema. |
| `perguntas_exemplo` | Sim | Lista de 2 a 8 textos de 5 a 180 caracteres | — | Sem itens vazios ou repetidos. |
| `chat.mensagem_boas_vindas` | Não | Texto de 10 a 500 caracteres | mensagem padrão | Deve estar em português. |
| `chat.max_caracteres_pergunta` | Não | Inteiro de 100 a 8.000 | `2.000` | Impede mensagens excessivamente longas. |

O validador rejeitará campos desconhecidos, tipos incorretos, YAML inválido,
texto vazio após remover espaços, caminhos de logo inválidos e configurações que
não tenham pelo menos um provedor válido. O modelo pode ser qualquer identificador
compatível com a conta do usuário; por isso a disponibilidade e o preço do modelo
não serão assumidos pela validação estática.

### Exemplo de intenção de ordem

A primeira entrada pode ser um modelo gratuito do OpenRouter, seguida por OpenAI
e Anthropic. Isso significa: tentar o gratuito primeiro; se estiver lotado, sem
crédito ou indisponível antes de responder, tentar o seguinte. O dono troca esses
nomes diretamente no YAML quando quiser, sem editar Python.

---

## 5. Requisitos funcionais

- **RF1.** O usuário deve conseguir abrir a URL pública do Space e conversar sem
  login.
- **RF2.** A tela deve exibir, em português, logo, nome, descrição, boas-vindas,
  campo de pergunta, botão de enviar, estado de carregamento e erros.
- **RF3.** A tela deve aplicar as cores e a largura de logo definidas na
  configuração e manter contraste legível no modo escolhido.
- **RF4.** A tela deve exibir de duas a oito perguntas de exemplo como botões;
  clicar em uma deve preencher/enviar a pergunta ao chat.
- **RF5.** Cada requisição deve incluir as instruções configuradas e manter o
  contexto somente da conversa aberta na página; não deve salvar histórico após
  ela terminar.
- **RF6.** O app deve suportar OpenRouter com `OPENROUTER_API_KEY`, Anthropic
  com `ANTHROPIC_API_KEY` e OpenAI com `OPENAI_API_KEY`, funcionando com somente
  uma dessas chaves.
- **RF7.** O app deve pular provedores sem secret e tentar os restantes conforme
  a ordem de `provedores`.
- **RF8.** Em falha anterior à resposta (rede, timeout, limite, crédito,
  indisponibilidade ou autenticação), o app deve tentar automaticamente o próximo
  provedor disponível.
- **RF9.** Se nenhuma tentativa funcionar, o chat deve informar cada tentativa e
  causa compreensível, sem vazar segredos, tokens, cabeçalhos ou dados internos.
- **RF10.** O app deve validar a configuração antes de iniciar e mostrar ao dono
  uma mensagem diagnóstica clara se estiver inválida.
- **RF11.** Alterar somente `config/assistente.yaml` no GitHub deve disparar a
  validação e, quando aprovada, atualizar o Space automaticamente.
- **RF12.** Se validações falharem, o workflow deve falhar antes de enviar uma
  revisão nova ao Space; a versão publicada anterior deve continuar disponível.
- **RF13.** O pipeline deve bloquear publicação se detectar segredo em arquivos
  rastreados, inclusive chaves compatíveis com OpenAI, Anthropic e OpenRouter.

---

## 6. Portão de testes e verificações

- **T1 — Formatação e análise estática:** `ruff format --check` e `ruff check`
  devem passar.
- **T2 — YAML válido:** o arquivo deve ser lido sem erro de sintaxe.
- **T3 — Contrato:** testes devem aceitar uma configuração completa válida e
  rejeitar, com mensagem específica, cor inválida, campo vazio, modelo ausente,
  caminho fora de `assets/`, logo inexistente, provedor duplicado e pergunta
  exemplo inválida.
- **T4 — Arquivo de logo:** a logo configurada deve existir no commit enviado e
  ter uma extensão permitida.
- **T5 — Provedor individual:** testes com clientes falsos devem cobrir cada tipo
  de provedor e confirmar a biblioteca/URL correta, sem chamar APIs reais.
- **T6 — Fallback:** testes devem comprovar: (a) pula secret ausente; (b) uma
  falha antes de resposta chama o próximo; (c) o primeiro sucesso interrompe as
  tentativas; (d) todos falhos retornam lista sanitizada de razões.
- **T7 — Segurança:** `gitleaks detect` e `detect-secrets` devem analisar os
  arquivos rastreados. Qualquer segredo novo bloqueia o workflow.
- **T8 — Dependências:** instalação a partir de `requirements.txt` deve concluir
  em ambiente limpo e conter `gradio`, `anthropic`, `openai` e dependências de
  validação necessárias.
- **T9 — Testes automatizados:** `pytest` deve passar integralmente.
- **T10 — Empacotamento do Space:** o workflow deve confirmar que os arquivos
  obrigatórios do Space existem antes de publicar.

Nenhum teste automatizado usará chaves reais, crédito ou chamada externa a um
modelo. Um teste manual posterior verificará cada secret que o dono decidir
cadastrar.

---

## 7. Pipeline de deploy e configurações manuais

### Fluxo automático no GitHub Actions

1. Um push na branch principal (`main`) ou uma atualização de pull request inicia
   o workflow.
2. O workflow baixa o repositório, instala Python e dependências.
3. Executa T1 a T10. Em pull request, para depois das verificações; não publica.
4. Em push na `main`, somente se tudo passar, prepara a versão do Space.
5. Usa `HF_TOKEN` exclusivamente no ambiente do job para enviar os arquivos ao
   repositório do Space `Jmerenciano/analisededadosIA`.
6. O Hugging Face reconstrói o Space. O Action informa o link da execução; o
   dono acompanha o log de build do Space se a reconstrução falhar.

Para manter o último site funcional quando há erro de configuração, a etapa de
envio só ocorre após todas as verificações. Assim, uma configuração ruim nunca é
enviada ao Space.

### Configurações manuais, uma única vez

1. Criar `Jmerenciano/analisededadosIA` no Hugging Face como **Space Gradio**,
   público, selecionando **ZeroGPU**.
2. Criar um token do Hugging Face com permissão de escrita limitada ao necessário
   e salvar seu valor como o secret `HF_TOKEN` em **GitHub → Settings → Secrets
   and variables → Actions**.
3. Em **Space → Settings → Secrets**, cadastrar uma ou mais das chaves
   `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` e `OPENAI_API_KEY`. Não usar
   *Variables* públicas para essas chaves.
4. Proteger a branch `main`, exigindo que o workflow de validação passe antes de
   mesclar alterações, se essa opção estiver disponível na conta GitHub.
5. Editar `config/assistente.yaml` com identidade, modelos, instruções e
   perguntas. Fazer commit pela interface web do GitHub é suficiente.

### O que nunca configurar no repositório

- Valores reais de chaves de API, tokens do Hugging Face ou arquivos `.env`.
- A chave de uma API em `assistente.yaml`, README, screenshot, issue, comentário
  de código ou log de teste.

---

## 8. Critérios de aceite

- [ ] Existe uma URL pública do Space acessível sem login.
- [ ] O topo contém logo, nome e descrição configurados.
- [ ] A página usa as cores configuradas e todos os textos visíveis estão em
  português.
- [ ] As perguntas de exemplo aparecem e uma delas inicia uma interação.
- [ ] O assistente responde de modo didático a uma pergunta de engenharia de
  dados ou IA usando uma única chave cadastrada.
- [ ] Com duas ou três chaves, a ordem configurada é respeitada e uma falha antes
  da resposta aciona o próximo provedor disponível.
- [ ] Sem chave correspondente, o provedor é ignorado sem quebrar o chat.
- [ ] Se todas as tentativas falharem, a interface mostra motivos úteis sem
  revelar segredo algum.
- [ ] Uma mudança de cor ou pergunta no GitHub chega ao Space após o workflow
  aprovado.
- [ ] Uma cor inválida, logo ausente ou campo obrigatório vazio falha no Action
  antes de qualquer envio e a versão anterior segue no ar.
- [ ] Um segredo introduzido acidentalmente bloqueia a publicação.

---

## 9. Ordem das tarefas de implementação

Cada tarefa deve ser implementada, testada, revisada e aprovada antes de iniciar
a seguinte.

1. **Base do projeto:** criar a estrutura Python/Gradio, dependências, ignore e
   README mínimo, sem chaves e sem integração de IA.
2. **Configuração:** criar o YAML de exemplo e o leitor/validador com testes dos
   campos, cores, logo e perguntas.
3. **Interface:** implementar a página Gradio em português que renderiza a
   identidade e as perguntas a partir da configuração, ainda com resposta falsa.
4. **OpenRouter:** implementar cliente `openai` com URL base configurada, secret
   de ambiente, tratamento sanitizado de falhas e testes falsos.
5. **Anthropic e OpenAI:** implementar os dois clientes exigidos e testes de cada
   um, sem chamadas reais.
6. **Fallback:** implementar seleção por ordem, pulo de secret ausente e relatório
   de esgotamento, com os cenários T6.
7. **Segurança e qualidade:** adicionar ruff, pytest e varredura de segredos;
   documentar operação segura.
8. **CI/CD:** criar o Action que executa o portão e publica no Space apenas em
   push aprovado na `main`.
9. **Publicação assistida:** configurar secrets no GitHub/Hugging Face, criar o
   Space ZeroGPU e validar manualmente a URL e cada provedor cadastrado.
10. **Teste de aceite:** alterar pelo GitHub uma cor/pergunta e, separadamente,
    introduzir e reverter uma configuração inválida para provar o bloqueio.

---

## 10. Erros comuns e como resolver

| Situação | Causa provável | Como resolver |
| --- | --- | --- |
| O workflow acusa cor inválida | Cor não está no formato `#RRGGBB` | Usar, por exemplo, `#0F172A`; incluir o `#` e seis dígitos hexadecimais. |
| O workflow acusa logo ausente | Caminho errado ou arquivo não foi enviado | Colocar a imagem em `assets/`, confirmar maiúsculas/minúsculas e fazer commit dela. |
| Space inicia, mas nenhum modelo funciona | Nenhum secret foi cadastrado ou o nome está errado | Cadastrar pelo menos um secret com o nome exato listado nesta spec e reiniciar o Space. |
| OpenRouter falha em modelo gratuito | Modelo está lotado, removido ou com limite | Manter um segundo provedor/modelo configurado; revisar o identificador do modelo. |
| Anthropic/OpenAI falha com crédito | Conta sem saldo, limite ou permissão para o modelo | Verificar faturamento/limites na conta do provedor e escolher modelo autorizado. |
| O erro mostra informação sensível | Exceção não foi sanitizada | Não compartilhar o log publicamente; corrigir o mapeamento de erros antes de novo deploy e rotacionar a chave se ela aparecer. |
| Gitleaks bloqueia o commit | Uma chave ou token foi colado em arquivo | Remover do arquivo e do histórico/commit antes de publicar; revogar e recriar a chave exposta. |
| O Action não consegue publicar | `HF_TOKEN` ausente, inválido ou sem escrita | Criar/revisar o secret no GitHub e conferir a permissão do token e o nome do Space. |
| O Space fica aguardando recurso | Fila ou indisponibilidade do ZeroGPU | Aguardar, tentar novamente ou usar CPU temporariamente para diagnosticar; isso não altera as chaves de IA. |
| A versão nova não aparece | Build ainda em andamento ou Action falhou | Abrir primeiro o log do Action; se ele passou, conferir o log de build do Space. |

---

## Próximo passo após aprovação

Depois de aprovar esta spec, o pedido de execução será: **“Implemente a tarefa 1
da spec e me mostre como testar.”** A implementação seguirá uma tarefa por vez.
