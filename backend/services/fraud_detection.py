import base64
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Detects various types of fraud:
    - Counterfeit currency notes
    - Wrong denomination (someone claims ₹500 but gives ₹100)
    - Short-changing (wrong change given)
    - Suspicious UPI / online payment requests
    - Phishing attempt detection
    """

    # Known suspicious UPI patterns
    SUSPICIOUS_UPI_PATTERNS = [
        'lottery', 'prize', 'winner', 'reward', 'refund',
        'kyc', 'verify', 'urgent', 'block', 'suspend'
    ]

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')

    def check_note_authenticity(self, image_data: bytes, claimed_denomination: int = None,
                                 currency: str = 'INR') -> dict:
        """
        Check if a currency note appears authentic.

        Args:
            image_data: Image bytes of the note
            claimed_denomination: What the other person claims it is
            currency: Currency type

        Returns:
            dict with fraud analysis results and audio_message
        """
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            prompt = (
                f"You are a counterfeit currency detection expert helping a visually impaired person.\n"
                f"Analyze this {currency} currency note image carefully.\n\n"
                f"Check for:\n"
                f"1. Correct denomination identification - what denomination is this ACTUALLY?\n"
                f"2. Visual quality - does it look like a genuine note or a photocopy/print?\n"
                f"3. Color accuracy - does the color match genuine {currency} notes?\n"
                f"4. Security features visible - watermark area, security thread, micro-lettering\n"
                f"5. Print quality - any blurriness, misalignment, or poor print quality\n"
                f"6. Size and proportions - does it look the right size?\n\n"
            )

            if claimed_denomination:
                prompt += (
                    f"IMPORTANT: The person giving this note CLAIMS it is a {claimed_denomination} {currency} note. "
                    f"Verify if this is actually a {claimed_denomination} note or a different denomination.\n\n"
                )

            prompt += (
                "Return a JSON response with:\n"
                "- 'actual_denomination': the real denomination you detect\n"
                "- 'claimed_denomination': what was claimed (or null)\n"
                "- 'denomination_matches': boolean\n"
                "- 'authenticity_score': 0.0 to 1.0 (1.0 = definitely genuine)\n"
                "- 'is_likely_genuine': boolean\n"
                "- 'concerns': list of specific concerns\n"
                "- 'features_detected': list of security features visible\n"
                "- 'recommendation': what the user should do\n"
                "Return ONLY valid JSON."
            )

            if self.api_key:
                result = self._analyze_with_openai(base64_image, prompt)
            elif self.anthropic_key:
                result = self._analyze_with_anthropic(base64_image, prompt)
            else:
                return {
                    'audio_message': 'Fraud detection service is not configured.',
                    'is_likely_genuine': None
                }

            # Generate audio warning
            audio = self._generate_fraud_audio(result, claimed_denomination, currency)
            result['audio_message'] = audio
            result['timestamp'] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            logger.error(f"Fraud detection failed: {e}")
            return {
                'audio_message': 'Sorry, I could not check this note right now. Please try again.',
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                        },
                        {"type": "text", "text": "Analyze this currency note for authenticity."}
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
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
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}
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

    def _generate_fraud_audio(self, result: dict, claimed_denomination: int, currency: str) -> str:
        """Generate clear audio warning about potential fraud."""
        actual = result.get('actual_denomination')
        is_genuine = result.get('is_likely_genuine', True)
        score = result.get('authenticity_score', 1.0)
        concerns = result.get('concerns', [])
        recommendation = result.get('recommendation', '')

        parts = []

        # Check denomination mismatch
        if claimed_denomination and actual and actual != claimed_denomination:
            parts.append(
                f"ALERT! This note is actually a {actual} {currency} note, "
                f"but it was claimed to be {claimed_denomination} {currency}. "
                f"Someone may be trying to cheat you!"
            )
        elif actual:
            parts.append(f"This is a {actual} {currency} note.")

        # Check authenticity
        if not is_genuine:
            parts.append(
                f"WARNING! This note may be counterfeit! "
                f"Confidence in authenticity is only {int(score * 100)} percent."
            )
            if concerns:
                parts.append(f"Concerns: {'. '.join(concerns[:2])}")
        elif score < 0.7:
            parts.append(
                f"I have some concerns about this note. "
                f"It might be worth checking with someone you trust."
            )
        else:
            parts.append("The note appears to be genuine.")

        if recommendation:
            parts.append(recommendation)

        return " ".join(parts)

    def check_upi_request(self, upi_data: dict) -> dict:
        """
        Analyze a UPI payment request for potential fraud.

        Args:
            upi_data: {
                'payee_upi': str,
                'payee_name': str,
                'amount': float,
                'note': str,  # payment note/message
                'is_collect_request': bool
            }
        """
        warnings = []
        risk_score = 0.0
        is_suspicious = False

        payee_name = upi_data.get('payee_name', '').lower()
        note = upi_data.get('note', '').lower()
        amount = upi_data.get('amount', 0)
        is_collect = upi_data.get('is_collect_request', False)

        # Check 1: Suspicious keywords in payment note
        for pattern in self.SUSPICIOUS_UPI_PATTERNS:
            if pattern in note:
                warnings.append(f"Suspicious keyword '{pattern}' found in payment note.")
                risk_score += 0.3

        # Check 2: Collect requests are inherently riskier
        if is_collect:
            warnings.append("This is a collect request — someone is asking YOU for money.")
            risk_score += 0.2

        # Check 3: Unusually large amounts
        if amount > 10000:
            warnings.append(f"This is a large payment of {amount}. Please verify.")
            risk_score += 0.1
        if amount > 50000:
            risk_score += 0.2

        # Check 4: Name seems like a business impersonation
        impersonation_keywords = ['paytm', 'phonepe', 'gpay', 'amazon', 'flipkart',
                                   'bank', 'rbi', 'government', 'tax', 'income tax']
        for keyword in impersonation_keywords:
            if keyword in payee_name:
                warnings.append(
                    f"The payee name contains '{keyword}'. "
                    f"Official services don't usually send collect requests."
                )
                risk_score += 0.3

        risk_score = min(risk_score, 1.0)
        is_suspicious = risk_score > 0.4

        # Generate audio
        if is_suspicious:
            audio = (
                f"WARNING! This payment request looks suspicious. "
                f"Risk level is {int(risk_score * 100)} percent. "
                f"{' '.join(warnings[:2])} "
                f"I recommend NOT proceeding with this payment."
            )
        elif warnings:
            audio = (
                f"Payment of {amount} rupees to {upi_data.get('payee_name', 'unknown')}. "
                f"Some caution: {warnings[0]} "
                f"Please verify before proceeding."
            )
        else:
            audio = (
                f"Payment of {amount} rupees to {upi_data.get('payee_name', 'unknown')}. "
                f"No suspicious activity detected. You can proceed if this is correct."
            )

        return {
            'is_suspicious': is_suspicious,
            'risk_score': risk_score,
            'warnings': warnings,
            'audio_message': audio,
            'recommendation': 'DO NOT PAY' if is_suspicious else 'Verify and proceed',
            'timestamp': datetime.utcnow().isoformat()
        }

    def verify_change(self, paid_amount: float, item_cost: float,
                       change_image: bytes, currency: str = 'INR') -> dict:
        """
        Verify if correct change was given back.

        Args:
            paid_amount: Amount paid by the user
            item_cost: Cost of the item/service
            change_image: Image of the change received
        """
        from services.currency_service import CurrencyService
        currency_svc = CurrencyService()

        expected_change = paid_amount - item_cost
        result = currency_svc.identify_currency(change_image)
        received_change = result.get('total_amount', 0)

        difference = received_change - expected_change
        is_correct = abs(difference) < 1  # Allow ₹1 tolerance

        if is_correct:
            audio = (
                f"Change is correct. You paid {paid_amount}, "
                f"the item costs {item_cost}, and you received "
                f"{received_change} {currency} back."
            )
        elif difference < 0:
            audio = (
                f"ALERT! You were short-changed! "
                f"You should have received {expected_change} {currency}, "
                f"but you only got {received_change}. "
                f"You are missing {abs(difference)} {currency}."
            )
        else:
            audio = (
                f"You received {received_change} {currency} in change, "
                f"which is {difference} more than the expected {expected_change}."
            )

        return {
            'paid_amount': paid_amount,
            'item_cost': item_cost,
            'expected_change': expected_change,
            'received_change': received_change,
            'difference': difference,
            'is_correct': is_correct,
            'audio_message': audio,
            'currency_details': result,
            'timestamp': datetime.utcnow().isoformat()
        }