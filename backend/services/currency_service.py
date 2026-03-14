import base64
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class CurrencyService:
    """
    Identifies currency notes and coins:
    - Denomination detection (₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000)
    - Multiple note counting
    - Total amount calculation
    - Basic counterfeit indicators
    """

    # Indian currency denominations and their visual features
    INR_NOTES = {
        10: {'color': 'chocolate brown', 'size': 'smallest'},
        20: {'color': 'greenish yellow', 'size': 'small'},
        50: {'color': 'fluorescent blue', 'size': 'medium-small'},
        100: {'color': 'lavender', 'size': 'medium'},
        200: {'color': 'bright yellow', 'size': 'medium'},
        500: {'color': 'stone grey', 'size': 'large'},
        2000: {'color': 'magenta', 'size': 'largest'}
    }

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')

    def identify_currency(self, image_data: bytes) -> dict:
        """
        Identify currency notes in an image.

        Returns:
            dict with 'notes', 'total_amount', 'currency', 'audio_message'
        """
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            prompt = (
                "You are a currency identification assistant for visually impaired people. "
                "Analyze this image of currency notes/coins carefully.\n\n"
                "Return a JSON response with:\n"
                "- 'notes': list of objects with 'denomination' (number), 'currency' (ISO code like INR/USD), 'count' (how many of this denomination)\n"
                "- 'coins': list of objects with 'denomination' (number), 'currency' (ISO code), 'count'\n"
                "- 'total_amount': total value of all money visible\n"
                "- 'currency_type': primary currency detected (ISO code)\n"
                "- 'authenticity_concerns': list of any concerns about the notes (empty list if none)\n"
                "- 'description': brief human-readable description\n\n"
                "Be very precise about denominations. If unsure, mention it.\n"
                "Return ONLY valid JSON, no markdown."
            )

            if self.api_key:
                result = self._analyze_with_openai(base64_image, prompt)
            elif self.anthropic_key:
                result = self._analyze_with_anthropic(base64_image, prompt)
            else:
                return self._no_api_response()

            # Generate audio message
            audio_msg = self._generate_audio_message(result)
            result['audio_message'] = audio_msg
            result['timestamp'] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            logger.error(f"Currency identification failed: {e}")
            return {
                'notes': [],
                'total_amount': 0,
                'currency_type': 'unknown',
                'audio_message': 'Sorry, I could not identify the currency. Please try again with better lighting.',
                'error': str(e)
            }

    def _analyze_with_openai(self, base64_image: str, prompt: str) -> dict:
        import openai
        import json

        client = openai.OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        },
                        {"type": "text", "text": "Identify all currency in this image. Return JSON only."}
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]

        return json.loads(content)

    def _analyze_with_anthropic(self, base64_image: str, prompt: str) -> dict:
        import anthropic
        import json

        client = anthropic.Anthropic(api_key=self.anthropic_key)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )

        content = response.content[0].text.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]

        return json.loads(content)

    def _generate_audio_message(self, result: dict) -> str:
        """Generate a clear audio message about the currency."""
        notes = result.get('notes', [])
        coins = result.get('coins', [])
        total = result.get('total_amount', 0)
        currency = result.get('currency_type', 'INR')
        concerns = result.get('authenticity_concerns', [])

        if not notes and not coins:
            return "I don't see any currency in the image."

        # Build description
        parts = []

        if notes:
            note_descriptions = []
            for note in notes:
                count = note.get('count', 1)
                denom = note.get('denomination', '?')
                if count == 1:
                    note_descriptions.append(f"one {denom} {currency} note")
                else:
                    note_descriptions.append(f"{count} notes of {denom} {currency}")
            parts.append("I can see " + ", ".join(note_descriptions))

        if coins:
            coin_descriptions = []
            for coin in coins:
                count = coin.get('count', 1)
                denom = coin.get('denomination', '?')
                if count == 1:
                    coin_descriptions.append(f"one {denom} {currency} coin")
                else:
                    coin_descriptions.append(f"{count} coins of {denom} {currency}")
            parts.append("and " + ", ".join(coin_descriptions))

        parts.append(f"The total amount is {total} {currency}.")

        if concerns:
            parts.append(f"Warning: {'. '.join(concerns)}")

        return " ".join(parts)

    def verify_amount(self, image_data: bytes, expected_amount: float,
                      currency: str = 'INR') -> dict:
        """
        Verify if the cash amount matches an expected amount.
        Useful for detecting short-changing.
        """
        result = self.identify_currency(image_data)
        detected_amount = result.get('total_amount', 0)

        is_correct = abs(detected_amount - expected_amount) < 0.01
        difference = detected_amount - expected_amount

        if is_correct:
            audio = f"The amount is correct. You received {detected_amount} {currency} as expected."
        elif difference > 0:
            audio = f"You received {detected_amount} {currency}, which is {difference} more than the expected {expected_amount}."
        else:
            audio = (
                f"Warning! You received only {detected_amount} {currency}, "
                f"but you should have received {expected_amount}. "
                f"You are short by {abs(difference)} {currency}."
            )

        return {
            **result,
            'expected_amount': expected_amount,
            'detected_amount': detected_amount,
            'difference': difference,
            'is_correct': is_correct,
            'audio_message': audio
        }

    def _no_api_response(self):
        return {
            'notes': [],
            'total_amount': 0,
            'currency_type': 'unknown',
            'audio_message': 'Currency detection service is not configured. Please set up an API key.'
        }