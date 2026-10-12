"""Envío de correo por SMTP (configuración por cliente)."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.models.empresa import EmpresaConfig


class MailError(Exception):
    """Error de configuración o envío de correo."""


def _connect(empresa: EmpresaConfig) -> smtplib.SMTP:
    if empresa.smtp_security == "ssl":
        return smtplib.SMTP_SSL(empresa.smtp_host, empresa.smtp_port, timeout=25)
    server = smtplib.SMTP(empresa.smtp_host, empresa.smtp_port, timeout=25)
    if empresa.smtp_security == "tls":
        server.starttls()
    return server


def send_email(
    empresa: EmpresaConfig,
    *,
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    attachments: list[tuple[str, bytes, str]] | None = None,
) -> None:
    if not empresa.smtp_activo or not empresa.smtp_host:
        raise MailError("El correo (SMTP) no está configurado o está inactivo.")
    from_email = empresa.smtp_from_email or empresa.smtp_username or empresa.email
    if not from_email:
        raise MailError("Falta el correo remitente (From).")

    from_name = empresa.smtp_from_name or empresa.nombre_comercial or empresa.razon_social
    message = EmailMessage()
    message["From"] = formataddr((from_name, from_email)) if from_name else from_email
    message["To"] = ", ".join(to)
    if cc:
        message["Cc"] = ", ".join(cc)
    message["Subject"] = subject
    message.set_content(body)

    for filename, content, mime in attachments or []:
        maintype, _, subtype = mime.partition("/")
        message.add_attachment(
            content, maintype=maintype or "application", subtype=subtype or "octet-stream",
            filename=filename,
        )

    recipients = [*to, *(cc or [])]
    try:
        with _connect(empresa) as server:
            if empresa.smtp_username:
                server.login(empresa.smtp_username, empresa.smtp_password)
            server.send_message(message, from_addr=from_email, to_addrs=recipients)
    except MailError:
        raise
    except Exception as exc:  # noqa: BLE001 - se sanea el mensaje para el cliente
        raise MailError(f"No se pudo enviar el correo ({type(exc).__name__}).") from exc
