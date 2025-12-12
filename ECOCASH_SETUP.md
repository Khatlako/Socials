# Ecocash Mobile Money Subscription System

This app uses **Ecocash USSD Push** for subscription payments. Users subscribe via their mobile phones without needing a credit card.

## How It Works

1. **User Selects Plan** → Clicks "Subscribe" on pricing page
2. **Phone Verification** → Enters phone number (0777123456 or +263777123456)
3. **USSD Push Sent** → Ecocash sends a payment prompt to their phone
4. **Confirm & Pay** → User enters PIN to authorize payment
5. **Subscription Activated** → Webhook confirms payment, subscription starts

---

## Quick Start (5 Steps)

### 1. Get Ecocash API Credentials

Contact Ecocash merchant support:
- **Website**: https://www.ecocash.com.zw/
- **Support Email**: merchant@econet.co.zw
- Note: This integration relies on the Ecocash endpoint responses and does not require merchant credentials to be stored in the application.

### 2. Update `.env` File

```dotenv
# Ecocash Configuration
ECOCASH_API_URL=https://dt-externalproxy-1.etl.co.ls/etl/salesagentpay/paymerchant/

# Your app's public URL (for webhooks)
SERVER_URL=https://yourdomain.com
```

### 3. Pricing Tiers in ZWL

Database seeded with 4 plans:

| Plan | Monthly | Annual | Trial | Features |
|------|---------|--------|-------|----------|
| **Free** | ZWL 0 | ZWL 0 | Unlimited | 1 page, 30 posts/mo, basic analytics |
| **Pro** | ZWL 99 | ZWL 990 | 14 days | 5 pages, 500 posts/mo, AI captions |
| **Business** | ZWL 299 | ZWL 2990 | 30 days | 25 pages, 2K posts/mo, advanced |
| **Enterprise** | Custom | Custom | Custom | Unlimited, dedicated support |

*Prices in Zimbabwean Dollar (ZWL) - adjust as needed in database*

### 4. Set Up Webhook Endpoint

Ecocash will POST payment confirmations to:
```
https://yourdomain.com/billing/ecocash-callback
```

**API Request Payload (sent by your app):**
```json
{
  "msisdn": "263777123456",
  "short_code": 36174,
  "amount": 99.00
}
```

**Webhook Callback Payload (sent by Ecocash):**
```json
{
  "transactionId": "TXN123456",
  "status": "completed|failed|pending",
  "amount": 99.00,
  "msisdn": "263777123456",
  "timestamp": "2024-12-12T10:30:00Z"
}
```

Configure in Ecocash dashboard:
- **Webhook URL**: `https://yourdomain.com/billing/ecocash-callback`
- **Request Method**: POST
- **Content-Type**: application/json

### 5. Test Payment Flow

```bash
# Start your app
python run.py

# Visit pricing page
http://localhost:5000/billing/pricing

# Click "Subscribe to Pro Plan"
# Enter test phone number: 0777123456
# Check for USSD push confirmation
```

---

## Database Schema

### `plans` Table
```python
id              - Plan ID (1=Free, 2=Pro, 3=Business, 4=Enterprise)
name            - free, pro, business, enterprise
display_name    - Free, Pro, Business, Enterprise
monthly_price   - ZWL price/month
annual_price    - ZWL price/year
trial_days      - Days free trial (0=none, 14=2 weeks, 30=1 month)
features        - JSON with feature limits
payment_methods - 'ecocash' (future: could be comma-separated)
```

### `subscriptions` Table
```python
id                      - Subscription ID
user_id                 - FK to users
plan_id                 - FK to plans
stripe_subscription_id  - Ecocash transaction ID (reusing for compatibility)
payment_method          - 'ecocash'
phone_number            - User's Ecocash phone number
status                  - active|pending|failed|canceled
billing_interval        - monthly|annual
current_period_start    - When subscription started
current_period_end      - When next charge occurs
trial_start/trial_end   - Trial period dates
currency                - ZWL
amount_billed           - Last charged amount
```

### `invoices` Table
```python
id                  - Invoice ID
subscription_id     - FK to subscriptions
amount_due          - Total charged
amount_paid         - Amount received
status              - paid|failed|pending
issued_date         - Invoice date
paid_date           - Payment confirmation date
currency            - ZWL
lines               - JSON with items (plan, amount, quantity)
```

### `payments` Table
```python
id                      - Payment ID
subscription_id         - FK to subscriptions
amount                  - Charged amount (ZWL)
currency                - ZWL
status                  - completed|failed
payment_method          - ecocash
external_transaction_id - Ecocash transaction ID
created_at              - Payment timestamp
```

---

## API Endpoints

### User Routes (all require login)

```
GET    /billing/pricing
       Display pricing page with all plans and feature matrix
       
GET    /billing/plans
       JSON API - returns all active plans

GET    /billing/ecocash-checkout/<plan_id>
       Ecocash checkout form (phone number entry)
       
POST   /billing/ecocash-checkout/<plan_id>
       Initiate USSD push payment
       Request: billing_interval, phone_number
       Response: Redirects to confirmation page
       
GET    /billing/ecocash-confirm/<transaction_id>
       Payment confirmation waiting page
       Auto-polls for payment status every 2 seconds
       
GET    /billing/ecocash-check-status/<transaction_id>
       AJAX endpoint - check if payment completed
       Response: {status: success|pending|failed, user_message: string}

GET    /billing/dashboard
       User's billing dashboard (current subscription, recent invoices)
       
GET    /billing/invoices
       Paginated list of all invoices
       
GET    /billing/invoice/<invoice_id>
       Single invoice details
       
POST   /billing/cancel-subscription
       Cancel active subscription
       Request: subscription_id, reason
       Response: Redirects to dashboard
```

