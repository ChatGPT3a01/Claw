"""LINE Bot webhook handler for LiangClaw."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request, HTTPException

from interfaces.message_adapter import ChatMessage


def create_line_router() -> APIRouter:
    """Create LINE Bot webhook router. Requires LINE_CHANNEL_* env vars."""
    from src.utils.config import get_config
    cfg = get_config()

    if not cfg.line_channel_access_token or not cfg.line_channel_secret:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET not set")

    from linebot.v3 import WebhookHandler
    from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
    from linebot.v3.webhooks import MessageEvent, TextMessageContent

    router = APIRouter()
    handler = WebhookHandler(cfg.line_channel_secret)
    line_config = Configuration(access_token=cfg.line_channel_access_token)

    @router.post("/webhook")
    async def line_webhook(request: Request):
        sig = request.headers.get("X-Line-Signature", "")
        body = (await request.body()).decode("utf-8")
        try:
            handler.handle(body, sig)
        except Exception as e:
            raise HTTPException(400, str(e))
        return "OK"

    @handler.add(MessageEvent, message=TextMessageContent)
    def on_text(event: MessageEvent):
        from interfaces.app import get_agent
        user_id = event.source.user_id
        text = event.message.text

        msg = ChatMessage(content=text, source="line", user_id=user_id)
        loop = asyncio.new_event_loop()
        try:
            resp = loop.run_until_complete(get_agent().chat(msg))
        finally:
            loop.close()

        reply = resp.content[:5000]  # LINE limit
        with ApiClient(line_config) as api:
            MessagingApi(api).reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)],
                )
            )

    return router
