from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Plan, Subscription, Invoice
from app.services.ecocash_service import ecocash_service
from app import db

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

# ===== PRICING PAGE =====

@billing_bp.route('/pricing')
def pricing():
    """Display pricing page with all plans"""
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.display_order).all()
    
    # Get user's current plan if logged in
    user_plan = None
    if current_user.is_authenticated:
        user_plan = current_user.get_current_plan()
    
    return render_template('pricing.html', plans=plans, user_plan=user_plan)


@billing_bp.route('/plans')
def get_plans():
    """API endpoint to get all active plans (for AJAX)"""
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.display_order).all()
    
    plan_data = []
    for plan in plans:
        plan_data.append({
            'id': plan.id,
            'name': plan.name,
            'display_name': plan.display_name,
            'slug': plan.slug,
            'monthly_price': plan.monthly_price,
            'annual_price': plan.annual_price,
            'annual_discount_percent': plan.annual_discount_percent,
            'trial_days': plan.trial_days,
            'features': plan.features
        })
    
    return jsonify(plan_data)


# ===== CHECKOUT & SUBSCRIPTION SETUP =====

@billing_bp.route('/checkout/<int:plan_id>')
@login_required
def checkout(plan_id):
    """Redirect to Ecocash checkout"""
    return redirect(url_for('billing.ecocash_checkout', plan_id=plan_id))


# ===== BILLING DASHBOARD =====

@billing_bp.route('/dashboard')
@login_required
def billing_dashboard():
    """User billing dashboard"""
    # Get current subscription
    subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    
    # Get recent invoices
    invoices = Invoice.query.join(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Invoice.issued_date.desc()).limit(10).all()
    
    return render_template('billing_dashboard.html', subscription=subscription, invoices=invoices)


# ===== SUBSCRIPTION MANAGEMENT =====

@billing_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel active subscription"""
    subscription_id = request.form.get('subscription_id') or request.json.get('subscription_id')
    
    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=current_user.id
    ).first()
    
    if not subscription:
        return jsonify({'success': False, 'message': 'Subscription not found'}), 404
    
    try:
        from datetime import datetime
        # Cancel Ecocash subscription
        subscription.status = 'canceled'
        subscription.canceled_at = datetime.utcnow()
        subscription.cancellation_reason = request.form.get('reason') or request.json.get('reason', 'User requested')
        
        current_user.subscription_status = 'canceled'
        
        db.session.commit()
        
        flash('Your subscription has been canceled', 'success')
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Subscription canceled'})
        else:
            return redirect(url_for('billing.billing_dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error canceling subscription: {str(e)}', 'error')
        
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            return redirect(url_for('billing.billing_dashboard'))


# ===== INVOICE MANAGEMENT =====

@billing_bp.route('/invoices')
@login_required
def invoices():
    """View all invoices"""
    page = request.args.get('page', 1, type=int)
    
    invoices_list = Invoice.query.join(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Invoice.issued_date.desc()).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template('invoices.html', invoices=invoices_list)


@billing_bp.route('/invoice/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    """View single invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check ownership
    if invoice.subscription.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('billing.invoices'))
    
    return render_template('invoice_detail.html', invoice=invoice)


# ===== WEBHOOK HANDLING (Ecocash only) =====


# ===== ECOCASH PAYMENT ROUTES =====

@billing_bp.route('/ecocash-checkout/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def ecocash_checkout(plan_id):
    """Ecocash USSD push payment flow"""
    plan = Plan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Get payment details
        billing_interval = request.form.get('billing_interval', 'monthly')
        phone_number = request.form.get('phone_number', '').strip()
        
        if not phone_number:
            flash('Phone number is required', 'error')
            return redirect(url_for('billing.ecocash_checkout', plan_id=plan_id))
        
        # Initiate USSD push
        result = ecocash_service.initiate_ussd_push(
            user=current_user,
            plan=plan,
            phone_number=phone_number,
            billing_interval=billing_interval
        )
        
        if result['success']:
            # Store transaction info in session
            session['ecocash_transaction'] = {
                'transaction_id': result['transaction_id'],
                'plan_id': plan_id,
                'billing_interval': billing_interval,
                'amount': str(result['amount'])
            }
            
            flash(f"USSD push sent! Confirm on your phone. You can also dial {result['ussd_code']}", 'info')
            return redirect(url_for('billing.ecocash_confirm', transaction_id=result['transaction_id']))
        else:
            flash(f"Payment initiation failed: {result['message']}", 'error')
            return redirect(url_for('billing.ecocash_checkout', plan_id=plan_id))
    
    # GET: Show checkout form
    return render_template('ecocash_checkout.html', plan=plan)


@billing_bp.route('/ecocash-confirm/<transaction_id>')
@login_required
def ecocash_confirm(transaction_id):
    """Confirmation page while waiting for Ecocash callback"""
    # Get subscription by transaction ID
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not subscription:
        flash('Transaction not found', 'error')
        return redirect(url_for('billing.pricing'))
    
    return render_template('ecocash_confirm.html', subscription=subscription, transaction_id=transaction_id)


@billing_bp.route('/ecocash-check-status/<transaction_id>')
@login_required
def ecocash_check_status(transaction_id):
    """AJAX endpoint to check payment status"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not subscription:
        return jsonify({'status': 'not_found'}), 404
    
    status_map = {
        'active': 'success',
        'pending': 'pending',
        'failed': 'failed',
        'canceled': 'canceled'
    }
    
    return jsonify({
        'status': status_map.get(subscription.status, subscription.status),
        'plan_name': subscription.plan.display_name,
        'user_message': {
            'active': 'Payment successful! Your subscription is now active.',
            'pending': 'Waiting for payment confirmation...',
            'failed': 'Payment failed. Please try again.',
            'canceled': 'Subscription was canceled.'
        }.get(subscription.status, 'Unknown status')
    })


@billing_bp.route('/ecocash-callback', methods=['POST'])
def ecocash_callback():
    """Webhook endpoint for Ecocash payment callbacks (no auth required)"""
    try:
        callback_data = request.get_json() or {}
        
        # Process callback
        result = ecocash_service.handle_callback(callback_data)
        
        if result['processed']:
            return jsonify({'status': 'success', 'message': 'Callback processed'}), 200
        else:
            return jsonify({'status': 'pending', 'message': result['message']}), 202
            
    except Exception as e:
        current_app.logger.error(f"Ecocash callback error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@billing_bp.route('/ecocash-dashboard')
@login_required
def ecocash_dashboard():
    """View Ecocash subscriptions and transactions"""
    # Get subscriptions paid via Ecocash
    subscriptions = Subscription.query.filter_by(
        user_id=current_user.id,
        payment_method='ecocash'
    ).order_by(Subscription.created_at.desc()).all()
    
    return render_template('ecocash_dashboard.html', subscriptions=subscriptions)


