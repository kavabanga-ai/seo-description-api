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

    def _parse_features(self, features: list) -> str:
        """Parse features list into a readable format for the AI prompt"""
        if not features:
            return "No features provided"

        feature_lines = []
        for feature in features:
            label = feature.get("label", "")
            value = feature.get("value", "")
            if label and value:
                feature_lines.append(f"- {label}: {value}")

        return "\n".join(feature_lines) if feature_lines else "No features provided"

    async def generate_description(
        self, product_id: str, features: list, basic_info: str = None
    ) -> Dict[str, Any]:
        """Generate SEO description using Dify AI"""
        try:
            # Parse features into a readable format
            features_text = self._parse_features(features)

            # Prepare the prompt
            prompt = f"""Generate an SEO-optimized product description in Russian based on the following product features:

Product Features:
{features_text}

{f'Additional Info: {basic_info}' if basic_info else ''}

Please provide:
1. A compelling product description with SEO keywords based on the features
2. After the description, add "Характеристики:" on a new line
3. Below "Характеристики:" provide key specifications as bullet points based on the features
Make it SEO-friendly and engaging and must be in Russian Language"""

            # Increased timeout to 120 seconds (2 minutes)
            async with httpx.AsyncClient(timeout=120.0) as client:
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

                    # Parse the answer splitting by "Характеристики:"
                    description = answer
                    specifications = ""

                    if "Характеристики:" in answer:
                        parts = answer.split("Характеристики:", 1)
                        description = parts[0].strip()
                        specifications = parts[1].strip() if len(parts) > 1 else ""
                    elif "Характеристики" in answer:
                        # Handle case without colon
                        parts = answer.split("Характеристики", 1)
                        description = parts[0].strip()
                        specifications = parts[1].strip() if len(parts) > 1 else ""

                    return {
                        "success": True,
                        "description": description,
                        "specifications": specifications,
                    }
                else:
                    logger.error(
                        f"AI API error: {response.status_code} - {response.text}"
                    )
                    return {
                        "success": False,
                        "error": f"AI service returned {response.status_code}",
                    }

        except httpx.TimeoutException:
            logger.warning(
                f"Timeout generating description for {product_id}, will retry"
            )
            return {"success": False, "error": "timeout", "retry": True}
        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            return {"success": False, "error": str(e)}


ai_service = DifyAIService()
