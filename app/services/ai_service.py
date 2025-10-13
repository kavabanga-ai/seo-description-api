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
        # Maximum characters for keywords to avoid truncation
        self.max_keywords_length = 2000

    def _format_keywords(self, keywords: list) -> tuple[str, int]:
        """
        Format keywords optimally and return formatted string with count.
        Returns: (formatted_string, actual_keyword_count)
        """
        if not keywords:
            return "", 0

        # Remove duplicates and empty strings
        keywords = [k.strip() for k in keywords if k and k.strip()]
        keywords = list(dict.fromkeys(keywords))  # Remove duplicates while preserving order

        actual_count = len(keywords)
        logger.info(f"Processing {actual_count} unique keywords (after deduplication)")

        # Try different formatting approaches
        # Approach 1: Numbered list (most readable)
        keywords_numbered = "\n".join([f"{i + 1}. {kw}" for i, kw in enumerate(keywords)])

        # Approach 2: Comma-separated (compact)
        keywords_comma = ", ".join(keywords)

        # Approach 3: Bullet points
        keywords_bullets = "\n- " + "\n- ".join(keywords)

        # Choose format based on length
        if len(keywords_comma) < self.max_keywords_length:
            # If comma-separated fits, use it (most compact)
            formatted = f"Keywords: {keywords_comma}"
            logger.info(f"Using comma-separated format ({len(keywords_comma)} chars)")
        elif len(keywords_bullets) < self.max_keywords_length * 1.5:
            # Use bullets if it fits with some margin
            formatted = f"Keywords:{keywords_bullets}"
            logger.info(f"Using bullet-point format ({len(keywords_bullets)} chars)")
        else:
            # Use numbered list for very large sets
            formatted = f"Keywords:\n{keywords_numbered}"
            logger.info(f"Using numbered format ({len(keywords_numbered)} chars)")

        return formatted, actual_count

    async def generate_description(
            self, product_id: str, keywords: list, basic_info: str = None
    ) -> Dict[str, Any]:
        """Generate SEO description using Dify AI"""
        try:
            # Log original keyword count
            original_count = len(keywords) if keywords else 0
            logger.info(f"[{product_id}] === KEYWORD PROCESSING START ===")
            logger.info(f"[{product_id}] Received {original_count} keywords from database")

            # Format keywords and get actual count
            keywords_formatted, actual_count = self._format_keywords(keywords)

            if original_count != actual_count:
                logger.warning(
                    f"[{product_id}] Keyword count changed from {original_count} to {actual_count} "
                    f"(duplicates or empty strings removed)"
                )

            # Log first few keywords for verification
            if keywords and len(keywords) > 0:
                preview = keywords[:5]
                logger.info(f"[{product_id}] First 5 keywords: {preview}")
                if len(keywords) > 5:
                    logger.info(f"[{product_id}] Last 5 keywords: {keywords[-5:]}")

            logger.info(f"[{product_id}] Formatted keywords length: {len(keywords_formatted)} characters")

            # Build the prompt
            prompt_parts = [
                "Generate an SEO-optimized product description for:",
                "",
                keywords_formatted,
                "",
            ]

            if basic_info:
                prompt_parts.append(f"Basic Info: {basic_info}")
                prompt_parts.append("")

            prompt_parts.extend([
                "Please provide:",
                "1. A compelling product description with perfect matched and trending keywords",
                "2. After the description, add \"Характеристики:\" on a new line",
                "3. Below \"Характеристики:\" provide key specifications as bullet points",
                "Make it SEO-friendly and engaging and must be in Russian Language"
            ])

            prompt = "\n".join(prompt_parts)

            # Log prompt details
            logger.info(f"[{product_id}] Full prompt length: {len(prompt)} characters")
            logger.info(f"[{product_id}] Prompt preview (first 500 chars):\n{prompt[:500]}...")

            # Prepare request payload
            request_payload = {
                "inputs": {},
                "query": prompt,
                "response_mode": "blocking",
                "user": f"api-{product_id}",
                "conversation_id": "",
            }

            # Log payload info
            import json as json_module
            payload_json = json_module.dumps(request_payload, ensure_ascii=False)
            payload_size = len(payload_json.encode('utf-8'))
            logger.info(f"[{product_id}] Request payload size: {payload_size} bytes ({payload_size / 1024:.2f} KB)")

            # Check if payload might be too large
            if payload_size > 50000:  # 50KB warning threshold
                logger.warning(f"[{product_id}] Large payload detected: {payload_size / 1024:.2f} KB")

            logger.info(f"[{product_id}] === SENDING TO DIFY API ===")

            # Increased timeout to 120 seconds (2 minutes)
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat-messages",
                    headers=self.headers,
                    json=request_payload,
                )

                logger.info(f"[{product_id}] Dify API response status: {response.status_code}")
                logger.info(f"[{product_id}] Response size: {len(response.content)} bytes")

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")

                    logger.info(f"[{product_id}] Received answer length: {len(answer)} characters")
                    logger.info(f"[{product_id}] Answer preview (first 200 chars): {answer[:200]}...")

                    # Parse the answer splitting by "Характеристики:"
                    description = answer
                    specifications = ""

                    if "Характеристики:" in answer:
                        parts = answer.split("Характеристики:", 1)
                        description = parts[0].strip()
                        specifications = parts[1].strip() if len(parts) > 1 else ""
                        logger.info(
                            f"[{product_id}] Split into description ({len(description)} chars) and specifications ({len(specifications)} chars)")
                    elif "Характеристики" in answer:
                        # Handle case without colon
                        parts = answer.split("Характеристики", 1)
                        description = parts[0].strip()
                        specifications = parts[1].strip() if len(parts) > 1 else ""
                        logger.info(
                            f"[{product_id}] Split into description ({len(description)} chars) and specifications ({len(specifications)} chars)")
                    else:
                        logger.warning(f"[{product_id}] No 'Характеристики' marker found in response")

                    logger.info(f"[{product_id}] === GENERATION SUCCESSFUL ===")

                    return {
                        "success": True,
                        "description": description,
                        "specifications": specifications,
                        "metadata": {
                            "keywords_sent": actual_count,
                            "keywords_original": original_count,
                        }
                    }
                else:
                    error_text = response.text[:500]  # Log first 500 chars of error
                    logger.error(
                        f"[{product_id}] AI API error: {response.status_code} - {error_text}"
                    )
                    return {
                        "success": False,
                        "error": f"AI service returned {response.status_code}",
                    }

        except httpx.TimeoutException:
            logger.warning(
                f"[{product_id}] Timeout generating description (exceeded 120s), will retry"
            )
            return {"success": False, "error": "timeout", "retry": True}
        except Exception as e:
            logger.error(f"[{product_id}] Error generating description: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


ai_service = DifyAIService()
