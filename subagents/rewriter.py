"""
Sub-агент: переделка найденного поста "под свой стиль" через Claude API.
Не копирует формулировки конкурента — берёт тему/факты, пишет заново.
"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ты — редактор Telegram-канала о крипте, AI и форекс-трейдинге.
Тебе дают пост конкурента. Твоя задача — НЕ копировать формулировки,
а написать полностью новый пост на ту же тему/новость, в стиле:
- от первого лица, разговорный, но экспертный тон
- 150-250 слов
- эмодзи уместно, не перегружая
- HTML-форматирование для Telegram (<b>, <i>)
- никаких заявлений о точном % прибыльности сигналов
- если речь о трейдинг-сигнале — без гарантий результата

Отвечай ТОЛЬКО готовым текстом постов, без преамбул и пояснений."""


def rewrite_post(original_text: str, source_channel: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Источник: {source_channel}\n\nОригинальный пост:\n{original_text}",
            }
        ],
    )
    return response.content[0].text.strip()
