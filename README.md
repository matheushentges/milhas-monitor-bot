# ✈️ Bot de Monitoramento de Promoções de Milhas e Pontos

Um bot autônomo, gratuito e de código aberto para monitorar transferências bonificadas de pontos de cartões de crédito (**Sicredi**, **Livelo**, **Esfera**, **Itaú**, **Bradesco**, **C6 Bank**, etc.) para programas de milhas aéreas (**Smiles**, **Azul Fidelidade**, **LATAM Pass**, **TAP Miles&Go**, etc.).

O bot executa automaticamente a cada **1 hora** via **GitHub Actions** (sem custos de servidor) e envia notificações instantâneas no **Telegram**.

---

## 🚀 Como Funciona

1. **Varredura Periódica:** A cada 1 hora, o GitHub Actions dispara uma rotina que busca promoções em feeds RSS especializados (*Melhores Destinos*, *Passageiro de Primeira*, *Pontos pra Voar*) e páginas diretas dos programas (*Smiles*, *Azul*).
2. **Filtro Inteligente:** Extrai automaticamente o banco de origem, o programa de destino e o percentual de bônus (ex: `70% de bônus`).
3. **Deduplicação:** Compara os links e IDs com o arquivo `data/seen_posts.json` para **nunca enviar a mesma promoção duas vezes**.
4. **Notificação no Telegram:** Envia um alerta com link direto da matéria e do cadastro da promoção.
5. **Auto-Persistência:** Atualiza o histórico de promoções vistas no próprio repositório com `[skip ci]`.

---

## 📲 Passo a Passo de Configuração

### 1. Criar o Bot no Telegram (Leva 2 minutos)
1. No Telegram, converse com o [@BotFather](https://t.me/BotFather).
2. Envie o comando `/newbot`.
3. Escolha um nome (ex.: `Alerta de Milhas`) e um username (ex.: `meu_milhas_bot`).
4. O BotFather fornecerá um **Token de Acesso** (ex.: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`). Guarde esse token.
5. Abra uma conversa com o seu novo bot recém-criado e clique em **Começar (`/start`)**.

### 2. Descobrir seu `CHAT_ID`
1. No Telegram, envie uma mensagem para o [@userinfobot](https://t.me/userinfobot).
2. Ele responderá com o seu **Id numérico** (ex.: `123456789`). Esse é o seu `CHAT_ID`.

---

### 3. Configurar no GitHub

1. Faça um **Fork** ou clone este repositório na sua conta do GitHub.
2. No seu repositório no GitHub, vá em:  
   `Settings` > `Secrets and variables` > `Actions` > `New repository secret`.
3. Adicione os dois segredos:
   * **`TELEGRAM_BOT_TOKEN`**: o token fornecido pelo BotFather.
   * **`TELEGRAM_CHAT_ID`**: o seu ID numérico obtido pelo userinfobot.
4. **Ativar Permissão de Escrita do Actions:**
   * Vá em `Settings` > `Actions` > `General`.
   * Na seção **Workflow permissions**, selecione **Read and write permissions**.
   * Clique em **Save**. *(Isso permite que o bot registre as promoções enviadas em `data/seen_posts.json`)*.

Pronto! O bot já começará a rodar automaticamente a cada 1 hora.

---

## 🛠️ Personalização (`config.yaml`)

Você pode escolher quais bancos monitorar editando o arquivo `config.yaml`:

```yaml
# Monitore todos os bancos:
banks:
  - all

# OU especifique apenas os cartões que você utiliza:
# banks:
#   - sicredi
#   - livelo
#   - esfera
#   - itau

# Percentual mínimo de bônus para disparar alerta (0 = todas as promoções):
min_bonus_percentage: 0
```

---

## 💻 Testando Localmente

Se você quiser testar o bot na sua própria máquina antes de colocar em produção:

```bash
# 1. Crie o ambiente virtual e instale as dependências
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Rode em modo de simulação (Dry-Run): não envia mensagens nem altera o histórico
python -m src.main --dry-run --verbose

# 3. Rodar os testes unitários
pytest
```

---

## ⚡ Como Disparar Manualmente no GitHub

Para testar no GitHub imediatamente sem esperar o cron de 1 hora:
1. Acesse a aba **Actions** no seu repositório.
2. No menu lateral esquerdo, clique em **Monitoramento de Milhas**.
3. Clique no botão **Run workflow**.

---

## 📄 Licença
Distribuído sob a licença MIT. Sinta-se à vontade para compartilhar, modificar e contribuir!
