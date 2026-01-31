"""
Client for enhancing prompts using AI models.
"""
import json
import logging
from typing import Optional, Dict, List
import httpx

from chatlist.config.settings import config
from chatlist.core.enhance_result import EnhanceResult

logger = logging.getLogger(__name__)


class PromptEnhancerClient:
    """Client for sending prompts to AI models for enhancement."""

    # System prompts for different enhancement types
    SYSTEM_PROMPTS = {
        'general': """Ты - эксперт по написанию промтов для AI моделей. Твоя задача улучшить следующий промт.

Требования:
1. Улучши четкость и структуру промта
2. Добавь специфические детали и контекст
3. Оптимизируй формулировки для лучшего понимания моделью
4. Предложи 2-3 альтернативных варианта переформулировки
5. Объясни, какие изменения были сделаны и почему
6. Дай рекомендации по адаптации этого промта для разных типов задач

ВАЖНО: Ответь ТОЛЬКО в формате JSON (без Markdown блоков):
{"enhanced": "...", "alternatives": ["...", "...", "..."], "explanation": "...", "recommendations": {"code": "...", "analysis": "...", "creative": "..."}}""",

        'code': """Ты - эксперт по написанию промтов для задач программирования. Твоя задача улучшить следующий промт, специализируясь на задачах кодирования.

Требования:
1. Убедись, что промт ясно описывает требования к коду
2. Добавь спецификацию языка программирования если нужно
3. Включи примеры формата ввода/вывода если применимо
4. Предложи 2-3 альтернативных варианта
5. Объясни изменения
6. Дай рекомендации для разных типов задач

ВАЖНО: Ответь ТОЛЬКО в формате JSON (без Markdown блоков):
{"enhanced": "...", "alternatives": ["...", "...", "..."], "explanation": "...", "recommendations": {"code": "...", "analysis": "...", "creative": "..."}}""",

        'analysis': """Ты - эксперт по написанию промтов для аналитических и исследовательских задач. Улучши промт для задач анализа.

Требования:
1. Уточни цель анализа и желаемые результаты
2. Добавь контекст и предпосылки если нужно
3. Укажи формат презентации результатов
4. Предложи 2-3 альтернативных варианта
5. Объясни улучшения
6. Дай рекомендации

ВАЖНО: Ответь ТОЛЬКО в формате JSON (без Markdown блоков):
{"enhanced": "...", "alternatives": ["...", "...", "..."], "explanation": "...", "recommendations": {"code": "...", "analysis": "...", "creative": "..."}}""",

        'creative': """Ты - эксперт по написанию промтов для творческих задач. Улучши промт для творческой работы.

Требования:
1. Расширь описание тона и стиля
2. Добавь примеры желаемого стиля или тона
3. Уточни целевую аудиторию и контекст
4. Предложи 2-3 альтернативных варианта
5. Объясни изменения
6. Дай рекомендации

ВАЖНО: Ответь ТОЛЬКО в формате JSON (без Markdown блоков):
{"enhanced": "...", "alternatives": ["...", "...", "..."], "explanation": "...", "recommendations": {"code": "...", "analysis": "...", "creative": "..."}}""",
    }

    def __init__(self):
        """Initialize the prompt enhancer client."""
        self.timeout = config.request_timeout
        self.openrouter_api_key = config.openrouter_api_key

    def enhance_prompt(
        self,
        prompt: str,
        model_id: int,
        enhancement_type: str = 'general',
        api_url: str = 'https://openrouter.ai/api/v1/chat/completions'
    ) -> Optional[EnhanceResult]:
        """
        Enhance a prompt using an AI model.

        Args:
            prompt: The original prompt to enhance
            model_id: ID of the model to use for enhancement
            enhancement_type: Type of enhancement (general, code, analysis, creative)
            api_url: API endpoint URL

        Returns:
            EnhanceResult with enhanced prompt and alternatives, or None on error
        """
        try:
            # Validate inputs
            if not prompt or len(prompt.strip()) < 10:
                logger.error("Prompt is too short (minimum 10 characters)")
                return None

            if len(prompt) > 10000:
                logger.error("Prompt is too long (maximum 10000 characters)")
                return None

            if enhancement_type not in self.SYSTEM_PROMPTS:
                logger.warning(f"Unknown enhancement type: {enhancement_type}, using 'general'")
                enhancement_type = 'general'

            system_prompt = self.SYSTEM_PROMPTS[enhancement_type]

            # Send request to API
            response = self._send_request(
                prompt=prompt,
                system_prompt=system_prompt,
                api_url=api_url
            )

            if not response:
                return None

            # Parse the response
            result = self._parse_response(
                response=response,
                original_prompt=prompt,
                model_id=model_id,
                enhancement_type=enhancement_type
            )

            return result

        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return None

    def _send_request(
        self,
        prompt: str,
        system_prompt: str,
        api_url: str
    ) -> Optional[str]:
        """
        Send request to AI model API.

        Args:
            prompt: User prompt to enhance
            system_prompt: System prompt with instructions
            api_url: API endpoint

        Returns:
            Response text or None on error
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'model': 'openai/gpt-4o-mini',  # Use a capable model for enhancement
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': f'Улучши этот промт:\n\n{prompt}'
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000,
            }

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(api_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']

            logger.error("Unexpected API response format")
            return None

        except httpx.TimeoutException:
            logger.error("Request timeout while enhancing prompt")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while enhancing prompt: {e}")
            return None
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return None

    def _parse_response(
        self,
        response: str,
        original_prompt: str,
        model_id: int,
        enhancement_type: str
    ) -> Optional[EnhanceResult]:
        """
        Parse AI response and extract enhancement data.

        Args:
            response: Raw API response text
            original_prompt: Original prompt
            model_id: Model ID used
            enhancement_type: Enhancement type

        Returns:
            EnhanceResult object or None on parse error
        """
        try:
            # Try to extract JSON from response
            # Sometimes the model might wrap it in markdown code blocks
            json_text = response.strip()
            if json_text.startswith('```'):
                # Remove markdown code block markers
                json_text = json_text.replace('```json\n', '').replace('```', '')

            # Parse JSON
            data = json.loads(json_text)

            # Validate required fields
            if not all(key in data for key in ['enhanced', 'alternatives', 'explanation', 'recommendations']):
                logger.error("Response missing required fields")
                return None

            # Ensure alternatives is a list
            alternatives = data.get('alternatives', [])
            if not isinstance(alternatives, list):
                alternatives = [alternatives]

            # Ensure we have 2-3 alternatives
            alternatives = alternatives[:3]

            return EnhanceResult(
                original_prompt=original_prompt,
                enhanced_prompt=data['enhanced'],
                alternatives=alternatives,
                explanation=data['explanation'],
                recommendations=data.get('recommendations', {}),
                model_id=model_id,
                enhancement_type=enhancement_type,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None
