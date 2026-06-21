"""
zapi_client.py

Responsável por enviar mensagens de texto via WhatsApp usando a Z-API.
Documentação: https://developer.z-api.io/
"""

import logging
import re

import requests

logger = logging.getLogger(__name__)


class ZApiClient:
    def __init__(self, instance_id: str, token: str, client_token: str, timeout: int = 15):
        if not instance_id or not token:
            raise ValueError("ZAPI_INSTANCE_ID e ZAPI_TOKEN são obrigatórios.")

        self.base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
        self.client_token = client_token
        self.timeout = timeout

    @staticmethod
    def _normalizar_telefone(telefone: str) -> str:
        """Remove caracteres não numéricos do telefone (Z-API espera só dígitos, com DDI)."""
        return re.sub(r"\D", "", telefone)

    def enviar_mensagem(self, telefone: str, mensagem: str) -> bool:
        """
        Envia uma mensagem de texto para o telefone informado.
        Retorna True se o envio foi aceito pela Z-API, False caso contrário.
        """
        telefone_normalizado = self._normalizar_telefone(telefone)

        if not telefone_normalizado:
            logger.error("Telefone inválido, envio abortado: '%s'", telefone)
            return False

        payload = {
            "phone": telefone_normalizado,
            "message": mensagem,
        }

        headers = {"Content-Type": "application/json"}
        if self.client_token:
            headers["Client-Token"] = self.client_token

        try:
            resposta = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            logger.error("Erro de rede ao enviar mensagem para %s: %s", telefone_normalizado, exc)
            return False

        if resposta.status_code in (200, 201):
            logger.info("Mensagem enviada com sucesso para %s.", telefone_normalizado)
            return True

        logger.error(
            "Falha ao enviar mensagem para %s. Status: %s | Resposta: %s",
            telefone_normalizado,
            resposta.status_code,
            resposta.text,
        )
        return False
