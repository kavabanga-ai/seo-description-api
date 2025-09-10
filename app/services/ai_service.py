import logging
from typing import Any, Dict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DifyAIService:
    def __init__(self):
        self.base_url = settings.DIFY_API_URL
        self.api_key = settings.DIFY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_description(
        self, product_id: str, keywords: list, basic_info: str = None
    ) -> Dict[str, Any]:
        """Generate SEO description using Dify AI"""
        try:
            # Prepare the prompt
            keywords_str = ", ".join(keywords)
            prompt = f"""Generate an SEO-optimized product description for:
Keywords: {keywords_str}
{f'Basic Info: {basic_info}' if basic_info else ''}

Please provide:
1. A compelling product description with perfect matched and trending keywords
2. Key features as bullet points
Make it SEO-friendly and engaging and must be in Russian Language"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat-messages",
                    headers=self.headers,
                    json={
                        "inputs": {},
                        "query": prompt,
                        "response_mode": "blocking",
                        "user": f"api-{product_id}",
                        "conversation_id": "",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")

                    # Parse the answer to extract description and features
                    parts = answer.split("\n\n")
                    description = parts[0] if parts else answer
                    features = "\n".join(parts[1:]) if len(parts) > 1 else ""

                    return {
                        "success": True,
                        "description": description,
                        "features": features,
                    }
                else:
                    logger.error(
                        f"AI API error: {response.status_code} - {response.text}"
                    )
                    return {
                        "success": False,
                        "error": f"AI service returned {response.status_code}",
                    }

        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            return {"success": False, "error": str(e)}


ai_service = DifyAIService()
