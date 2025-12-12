"""
Ecocash USSD Push Payment Service
Handles mobile money payments via USSD push for subscription billing
"""
import os
import json
import requests
import logging
from datetime import datetime, timedelta
from flask import current_app
from app.models import Subscription, Invoice, Payment, PaymentMethod

logger = logging.getLogger(__name__)


class EcocashService:
    """Service for Ecocash USSD push payment processing"""
    
    def __init__(self):
        self.api_url = os.getenv('ECOCASH_API_URL', 'https://dt-externalproxy-1.etl.co.ls/etl/salesagentpay/paymerchant/')
        # This integration relies on the Ecocash endpoint's response
        # and does not require merchant credentials in the app.
        self.timeout = 30  # API request timeout in seconds
    
    def initiate_ussd_push(self, user, plan, phone_number, billing_interval='monthly'):
        """
        Initiate USSD push payment for subscription
        
        Args:
            user: User object
            plan: Plan object
            phone_number: User's mobile number (format: +263777123456 or 0777123456)
            billing_interval: 'monthly' or 'annual'
            
        Returns:
            dict: {
                'success': bool,
                'transaction_id': str (if success),
                'message': str,
                'ussd_code': str (USSD code user can dial if push fails),
                'amount': decimal,
                'reference': str
            }
        """
        try:
            # Get price
            if billing_interval == 'annual':
                amount = float(plan.annual_price)
            else:
                amount = float(plan.monthly_price)
            
            # Format phone number
            phone = self._format_phone_number(phone_number)
            
            # Create transaction reference
            reference = self._generate_reference(user.id, plan.id)
            
            # Prepare payload (simplified - Ecocash API spec)
            payload = {
                'msisdn': phone,
                'short_code': 36174,
                'amount': amount
            }
            
            # Call Ecocash API
            logger.info(f"Initiating Ecocash USSD push for user {user.id}, phone {phone}, amount {amount}")
            
            success, response_data = self._attempt_payment(phone, amount)
            
            if success:
                # Extract transaction ID from response
                if isinstance(response_data, dict):
                    transaction_id = (
                        response_data.get('transactionId') or 
                        response_data.get('transaction_id') or 
                        response_data.get('ref') or 
                        response_data.get('id') or 
                        reference
                    )
                else:
                    transaction_id = reference
                
                # Create pending subscription record
                subscription = self._create_pending_subscription(
                    user, plan, transaction_id, billing_interval, phone
                )
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'message': 'USSD push sent to your phone. Please confirm the payment.',
                    'ussd_code': '*151#',  # Standard Ecocash USSD code
                    'amount': amount,
                    'reference': reference
                }
            else:
                error_msg = 'Payment initiation failed'
                if isinstance(response_data, dict):
                    error_msg = response_data.get('message') or response_data.get('error') or error_msg
                else:
                    error_msg = str(response_data) if response_data else error_msg
                
                logger.warning(f"Ecocash payment failed: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'amount': amount,
                    'reference': reference
                }
        except Exception as e:
            logger.error(f"Ecocash payment initiation error: {str(e)}")
            return {
                'success': False,
                'message': f"Payment error: {str(e)}"
            }
    
    def verify_transaction(self, transaction_id):
        """
        Verify if Ecocash transaction was successful
        
        Args:
            transaction_id: Transaction ID from Ecocash
            
        Returns:
            dict: {
                'verified': bool,
                'status': str,
                'amount': decimal,
                'timestamp': str
            }
        """
        try:
            # Rely on the Ecocash API response; no merchant credentials required
            payload = {
                'transaction_id': transaction_id
            }

            response = requests.post(
                f"{self.api_url}verify/",
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'completed' or data.get('status') == 'success':
                return {
                    'verified': True,
                    'status': 'completed',
                    'amount': float(data.get('amount', 0)),
                    'timestamp': data.get('timestamp')
                }
            else:
                return {
                    'verified': False,
                    'status': data.get('status', 'pending'),
                    'amount': float(data.get('amount', 0)),
                    'timestamp': data.get('timestamp')
                }
        except Exception as e:
            logger.error(f"Transaction verification error: {str(e)}")
            return {
                'verified': False,
                'status': 'error',
                'error': str(e)
            }
    
    def handle_callback(self, callback_data):
        """
        Handle Ecocash payment callback/webhook
        
        Args:
            callback_data: JSON data from Ecocash webhook
            
        Returns:
            dict: {
                'processed': bool,
                'subscription_id': int (if successful),
                'message': str
            }
        """
        try:
            # Extract transaction data - handle various field name conventions
            transaction_id = (
                callback_data.get('transactionId') or 
                callback_data.get('transaction_id') or 
                callback_data.get('ref') or 
                callback_data.get('id')
            )
            
            status = (
                callback_data.get('status') or 
                callback_data.get('Status') or 
                callback_data.get('state')
            )
            
            amount = float(callback_data.get('amount', 0))
            
            if not transaction_id:
                logger.warning(f"No transaction ID in callback: {callback_data}")
                return {
                    'processed': False,
                    'message': 'Missing transaction ID'
                }
            
            # Find pending subscription by transaction ID
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=transaction_id,  # Using this field for ecocash transaction ID
                status='pending'
            ).first()
            
            if not subscription:
                logger.warning(f"No pending subscription found for transaction {transaction_id}")
                return {
                    'processed': False,
                    'message': 'Subscription not found'
                }
            
            # Normalize status check (handles various response formats)
            status_lower = str(status).lower() if status else ''
            is_success = 'success' in status_lower or 'completed' in status_lower or 'completed' in status_lower
            is_failed = 'fail' in status_lower or 'declined' in status_lower or 'error' in status_lower
            
            if is_success:
                # Payment successful - activate subscription
                subscription.status = 'active'
                subscription.current_period_start = datetime.utcnow()
                
                # Set renewal date
                if subscription.billing_interval == 'annual':
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=365)
                else:
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
                
                # Record payment
                payment = Payment(
                    subscription_id=subscription.id,
                    amount=amount,
                    currency='ZWL',
                    status='completed',
                    payment_method='ecocash',
                    external_transaction_id=transaction_id,
                    created_at=datetime.utcnow()
                )
                
                # Create invoice
                invoice = Invoice(
                    subscription_id=subscription.id,
                    amount_due=amount,
                    amount_paid=amount,
                    amount_remaining=0,
                    status='paid',
                    issued_date=datetime.utcnow(),
                    paid_date=datetime.utcnow(),
                    currency='ZWL',
                    lines=json.dumps([{
                        'description': f"{subscription.plan.name.capitalize()} Plan",
                        'amount': float(subscription.plan.monthly_price if subscription.billing_interval == 'monthly' else subscription.plan.annual_price),
                        'quantity': 1
                    }])
                )
                
                subscription.user.subscription_status = 'active'
                subscription.user.current_subscription_id = subscription.id
                
                from app import db
                db.session.add(payment)
                db.session.add(invoice)
                db.session.commit()
                
                logger.info(f"Subscription {subscription.id} activated via Ecocash")

                # Send subscription activation webhook to Make
                try:
                    from app.services.make_service import send_subscription_webhook
                    # Include the callback payload if available in callback_data
                    ecocash_response = callback_data if isinstance(callback_data, dict) else None
                    send_subscription_webhook(subscription, ecocash_response)
                except Exception as ex:
                    logger.error(f"Failed sending subscription webhook: {str(ex)}")
                
                return {
                    'processed': True,
                    'subscription_id': subscription.id,
                    'message': 'Subscription activated'
                }
            elif is_failed:
                # Payment failed
                subscription.status = 'failed'
                
                from app import db
                db.session.commit()
                
                logger.warning(f"Ecocash payment failed for subscription {subscription.id}")
                
                return {
                    'processed': True,
                    'subscription_id': subscription.id,
                    'message': 'Payment failed'
                }
            else:
                # Pending - do nothing
                return {
                    'processed': False,
                    'message': f"Transaction status: {status}"
                }
                
        except Exception as e:
            logger.error(f"Ecocash callback handling error: {str(e)}")
            return {
                'processed': False,
                'message': f"Error: {str(e)}"
            }
    
    def refund_transaction(self, transaction_id, reason=None):
        """
        Request refund for Ecocash transaction
        
        Args:
            transaction_id: Original transaction ID
            reason: Refund reason
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Rely on the Ecocash API response; no merchant credentials required
            payload = {
                'transaction_id': transaction_id,
                'reason': reason or 'Customer requested'
            }

            response = requests.post(
                f"{self.api_url}refund/",
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                logger.info(f"Refund initiated for transaction {transaction_id}")
                return {
                    'success': True,
                    'message': 'Refund initiated'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Refund failed')
                }
        except Exception as e:
            logger.error(f"Refund error: {str(e)}")
            return {
                'success': False,
                'message': f"Refund error: {str(e)}"
            }
    
    # Helper methods
    
    def _attempt_payment(self, phone_number: str, amount: float, short_code: str = "36174") -> tuple:
        """
        Make a payment request to Ecocash USSD-push endpoint.
        
        Returns:
            tuple: (success: bool, response_data: dict|str)
                   - success=True if payment initiated successfully
                   - response_data contains the parsed response or error message
        """
        payload = {
            "msisdn": phone_number,
            "short_code": short_code,
            "amount": amount
        }
        try:
            resp = requests.post(self.api_url, json=payload, headers=self._get_headers(), timeout=self.timeout)
            parsed = None
            try:
                parsed = resp.json()
            except Exception:
                parsed = resp.text

            # Heuristic success checks: HTTP 200 and either JSON status or "successfully" in text
            if resp.status_code == 200:
                if isinstance(parsed, dict):
                    status_val = parsed.get("status") or parsed.get("Status") or parsed.get("message")
                    if status_val and ("success" in str(status_val).lower()):
                        return True, parsed
                    flattened = " ".join([str(v) for v in parsed.values()])
                    if "success" in flattened.lower() or "successfully" in flattened.lower():
                        return True, parsed
                else:
                    if "success" in str(parsed).lower() or "successfully" in str(parsed).lower():
                        return True, parsed

            # Not a success
            logger.warning(f"Ecocash API returned HTTP {resp.status_code}: {parsed}")
            return False, parsed
        except requests.exceptions.RequestException as e:
            logger.error(f"Ecocash API request error: {str(e)}")
            return False, str(e)
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number to Ecocash standard format.

        Supports: +263777123456, 0777123456, 263777123456
        Returns: 263777123456
        """
        phone = str(phone).strip()

        # Remove +
        if phone.startswith('+'):
            phone = phone[1:]

        # Replace leading 0 with country code 263
        if phone.startswith('0'):
            phone = '263' + phone[1:]

        # Ensure it starts with 263
        if not phone.startswith('263'):
            phone = '263' + phone

        return phone
    
    def _generate_reference(self, user_id, plan_id):
        """Generate unique transaction reference"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"SOCIALS-{user_id}-{plan_id}-{timestamp}"
    
    def _get_callback_url(self):
        """Get callback URL for webhooks"""
        return f"{current_app.config.get('SERVER_URL', 'http://localhost:5000')}/billing/ecocash-callback"
    
    def _get_headers(self):
        """Get request headers for Ecocash API"""
        return {
            'Content-Type': 'application/json'
        }
    
    def _create_pending_subscription(self, user, plan, transaction_id, billing_interval, phone):
        """Create pending subscription record before payment confirmation"""
        from app import db
        
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            stripe_subscription_id=transaction_id,  # Store ecocash transaction ID here
            status='pending',  # Will be activated on callback
            billing_interval=billing_interval,
            current_period_start=None,
            current_period_end=None,
            trial_start=None,
            trial_end=None,
            cancel_at=None,
            canceled_at=None,
            cancellation_reason=None,
            currency='ZWL',
            payment_method='ecocash',
            phone_number=phone,
            created_at=datetime.utcnow()
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return subscription


# Global instance
ecocash_service = EcocashService()