### Webhook Route (no auth)

```
POST   /billing/ecocash-callback
       Ecocash payment confirmation webhook
       Request: {transaction_id, status, amount, msisdn, timestamp}
       Response: {status: success|pending|error}
```

---

## Feature Gating System

Restrict features based on plan:

```python
# In your routes
@app.route('/ai-captions')
@login_required
def ai_captions():
    if not current_user.has_feature('ai_captions_per_month'):
        flash('AI captions require Pro plan or higher', 'info')
        return redirect(url_for('billing.pricing'))
    # Process captions...

# In templates
{% if current_user.has_feature('advanced_analytics') %}
    <div class="analytics-dashboard">
        <!-- Show advanced features -->
    </div>
{% else %}
    <div class="upgrade-prompt">
        <p>Upgrade to Business plan for advanced analytics</p>
        <a href="{{ url_for('billing.pricing') }}" class="btn">Upgrade Now</a>
    </div>
{% endif %}

# User model methods
current_user.get_current_plan()          # Returns Plan object
current_user.has_feature('feature_name') # Returns feature value
current_user.is_on_free_plan()           # Boolean
current_user.is_paid_subscriber()        # Boolean
```

---

## Ecocash Service Layer

### `app/services/ecocash_service.py`

**Main Methods:**

```python
ecocash_service.initiate_ussd_push(user, plan, phone_number, billing_interval)
    # Initiates USSD push payment
    # Returns: {success: bool, transaction_id: str, amount: float, ussd_code: str}

ecocash_service.verify_transaction(transaction_id)
    # Check if transaction was successful
    # Returns: {verified: bool, status: str, amount: float}

ecocash_service.handle_callback(callback_data)
    # Process webhook from Ecocash
    # Activates subscription on successful payment
    # Returns: {processed: bool, subscription_id: int}

ecocash_service.refund_transaction(transaction_id, reason)
    # Request refund from Ecocash
    # Returns: {success: bool, message: str}
```

**Phone Number Formatting:**
```python
Supports:
  +263777123456    → 263777123456
  0777123456       → 263777123456  
  263777123456     → 263777123456
```

---

## Testing

### Test Phone Numbers
```
Ecocash test environment may provide test numbers:
- 0777000001 - Success
- 0777000002 - Failure
- 0777000003 - Timeout

Check Ecocash test documentation for current values
```

### Test Workflow
```bash
1. Visit http://localhost:5000/billing/pricing
2. Click "Subscribe" on any plan
3. Enter test phone: 0777000001
4. Click "Pay with Ecocash"
5. Wait for USSD prompt simulation
6. Check http://localhost:5000/billing/dashboard
   Should show active subscription
```

### Logs
```
Check Flask logs for:
  - "Initiating Ecocash USSD push..."
  - "Subscription X activated via Ecocash"
  - "Ecocash API error" (if issues)

Database:
  - Check `subscriptions` table status field
  - Check `payments` table for records
```

---

## Production Deployment

### Checklist

- [ ] Ecocash API credentials obtained from merchant support
- [ ] `.env` updated with real credentials
- [ ] `SERVER_URL` points to your production domain
- [ ] Webhook URL configured in Ecocash dashboard
- [ ] SSL/HTTPS enabled (required by Ecocash)
- [ ] Test payment successful
- [ ] Email notifications set up for subscription changes
- [ ] Database backed up
- [ ] Error logging configured (Sentry, etc.)
- [ ] Monitoring alerts set up for failed payments

### Environment Variables
```dotenv
# Production
FLASK_ENV=production
SERVER_URL=https://yourdomain.com
DEBUG=False
```

---

## Troubleshooting

### "USSD push not received"
- Check phone number format (leading zero or +263)
- Verify phone is Ecocash-enabled
- Check API credentials in `.env`
- Review Ecocash API logs

### "Payment confirmed but subscription not activated"
- Check webhook URL is public and accessible
- Verify webhook endpoint logs for errors
- Check Ecocash dashboard webhook delivery status
- Manually trigger webhook from Ecocash for testing

### "API request timeout"
- Increase timeout in `ecocash_service.py` (currently 30s)
- Check internet connectivity
- Verify Ecocash API is responding
- Monitor server logs for network errors

### "Transaction ID mismatch"
- Ensure `stripe_subscription_id` field used for Ecocash IDs
- Check that webhook sends matching transaction_id
- Verify database constraints aren't blocking creation

---

## File Structure

```
app/
├── models/
│   ├── plan.py          # Plan, Subscription, Invoice, Payment models
│   └── user.py          # User model (has subscription methods)
├── services/
│   └── ecocash_service.py   # Ecocash API integration
├── routes/
│   └── billing.py       # All billing endpoints
└── templates/
    ├── pricing.html                 # Pricing page
    ├── ecocash_checkout.html        # Phone entry form
    ├── ecocash_confirm.html         # Payment confirmation
    ├── billing_dashboard.html       # User dashboard
    ├── invoices.html                # Invoice list
    └── invoice_detail.html          # Invoice detail
```

---

## Future Enhancements

- [ ] Multiple payment methods (Stripe, MoMoPay, etc.)
- [ ] Discount codes / coupon system
- [ ] Usage-based billing (overage charges)
- [ ] Dunning management (retry failed payments)
- [ ] Tax calculation integration
- [ ] Team seat management
- [ ] Usage analytics dashboard
- [ ] Churn prediction / retention offers

---

**Questions?** Contact support or review `app/services/ecocash_service.py` for complete implementation details.
