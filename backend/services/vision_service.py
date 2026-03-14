import base64
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class VisionService:
    """
    Analyzes camera frames for:
    - Object detection & identification
    - Scene description
    - Text reading (OCR)
    - Obstacle detection
    - Face recognition (known contacts)
    """

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')

    def analyze_frame(self, image_data: bytes, context: str = 'general') -> dict:
        """
        Analyze a camera frame and return description for audio feedback.

        Args:
            image_data: Raw image bytes (JPEG/PNG)
            context: 'general', 'navigation', 'reading', 'currency', 'face'

        Returns:
            dict with 'description', 'objects', 'warnings', 'audio_message'
        """
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            prompt = self._get_context_prompt(context)

            # Using OpenAI GPT-4 Vision
            if self.api_key:
                return self._analyze_with_openai(base64_image, prompt, context)

            # Using Anthropic Claude Vision
            if self.anthropic_key:
                return self._analyze_with_anthropic(base64_image, prompt, context)

            # Fallback: basic analysis description
            return self._fallback_analysis(context)

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                'description': 'Unable to analyze the image at this moment.',
                'objects': [],
                'warnings': [],
                'audio_message': 'Sorry, I could not analyze what the camera sees right now. Please try again.'
            }

    def _get_context_prompt(self, context: str) -> str:
        prompts = {
            'general': (
                "You are LUMI, an AI assistant helping a visually impaired person. "
                "Describe what you see in this image clearly and concisely. "
                "Mention: people (count, approximate distance, what they're doing), "
                "objects, text/signs, potential hazards, and the general environment. "
                "Keep it under 3 sentences for quick audio playback. "
                "Prioritize safety-critical information first."
            ),
            'navigation': (
                "You are LUMI, a friendly AI guide for visually impaired navigation and general assistance. "
                "Describe what you see in the image clearly and helpfully. "
                "Focus on: objects in view (especially if asked about hands or specific items), obstacles, people, environment. "
                "Start with 'Hey,' and be conversational. "
                "For questions like 'what is in my hand', describe the object accurately. "
                "Keep it brief for audio."
            ),
            'reading': (
                "You are LUMI, helping a visually impaired person read text accurately. "
                "Extract and read ALL visible text from the image precisely, including any printed or handwritten text. "
                "Describe the layout if it's a page or document. "
                "Read it in order, as it appears. "
                "If it's a screen or display, describe the interface and read all text content. "
                "Be completely accurate - do not summarize or omit text. "
                "Start with 'Hey,' and speak clearly."
            ),
            'currency': (
                "You are LUMI helping identify currency/money. "
                "Identify: denomination, currency type (INR/USD/EUR/GBP), "
                "count of notes if multiple are visible, total amount. "
                "Check for signs of counterfeit: color inconsistencies, "
                "missing security features, blurriness in security thread area. "
                "Report clearly: 'I see two 500 rupee notes, total 1000 rupees. "
                "They appear genuine.'"
            ),
            'face': (
                "You are LUMI. Describe the people visible in this image: "
                "approximate age, gender, expression, what they're wearing, "
                "and approximately how far they are. "
                "Do NOT try to identify specific individuals by name."
            )
        }
        return prompts.get(context, prompts['general'])

    def _analyze_with_openai(self, base64_image: str, prompt: str, context: str) -> dict:
        """Use OpenAI GPT-4 Vision API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"  # faster for real-time
                                }
                            },
                            {
                                "type": "text",
                                "text": "Describe what you see. Be concise and helpful."
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )

            description = response.choices[0].message.content

            return {
                'description': description,
                'objects': self._extract_objects(description),
                'warnings': self._extract_warnings(description),
                'audio_message': description,
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            raise

    def _analyze_with_anthropic(self, base64_image: str, prompt: str, context: str) -> dict:
        """Use Anthropic Claude Vision API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
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
                            {
                                "type": "text",
                                "text": prompt + "\n\nDescribe what you see. Be concise and helpful."
                            }
                        ]
                    }
                ]
            )

            description = response.content[0].text

            return {
                'description': description,
                'objects': self._extract_objects(description),
                'warnings': self._extract_warnings(description),
                'audio_message': description,
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Anthropic Vision API error: {e}")
            raise

    def _extract_objects(self, description: str) -> list:
        """Extract mentioned objects from description text."""
        common_objects = [
            'person', 'people', 'car', 'vehicle', 'door', 'stairs', 'chair',
            'table', 'phone', 'sign', 'tree', 'building', 'road', 'sidewalk',
            'wall', 'window', 'bus', 'bicycle', 'dog', 'cat', 'bag', 'bottle',
            'curb', 'pole', 'traffic light', 'crosswalk', 'elevator', 'ramp'
        ]
        description_lower = description.lower()
        found = [obj for obj in common_objects if obj in description_lower]
        return found

    def _extract_warnings(self, description: str) -> list:
        """Extract safety warnings from description."""
        warning_keywords = [
            'careful', 'caution', 'warning', 'danger', 'obstacle', 'stairs',
            'step', 'hole', 'wet', 'slippery', 'vehicle approaching', 'traffic',
            'curb', 'drop', 'edge', 'construction', 'blocked'
        ]
        description_lower = description.lower()
        warnings = [w for w in warning_keywords if w in description_lower]
        return warnings

    def _fallback_analysis(self, context: str) -> dict:
        return {
            'description': 'Vision API not configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.',
            'objects': [],
            'warnings': [],
            'audio_message': 'Vision service is not configured. Please contact support.',
            'context': context
        }

    def read_text_from_image(self, image_data: bytes) -> dict:
        """Specialized OCR function for reading text."""
        return self.analyze_frame(image_data, context='reading')

    def detect_currency(self, image_data: bytes) -> dict:
        """Specialized function for currency identification."""
        return self.analyze_frame(image_data, context='currency')