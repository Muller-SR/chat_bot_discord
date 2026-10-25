# Mestre RPG — Bot para Discord

Bot de RPG de fantasia para jogar pelo Discord. Crie um personagem, evolua em aventuras narradas por IA ou em modo de demonstração, use itens e enfrente outros jogadores.

## Funcionalidades

- Criação de personagens das classes Guerreiro, Mago e Arqueiro.
- Ficha com vida, ataque, defesa, experiência e nível.
- Aventuras com narração opcional pela API da OpenAI ou do Google Gemini. Sem chave de IA, o bot usa uma narrativa local de demonstração.
- Combate entre jogadores, rolagens de dados D6, D10, D12 e D20 e itens consumíveis.
- Dados do jogo salvos em SQLite.

## Requisitos

- Python 3.10 ou superior.
- Uma aplicação e um bot criados no [Discord Developer Portal](https://discord.com/developers/applications).
- Uma chave da OpenAI ou do Gemini é opcional. O modo de demonstração funciona sem elas.

## Instalação

No terminal, entre na pasta do projeto:

```bash
cd bot-RPG
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, use `.venv\Scripts\Activate.ps1` para ativar o ambiente.

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` dentro de `bot-RPG/`:

```env
DISCORD_TOKEN=seu_token_do_bot
DISCORD_GUILD_ID=id_do_servidor_de_teste

# Opcional: auto escolhe Gemini, depois OpenAI; sem chaves, usa demo.
AI_PROVIDER=auto
GEMINI_API_KEY=


# O caminho padrão é data/mestre_rpg.sqlite3.
DATABASE_PATH=data/mestre_rpg.sqlite3
```

Para usar um provedor específico, configure `AI_PROVIDER=gemini` ou `AI_PROVIDER=openai` e preencha a chave correspondente. Para não fazer chamadas de IA, use `AI_PROVIDER=demo`. Os nomes dos modelos podem ser ajustados com `GEMINI_MODEL` e `OPENAI_MODEL`.

Convide o bot ao seu servidor com os escopos `bot` e `applications.commands`. O ID configurado em `DISCORD_GUILD_ID` é usado para sincronizar os comandos de barra nesse servidor.

## Executar

Ainda dentro de `bot-RPG/`, com o ambiente virtual ativado:

```bash
python main.py
```

## Comandos

| Comando | O que faz |
| --- | --- |
| `/ping` | Verifica se o bot está online. |
| `/criar` | Cria um personagem e entrega os itens iniciais. |
| `/ficha` | Consulta os atributos e a experiência do personagem. |
| `/aventura` | Descreve uma ação para continuar a aventura e ganhar experiência. |
| `/atacar` | Ataca o personagem de outro jogador. |
| `/dado` | Rola um D6, D10, D12 ou D20. |
| `/inventario` | Lista os itens do personagem. |
| `/usar` | Usa uma poção ou um pergaminho de experiência. |

## Estrutura do projeto

```text
bot-RPG/
├── comands/    # Comandos e integrações com o Discord
├── config/     # Classes, itens e configurações
├── services/   # Narração e armazenamento SQLite
├── main.py     # Inicialização do bot
└── requirements.txt
```

O arquivo `.env`, o ambiente virtual e o banco SQLite local são ignorados pelo Git. Não publique tokens ou chaves de API.
