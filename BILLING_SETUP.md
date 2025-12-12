# 💳 Subscription & Billing Implementation Guide

## Overview

Your application now includes a complete subscription and billing system powered by **Stripe**. Users can:

- View pricing plans and features
- Start free trials (14-30 days depending on tier)
- Upgrade/downgrade plans anytime
- Manage payment methods
- View invoices and billing history
- Cancel subscriptions with prorations

## Quick Start

### 1. Get Stripe API Keys

1. Visit [Stripe Dashboard](https://dashboard.stripe.com)
2. Sign up or log in (create a test account for development)
3. Go to **Developers → API Keys**
4. Copy your **Publishable Key** (starts with `pk_test_`)
5. Copy your **Secret Key** (starts with `sk_test_`)

### 2. Update .env File

Add your Stripe credentials to `.env`:

```env
STRIPE_PUBLIC_KEY=pk_test_YOUR_PUBLISHABLE_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET
```

### 3. Create Stripe Products and Prices

For each plan (Free doesn't need Stripe setup, Pro/Business/Enterprise do):

#### Create Product (once per plan)
```bash
curl https://api.stripe.com/v1/products \
  -u sk_test_YOUR_SECRET_KEY: \
  -d name="Socials Pro Plan" \
  -d description="Pro tier subscription"
```

#### Create Monthly Price
```bash
curl https://api.stripe.com/v1/prices \
  -u sk_test_YOUR_SECRET_KEY: \
  -d product=prod_xxxxx \
  -d unit_amount=2900 \
  -d currency=usd \
  -d recurring[interval]=month
```

#### Create Annual Price
```bash
curl https://api.stripe.com/v1/prices \
  -u sk_test_YOUR_SECRET_KEY: \
  -d product=prod_xxxxx \
  -d unit_amount=29000 \
  -d currency=usd \
  -d recurring[interval]=year
```

### 4. Update Database

Store Stripe price IDs in the database:

```python
from app.models import Plan

pro = Plan.query.filter_by(name='pro').first()
pro.stripe_product_id = 'prod_xxxxx'
pro.stripe_price_id_monthly = 'price_xxxxx'
pro.stripe_price_id_annual = 'price_xxxxx'
db.session.commit()
```

### 5. Set Up Webhooks

1. In Stripe Dashboard → **Developers → Webhooks**
2. Click **Add endpoint**
3. Endpoint URL: `https://yourdomain.com/billing/webhook`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.created`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy **Signing secret** to `STRIPE_WEBHOOK_SECRET` in `.env`

### 6. Test the Flow

1. Open app at `http://localhost:5000`
2. Go to `/billing/pricing`
3. Click **Sign Up** on Pro plan
4. Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
5. Complete checkout
6. Verify subscription created in Stripe dashboard

## Database Schema

### Plans Table
```
id                       INT PRIMARY KEY
name                     VARCHAR (free, pro, business, enterprise)
display_name             VARCHAR (Free, Pro, Business, Enterprise)
monthly_price            FLOAT ($29.00)
annual_price             FLOAT ($290.00)
trial_days               INT (14, 30, 0)
features                 JSON {pages: 5, posts_per_month: 500, ...}
stripe_product_id        VARCHAR (prod_xxxxx)
stripe_price_id_monthly  VARCHAR (price_xxxxx)
stripe_price_id_annual   VARCHAR (price_xxxxx)
```

### Subscriptions Table
```
id                       INT PRIMARY KEY
user_id                  INT FK → users
plan_id                  INT FK → plans
stripe_subscription_id   VARCHAR (sub_xxxxx)
status                   VARCHAR (active, trialing, past_due, canceled)
billing_interval         VARCHAR (monthly, annual)
current_period_start     DATETIME
current_period_end       DATETIME
trial_start              DATETIME
trial_end                DATETIME
canceled_at              DATETIME
```

### Invoices Table
```
id                       INT PRIMARY KEY
user_id                  INT FK → users
subscription_id          INT FK → subscriptions
stripe_invoice_id        VARCHAR (in_xxxxx)
status                   VARCHAR (paid, open, draft, void)
amount_due               FLOAT
amount_paid              FLOAT
issued_date              DATETIME
paid_date                DATETIME
pdf_url                  VARCHAR (PDF from Stripe)
```

### PaymentMethods Table
```
id                       INT PRIMARY KEY
user_id                  INT FK → users
stripe_payment_method_id VARCHAR (pm_xxxxx)
type                     VARCHAR (card, bank_account)
card_brand               VARCHAR (visa, mastercard, amex)
card_last4               VARCHAR (4242)
is_default               BOOLEAN
```

## API Endpoints

### Pricing & Checkout
```
GET  /billing/pricing              # View all plans
GET  /billing/plans                # JSON API - all plans
GET  /billing/checkout/<plan_id>   # Checkout form
POST /billing/checkout/<plan_id>   # Start subscription
```

### Payment Methods
```
GET  /billing/add-payment-method   # Add card form
POST /billing/add-payment-method   # Save payment method
```

### Subscription Management
```
GET  /billing/dashboard                       # User billing dashboard
POST /billing/upgrade-plan/<plan_id>          # Change plan
POST /billing/cancel-subscription             # Cancel subscription
GET  /billing/invoices                        # List invoices
GET  /billing/invoice/<invoice_id>            # View single invoice
```

### Webhooks
```
POST /billing/webhook              # Stripe webhook endpoint
```

### Admin
```
GET  /billing/admin/plans                    # Manage plans
GET  /billing/admin/plans/<plan_id>/edit     # Edit plan
POST /billing/admin/plans/<plan_id>/edit     # Save plan
```

## User Model Changes

New fields added to `User`:

```python
plan_id                    # FK to current plan
stripe_customer_id         # Stripe customer ID (unique)
current_subscription_id    # FK to active subscription
subscription_status        # none, trialing, active, past_due, canceled
subscription_ends_at       # When current subscription ends
billing_email              # May differ from login email
```

New methods:

```python
user.get_current_plan()           # Get user's current plan
user.has_feature(feature_name)    # Check if feature available
user.is_on_free_plan()            # Boolean check
user.is_paid_subscriber()         # Check for active paid subscription
```

## Feature-Based Access Control

Restrict features based on subscription plan:

```python
from flask_login import current_user
from functools import wraps

def requires_feature(feature_name):
    """Decorator to require a feature"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            if current_user.has_feature(feature_name):
                return f(*args, **kwargs)
            flash('This feature requires a paid plan', 'warning')
            return redirect(url_for('billing.pricing'))
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

# Usage:
@app.route('/ai-captions')
@login_required
@requires_feature('ai_captions_per_month')
def ai_captions():
    # Only Pro+ users can access
    pass
```

## Webhook Handling

Stripe automatically calls `/billing/webhook` for these events:

### Subscription Events
- `customer.subscription.created` → Create subscription record
- `customer.subscription.updated` → Update subscription status
- `customer.subscription.deleted` → Mark as canceled

### Invoice Events
- `invoice.created` → Store invoice in database
- `invoice.payment_succeeded` → Mark invoice as paid
- `invoice.payment_failed` → Set subscription to past_due

The `StripeService` automatically handles all webhook processing.

## Testing

### Test Cards (Stripe Testmode)

| Card | Use Case |
|------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0002 4000 0010` | Requires authentication |
| `4000 0200 0000 0000` | 3D Secure 2 challenge |

### Test Subscription Flow

1. Add test payment method
2. Start 14-day free trial (Pro tier)
3. Wait for trial to end in Stripe dashboard
4. Verify upgrade prompt appears in app
5. Upgrade to Business plan
6. Verify prorations calculated
7. Cancel subscription
8. Verify access downgraded to Free plan

## Production Checklist

Before deploying to production:

- [ ] Create production Stripe account
- [ ] Update `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY` (production keys)
- [ ] Configure production webhook URL in Stripe
- [ ] Update `STRIPE_WEBHOOK_SECRET` with production secret
- [ ] Create all products and prices in production
- [ ] Update database with production stripe IDs
- [ ] Test full subscription flow with real cards
- [ ] Set up email notifications for failed payments
- [ ] Configure dunning emails in Stripe
- [ ] Review subscription pricing and features
- [ ] Add Terms of Service mentioning auto-renewal
- [ ] Implement cancellation survey
- [ ] Set up revenue analytics dashboard
- [ ] Configure fraud detection in Stripe

## Troubleshooting

### "No payment method" error
**Solution**: User must add a payment method before checkout.
Route: `/billing/add-payment-method`

### Webhook not firing
1. Check Stripe dashboard → Webhooks → Event logs
2. Verify webhook URL is correct and accessible
3. Confirm `STRIPE_WEBHOOK_SECRET` matches in `.env`
4. Check app logs for webhook processing errors

### Proration math incorrect
Stripe auto-calculates prorations. Verify in Stripe dashboard under subscription details.

### Trial period issue
- Free → check that plan has `trial_days = 0`
- Pro → check that plan has `trial_days = 14`
- Business → check that plan has `trial_days = 30`

## Next Steps

1. **Implement dunning** (automatic retry for failed payments)
2. **Add usage-based billing** (overage charges for extra features)
3. **Usage analytics** (track how much of quota users are using)
4. **Discount codes** (promo/coupon system)
5. **Team seat management** (sell seats as add-on)
6. **Custom invoicing** (white-label invoices)
7. **Tax integration** (auto calculate sales tax)

---

For more details, see `SUBSCRIPTION_REFERENCE.md` or check the `app/services/stripe_service.py` source code.
