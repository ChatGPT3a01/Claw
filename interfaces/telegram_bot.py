"""Telegram Bot webhook handler for LiangClaw."""
from __future__ import annotations

from fastapi import APIRouter, Request

from interfaces.message_adapter import ChatMessage


def create_telegram_router() -> APIRouter:
    """Create Telegram Bot webhook router. Requires TELEGRAM_BOT_TOKEN env var."""
    from src.utils.config import get_config
    cfg = get_config()

    if not cfg.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")

    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

    router = APIRouter()
    application = Application.builder().token(cfg.telegram_bot_token).build()

    async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "你好！我是阿亮老師 AI 助教 🦞\n\n"
            "可以問我教學設計、學習分析、課程規劃等問題。\n"
            "/help — 查看指令\n"
            "/skills — 列出可用技能\n"
            "/model <名稱> — 切換模型"
        )

    async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📖 LiangClaw 指令：\n"
            "/start — 開始對話\n"
            "/help — 顯示此說明\n"
            "/skills — 列出所有教育技能\n"
            "/model gemini-3-flash — 切換模型\n\n"
            "直接輸入文字即可對話！"
        )

    async def cmd_skills(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        from interfaces.app import get_agent
        skills = get_agent().skill_registry.list_skills()
        lines = [f"📚 可用技能 ({len(skills)} 個)：\n"]
        for s in skills[:30]:
            lines.append(f"• {s['display_name']}")
        if len(skills) > 30:
            lines.append(f"\n...還有 {len(skills) - 30} 個")
        await update.message.reply_text("\n".join(lines))

    async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        from interfaces.app import get_agent
        uid = str(update.effective_user.id)
        text = update.message.text

        msg = ChatMessage(content=text, source="telegram", user_id=uid)
        resp = await get_agent().chat(msg)

        content = resp.content
        # Telegram 4096 char limit — split if needed
        if len(content) <= 4000:
            await update.message.reply_text(content)
        else:
            for i in range(0, len(content), 4000):
                await update.message.reply_text(content[i:i + 4000])

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("skills", cmd_skills))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    @router.post("/webhook")
    async def telegram_webhook(request: Request):
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}

    return router
