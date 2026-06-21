"""
supabase_client.py

Responsável por toda a comunicação com o Supabase:
- Cria o client autenticado
- Busca os contatos cadastrados na tabela configurada

Tabela esperada (exemplo de setup, veja README.md):

    create table contatos (
        id bigint generated always as identity primary key,
        nome_contato text not null,
        telefone text not null,
        created_at timestamp with time zone default now()
    );
"""

import logging
from typing import List, Dict

from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseContatosClient:
    def __init__(self, url: str, key: str, table: str, col_nome: str, col_telefone: str):
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios.")

        self.table = table
        self.col_nome = col_nome
        self.col_telefone = col_telefone

        try:
            self.client: Client = create_client(url, key)
        except Exception as exc:
            logger.error("Falha ao criar client do Supabase: %s", exc)
            raise

    def buscar_contatos(self, limite: int = 3) -> List[Dict]:
        """
        Busca até `limite` contatos na tabela configurada.
        Retorna uma lista de dicts, ex:
        [{"nome_contato": "Maria", "telefone": "5511999999999"}, ...]
        """
        try:
            resposta = (
                self.client.table(self.table)
                .select(f"{self.col_nome}, {self.col_telefone}")
                .order("id", desc=False)
                .limit(limite)
                .execute()
            )
        except Exception as exc:
            logger.error("Erro ao consultar a tabela '%s' no Supabase: %s", self.table, exc)
            raise

        contatos = resposta.data or []

        if not contatos:
            logger.warning("Nenhum contato encontrado na tabela '%s'.", self.table)
            return []

        # Normaliza as chaves para nome_contato / telefone, independente do nome
        # configurado nas colunas, para o resto do código não depender disso.
        contatos_normalizados = []
        for c in contatos:
            nome = c.get(self.col_nome)
            telefone = c.get(self.col_telefone)

            if not nome or not telefone:
                logger.warning("Contato ignorado por dados incompletos: %s", c)
                continue

            contatos_normalizados.append({
                "nome_contato": str(nome).strip(),
                "telefone": str(telefone).strip(),
            })

        logger.info("Total de contatos válidos encontrados: %d", len(contatos_normalizados))
        return contatos_normalizados
