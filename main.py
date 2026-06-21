"""
main.py

Fluxo principal do desafio b2bflow:
1. Lê variáveis de ambiente (.env)
2. Busca até N contatos cadastrados no Supabase
3. Para cada contato, monta a mensagem personalizada
4. Envia a mensagem via Z-API
5. Loga o resultado de cada envio

Como rodar:
    python main.py
"""

import logging
import os
import sys

from dotenv import load_dotenv

from supabase_client import SupabaseContatosClient
from zapi_client import ZApiClient

# ---------- Configuração de logs ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("b2bflow-desafio")

MENSAGEM_TEMPLATE = "Olá, {nome_contato} tudo bem com você?"


def carregar_configuracoes() -> dict:
    """Carrega e valida as variáveis de ambiente necessárias."""
    load_dotenv()

    config = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "SUPABASE_TABLE": os.getenv("SUPABASE_TABLE", "contatos"),
        "SUPABASE_COLUMN_NOME": os.getenv("SUPABASE_COLUMN_NOME", "nome_contato"),
        "SUPABASE_COLUMN_TELEFONE": os.getenv("SUPABASE_COLUMN_TELEFONE", "telefone"),
        "MAX_CONTATOS": int(os.getenv("MAX_CONTATOS", "3")),
        "ZAPI_INSTANCE_ID": os.getenv("ZAPI_INSTANCE_ID"),
        "ZAPI_TOKEN": os.getenv("ZAPI_TOKEN"),
        "ZAPI_CLIENT_TOKEN": os.getenv("ZAPI_CLIENT_TOKEN"),
    }

    obrigatorias = [
        "SUPABASE_URL", "SUPABASE_KEY", "ZAPI_INSTANCE_ID", "ZAPI_TOKEN"
    ]
    faltando = [chave for chave in obrigatorias if not config.get(chave)]

    if faltando:
        logger.error(
            "Variáveis de ambiente obrigatórias ausentes: %s. "
            "Confira o arquivo .env (use .env.example como referência).",
            ", ".join(faltando),
        )
        sys.exit(1)

    return config


def main():
    logger.info("Iniciando desafio b2bflow...")

    config = carregar_configuracoes()

    # ---------- 1. Conectar ao Supabase e buscar contatos ----------
    try:
        supabase_client = SupabaseContatosClient(
            url=config["SUPABASE_URL"],
            key=config["SUPABASE_KEY"],
            table=config["SUPABASE_TABLE"],
            col_nome=config["SUPABASE_COLUMN_NOME"],
            col_telefone=config["SUPABASE_COLUMN_TELEFONE"],
        )
        contatos = supabase_client.buscar_contatos(limite=config["MAX_CONTATOS"])
    except Exception:
        logger.exception("Erro inesperado ao buscar contatos no Supabase.")
        sys.exit(1)

    if not contatos:
        logger.warning("Nenhum contato válido para enviar mensagem. Encerrando.")
        sys.exit(0)

    # ---------- 2. Conectar ao Z-API ----------
    try:
        zapi_client = ZApiClient(
            instance_id=config["ZAPI_INSTANCE_ID"],
            token=config["ZAPI_TOKEN"],
            client_token=config["ZAPI_CLIENT_TOKEN"],
        )
    except Exception:
        logger.exception("Erro ao configurar client da Z-API.")
        sys.exit(1)

    # ---------- 3. Enviar mensagem personalizada para cada contato ----------
    total_sucesso = 0
    total_falha = 0

    for contato in contatos:
        nome = contato["nome_contato"]
        telefone = contato["telefone"]
        mensagem = MENSAGEM_TEMPLATE.format(nome_contato=nome)

        logger.info("Enviando mensagem para %s (%s)...", nome, telefone)

        sucesso = zapi_client.enviar_mensagem(telefone=telefone, mensagem=mensagem)

        if sucesso:
            total_sucesso += 1
        else:
            total_falha += 1

    logger.info(
        "Processo finalizado. Sucesso: %d | Falhas: %d | Total processado: %d",
        total_sucesso, total_falha, len(contatos),
    )


if __name__ == "__main__":
    main()
