from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db          # ← CHANGED
from models.transaction import Transaction
from models.fraud_log import FraudLog
from services.currency_service import CurrencyService
from services.fraud_detection import FraudDetectionService
from services.payment_service import PaymentService

payment_bp = Blueprint('payment', __name__)
currency_service = CurrencyService()
fraud_service = FraudDetectionService()
payment_service = PaymentService()


@payment_bp.route('/identify-currency', methods=['POST'])
@jwt_required()
def identify_currency():
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please point the camera at the currency.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()
    result = currency_service.identify_currency(image_data)
    return jsonify(result), 200


@payment_bp.route('/verify-amount', methods=['POST'])
@jwt_required()
def verify_amount():
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please show me the money to verify.'
        }), 400

    expected = request.form.get('expected_amount')
    currency = request.form.get('currency', 'INR')

    if not expected:
        return jsonify({
            'error': 'Expected amount required',
            'audio_message': 'Please tell me how much money you should have received.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()
    result = currency_service.verify_amount(image_data, float(expected), currency)

    if not result.get('is_correct', True):
        user_id = get_jwt_identity()
        fraud_log = FraudLog(
            user_id=int(user_id),
            detection_type='short_change',
            currency=currency,
            expected_amount=float(expected),
            detected_amount=result.get('detected_amount', 0),
            confidence_score=0.8,
            description=result.get('audio_message', ''),
            is_fraud=True,
            action_taken='User alerted via audio'
        )
        db.session.add(fraud_log)
        db.session.commit()

    return jsonify(result), 200


@payment_bp.route('/check-note', methods=['POST'])
@jwt_required()
def check_note():
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please show me the note to check.'
        }), 400

    claimed = request.form.get('claimed_denomination')
    currency = request.form.get('currency', 'INR')

    image_file = request.files['image']
    image_data = image_file.read()

    result = fraud_service.check_note_authenticity(
        image_data,
        claimed_denomination=int(claimed) if claimed else None,
        currency=currency
    )

    user_id = get_jwt_identity()
    is_fraud = not result.get('is_likely_genuine', True)

    fraud_log = FraudLog(
        user_id=int(user_id),
        detection_type='fake_note' if is_fraud else 'note_check',
        currency=currency,
        expected_amount=int(claimed) if claimed else None,
        detected_amount=result.get('actual_denomination'),
        confidence_score=result.get('authenticity_score', 0),
        description=result.get('audio_message', ''),
        is_fraud=is_fraud,
        action_taken='User alerted' if is_fraud else 'Verified genuine'
    )
    db.session.add(fraud_log)
    db.session.commit()

    return jsonify(result), 200


@payment_bp.route('/check-upi', methods=['POST'])
@jwt_required()
def check_upi():
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 'UPI data required',
            'audio_message': 'Please provide the payment details.'
        }), 400

    result = fraud_service.check_upi_request(data)

    if result.get('is_suspicious', False):
        user_id = get_jwt_identity()
        fraud_log = FraudLog(
            user_id=int(user_id),
            detection_type='suspicious_upi',
            expected_amount=data.get('amount', 0),
            confidence_score=result.get('risk_score', 0),
            description=result.get('audio_message', ''),
            is_fraud=True,
            action_taken='Payment blocked'
        )
        db.session.add(fraud_log)
        db.session.commit()

    return jsonify(result), 200


@payment_bp.route('/read-qr', methods=['POST'])
@jwt_required()
def read_qr():
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please point the camera at the QR code.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()
    result = payment_service.read_qr_code(image_data)
    return jsonify(result), 200


@payment_bp.route('/verify-change', methods=['POST'])
@jwt_required()
def verify_change():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    paid = request.form.get('paid_amount')
    cost = request.form.get('item_cost')
    currency = request.form.get('currency', 'INR')

    if not paid or not cost:
        return jsonify({
            'error': 'paid_amount and item_cost required',
            'audio_message': 'Tell me how much you paid and what the item cost.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()
    result = fraud_service.verify_change(float(paid), float(cost), image_data, currency)
    return jsonify(result), 200


@payment_bp.route('/guide-payment', methods=['POST'])
@jwt_required()
def guide_payment():
    data = request.get_json()
    step = data.get('step', 1) if data else 1
    context = data.get('context', {}) if data else {}
    result = payment_service.guide_upi_payment(step, context)
    return jsonify(result), 200


@payment_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=int(user_id)) \
        .order_by(Transaction.created_at.desc()).limit(10).all()
    txn_list = [t.to_dict() for t in transactions]
    result = payment_service.format_transaction_history(txn_list)
    return jsonify(result), 200


@payment_bp.route('/fraud-history', methods=['GET'])
@jwt_required()
def get_fraud_history():
    user_id = get_jwt_identity()
    logs = FraudLog.query.filter_by(user_id=int(user_id)) \
        .order_by(FraudLog.created_at.desc()).limit(10).all()
    log_list = [l.to_dict() for l in logs]
    fraud_count = sum(1 for l in log_list if l.get('is_fraud'))

    audio = f"You have {len(log_list)} recent security checks. "
    if fraud_count:
        audio += f"{fraud_count} suspicious activities were detected."
    else:
        audio += "No fraud was detected."

    return jsonify({
        'fraud_logs': log_list,
        'total_checks': len(log_list),
        'fraud_detected': fraud_count,
        'audio_message': audio
    }), 200