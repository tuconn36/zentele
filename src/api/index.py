"""Telegram webhook cho Vercel (ASGI)."""

import hmac
import json
import logging
import os

from telegram import Update

from src.bot import main as bot, handlers

logger = logging.getLogger(__name__)
MAX_BODY_BYTES = 1024 * 1024

# Các tác vụ trong bộ nhớ không tồn tại đủ lâu trên serverless.
handlers.AUTO_DISSOLVE = False


async def _respond(send, status, message):
    body = message.encode("utf-8")
    await send({"type": "http.response.start", "status": status, "headers": [
        (b"content-type", b"text/plain; charset=utf-8"),
        (b"content-length", str(len(body)).encode("ascii")),
    ]})
    await send({"type": "http.response.body", "body": body})


async def app(scope, receive, send):
    if scope["type"] != "http":
        return
    if scope["method"] != "POST":
        await _respond(send, 405, "Method not allowed")
        return

    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    headers = dict(scope.get("headers", []))
    supplied = headers.get(b"x-telegram-bot-api-secret-token", b"")
    if not secret or not hmac.compare_digest(secret.encode("utf-8"), supplied):
        await _respond(send, 403, "Forbidden")
        return

    body = bytearray()
    while True:
        event = await receive()
        if event["type"] == "http.disconnect":
            return
        if event["type"] != "http.request":
            continue
        body.extend(event.get("body", b""))
        if len(body) > MAX_BODY_BYTES:
            await _respond(send, 413, "Payload too large")
            return
        if not event.get("more_body", False):
            break

    try:
        payload = json.loads(body)
        if not isinstance(payload, dict) or not isinstance(payload.get("update_id"), int):
            raise ValueError("Invalid update")
    except (ValueError, UnicodeDecodeError):
        await _respond(send, 400, "Invalid update")
        return

    try:
        application = bot.build_application()
        async with application:
            update = Update.de_json(payload, application.bot)
            await application.process_update(update)
    except Exception:
        logger.exception("Không xử lý được Telegram webhook")
        await _respond(send, 500, "Webhook error")
        return
    await _respond(send, 200, "OK")
