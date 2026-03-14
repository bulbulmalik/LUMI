import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Assists visually impaired users with payments:
    - UPI payment guidance (step by step voice instructions)
    - QR code reading and verification
    - Payment confirmation and logging
    - Transaction history in audio format
    """

    def __init__(self):
        pass

    def read_qr_code(self, image_data: bytes) -> dict:
        """
        Read and parse a QR code from an image.
        """
        try:
            # Try pyzbar first
            from pyzbar import pyzbar
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_data))
            decoded = pyzbar.decode(image)

            if not decoded:
                return {
                    'success': False,
                    'audio_message': 'No QR code detected. Please point the camera directly at the QR code.'
                }

            qr_data = decoded[0].data.decode('utf-8')
            parsed = self._parse_upi_qr(qr_data)

            if parsed:
                audio = (
                    f"QR code detected. "
                    f"Payment to {parsed.get('payee_name', 'unknown')}. "
                    f"UPI ID: {parsed.get('upi_id', 'unknown')}."
                )
                if parsed.get('amount'):
                    audio += f" Amount: {parsed['amount']} rupees."
                audio += " Shall I proceed with this payment?"

                return {
                    'success': True,
                    'qr_data': qr_data,
                    'parsed': parsed,
                    'audio_message': audio,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': True,
                    'qr_data': qr_data,
                    'parsed': None,
                    'audio_message': f'QR code reads: {qr_data[:100]}. This does not appear to be a payment QR code.'
                }

        except ImportError:
            logger.warning("pyzbar not installed, trying OpenCV")
            return self._read_qr_opencv(image_data)

        except Exception as e:
            logger.error(f"QR reading failed: {e}")
            return {
                'success': False,
                'audio_message': 'Sorry, I could not read the QR code. Please try again.',
                'error': str(e)
            }

    def _read_qr_opencv(self, image_data: bytes) -> dict:
        """Fallback QR reader using OpenCV."""
        try:
            import cv2
            import numpy as np

            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(image)

            if data:
                parsed = self._parse_upi_qr(data)
                if parsed:
                    audio = (
                        f"QR code detected. Payment to {parsed.get('payee_name', 'unknown')}. "
                        f"UPI ID: {parsed.get('upi_id', 'unknown')}."
                    )
                    if parsed.get('amount'):
                        audio += f" Amount: {parsed['amount']} rupees."
                    return {
                        'success': True,
                        'qr_data': data,
                        'parsed': parsed,
                        'audio_message': audio
                    }
                return {
                    'success': True,
                    'qr_data': data,
                    'audio_message': f'QR code reads: {data[:100]}'
                }
            return {
                'success': False,
                'audio_message': 'No QR code found. Please try pointing the camera directly at the code.'
            }

        except Exception as e:
            logger.error(f"OpenCV QR reading failed: {e}")
            return {
                'success': False,
                'audio_message': 'QR code reading is not available right now.'
            }

    def _parse_upi_qr(self, qr_data: str) -> dict:
        """Parse UPI QR code data (upi://pay?...)."""
        if not qr_data.startswith('upi://'):
            return None

        parsed = {}
        try:
            # Remove 'upi://pay?'
            params_str = qr_data.split('?', 1)[1] if '?' in qr_data else ''
            params = dict(p.split('=', 1) for p in params_str.split('&') if '=' in p)

            parsed['upi_id'] = params.get('pa', '')
            parsed['payee_name'] = params.get('pn', '').replace('%20', ' ')
            parsed['amount'] = params.get('am', None)
            parsed['transaction_note'] = params.get('tn', '').replace('%20', ' ')
            parsed['currency'] = params.get('cu', 'INR')
            parsed['merchant_code'] = params.get('mc', '')

            if parsed['amount']:
                parsed['amount'] = float(parsed['amount'])

        except Exception as e:
            logger.error(f"UPI QR parsing error: {e}")
            return None

        return parsed

    def guide_upi_payment(self, step: int, context: dict = None) -> dict:
        """
        Provide step-by-step voice guidance for making a UPI payment.
        """
        steps = {
            1: {
                'instruction': (
                    "Step 1: Open your UPI payment app. "
                    "I'll guide you through the payment process. "
                    "Tell me when the app is open."
                ),
                'action': 'open_app'
            },
            2: {
                'instruction': (
                    "Step 2: Now tap on 'Pay' or 'Send Money' button. "
                    "It's usually at the center bottom or top of the screen. "
                    "Or you can scan a QR code if available."
                ),
                'action': 'navigate_to_pay'
            },
            3: {
                'instruction': (
                    "Step 3: Enter the UPI ID or phone number of the person you want to pay. "
                    "Tell me the details and I'll verify them for you."
                ),
                'action': 'enter_details'
            },
            4: {
                'instruction': (
                    "Step 4: Enter the amount you want to pay. "
                    "Tell me the amount and I'll confirm."
                ),
                'action': 'enter_amount'
            },
            5: {
                'instruction': (
                    "Step 5: Review the payment details. "
                    "I'll read them out to you for verification. "
                    "Point your camera at the screen."
                ),
                'action': 'review'
            },
            6: {
                'instruction': (
                    "Step 6: Enter your UPI PIN to confirm the payment. "
                    "This is your secret PIN. Make sure no one is watching. "
                    "I will look away — I cannot and will not see your PIN."
                ),
                'action': 'enter_pin'
            },
            7: {
                'instruction': (
                    "Payment submitted! Point your camera at the screen "
                    "so I can confirm whether it was successful."
                ),
                'action': 'confirm'
            }
        }

        step_data = steps.get(step, {
            'instruction': 'Payment process complete. Let me know if you need anything else.',
            'action': 'complete'
        })

        return {
            'step': step,
            'total_steps': 7,
            **step_data,
            'audio_message': step_data['instruction']
        }

    def format_transaction_history(self, transactions: list) -> dict:
        """
        Format transaction history as audio-friendly text.
        """
        if not transactions:
            return {
                'audio_message': 'You have no recent transactions.',
                'transactions': []
            }

        audio_parts = [f"You have {len(transactions)} recent transactions. "]

        for i, txn in enumerate(transactions[:5], 1):  # Read last 5
            t_type = txn.get('transaction_type', 'payment')
            amount = txn.get('amount', 0)
            currency = txn.get('currency', 'INR')
            recipient = txn.get('recipient', 'unknown')
            status = txn.get('status', 'unknown')
            date = txn.get('created_at', '')

            audio_parts.append(
                f"Transaction {i}: {t_type} of {amount} {currency} "
                f"to {recipient}, status: {status}. "
            )

        return {
            'audio_message': ' '.join(audio_parts),
            'count': len(transactions),
            'transactions': transactions[:5]
        }