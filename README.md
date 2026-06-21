# supabase-zapi-whatsapp

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Z-API](https://img.shields.io/badge/Z--API-252F3F?style=for-the-badge)

Desafio b2bflow — Estágio em Desenvolvimento Python

Script em Python que lê contatos cadastrados no **Supabase** e envia a mensagem
`"Olá, <nome_contato> tudo bem com você?"` via **WhatsApp**, usando a **Z-API**.

## 🧱 Stack

- Python 3.10+
- [Supabase](https://supabase.com/) (banco de dados / plano free)
- [Z-API](https://www.z-api.io/) (envio de WhatsApp / plano free)
- `python-dotenv` para variáveis de ambiente

---

## 1. Setup da tabela no Supabase

No painel do Supabase, vá em **SQL Editor** e rode:

```sql
create table contatos (
    id bigint generated always as identity primary key,
    nome_contato text not null,
    telefone text not null,
    created_at timestamp with time zone default now()
);

-- Exemplo de inserção de até 3 contatos
insert into contatos (nome_contato, telefone) values
('Maria Silva', '5511999990001'),
('João Souza', '5511999990002'),
('Ana Lima', '5511999990003');
```

> ⚠️ O campo `telefone` deve estar no formato internacional, só números
> (DDI + DDD + número), ex: `5511999990001`. O código remove automaticamente
> qualquer caractere não numérico antes de enviar.

Pegue a Project URL e a Publishable key (anon) diretamente no topo do painel inicial do projeto (botão "Cópia").

---

## 2. Variáveis de ambiente (`.env`)

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```env
# ===== SUPABASE =====
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=sua-chave-anon-ou-service-role-aqui

SUPABASE_TABLE=contatos
SUPABASE_COLUMN_NOME=nome_contato
SUPABASE_COLUMN_TELEFONE=telefone

MAX_CONTATOS=3

# ===== Z-API =====
ZAPI_INSTANCE_ID=sua-instance-id
ZAPI_TOKEN=seu-token
ZAPI_CLIENT_TOKEN=seu-client-token-de-seguranca
```

- `ZAPI_INSTANCE_ID` e `ZAPI_TOKEN`: encontrados no painel da sua instância Z-API.
- `ZAPI_CLIENT_TOKEN`: token de segurança da conta (Z-API > Segurança).
- `MAX_CONTATOS`: quantidade máxima de contatos para os quais a mensagem será
  enviada (o desafio pede até 3; se a tabela tiver menos, envia para todos
  que existirem).

⚠️ **Nunca commite o `.env`** — ele já está no `.gitignore`.

---

## 3. Como rodar

```bash
# 0. Clonar o repositório
git clone https://github.com/johnatanduarte/supabase-zapi-whatsapp.git
cd supabase-zapi-whatsapp

# 1. Criar e ativar um ambiente virtual
python3 -m venv venv
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar o .env (passo 2 acima)

# 4. Rodar o script
python main.py
```

### Saída esperada (exemplo de log)

```
2026-06-21 16:02:57 | INFO | Iniciando desafio b2bflow...
2026-06-21 16:02:59 | INFO | Total de contatos válidos encontrados: 3
2026-06-21 16:02:59 | INFO | Enviando mensagem para Maria Silva (5511999990001)...
2026-06-21 16:03:00 | INFO | Mensagem enviada com sucesso para 5511999990001.
2026-06-21 16:03:00 | INFO | Enviando mensagem para João Souza (5511999990002)...
2026-06-21 16:03:01 | INFO | Mensagem enviada com sucesso para 5511999990002.
2026-06-21 16:03:01 | INFO | Enviando mensagem para Ana Lima (5511999990003)...
2026-06-21 16:03:02 | INFO | Mensagem enviada com sucesso para 5511999990003.
2026-06-21 16:03:02 | INFO | Processo finalizado. Sucesso: 3 | Falhas: 0 | Total processado: 3
```

---

## 4. Estrutura do projeto

```
supabase-zapi-whatsapp/
├── main.py              # Orquestra o fluxo: busca contatos -> envia mensagens
├── supabase_client.py   # Camada de acesso ao Supabase
├── zapi_client.py       # Camada de envio via Z-API
├── requirements.txt     # Dependências
├── .env.example         # Modelo de variáveis de ambiente
├── .gitignore
└── README.md
```

## 5. Decisões de projeto / boas práticas

- **Separação de responsabilidades**: acesso ao Supabase, envio via Z-API e
  orquestração do fluxo estão em arquivos distintos.
- **Tratamento de erros**: falhas de conexão, variáveis ausentes ou contatos
  inválidos são tratadas e logadas, sem derrubar o processo inteiro caso um
  único envio falhe.
- **Logs**: todo o fluxo é logado (sucesso, falha, contatos ignorados) para
  facilitar debug.
- **Configuração via `.env`**: nenhuma credencial fica hardcoded no código.
- **Normalização de telefone**: remove automaticamente espaços, traços e
  parênteses antes de enviar à Z-API.

---

Desenvolvido para o desafio técnico de Estágio em Desenvolvimento Python — b2bflow ⚡
