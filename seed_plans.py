"""
Seed script to create default subscription plans in the database
Run with: python seed_plans.py
"""

from app import create_app, db
from app.models import Plan

def seed_plans():
    """Create default subscription plans"""
    
    plans = [
        {
            'name': 'free',
            'display_name': 'Free',
            'slug': 'free',
            'description': 'Perfect for getting started',
            'monthly_price': 0,
            'annual_price': 0,
            'trial_days': 0,
            'require_card_for_trial': False,
            'display_order': 0,
            'features': {
                'pages': 1,
                'team_members': 1,
                'posts_per_month': 30,
                'scheduled_posts': 10,
                'media_storage_gb': 0.05,  # 50MB
                'analytics_history_days': 30,
                'ai_captions_per_month': 0,
                'support_response_hours': None,
                'api_access': False,
                'advanced_analytics': False,
                'competitor_analysis': False,
                'export_reports': False,
                'custom_integrations': False,
            }
        },
        {
            'name': 'pro',
            'display_name': 'Pro',
            'slug': 'pro',
            'description': 'For growing businesses',
            'monthly_price': 29.00,
            'annual_price': 290.00,  # 17% discount
            'trial_days': 14,
            'require_card_for_trial': False,
            'display_order': 1,
            'features': {
                'pages': 5,
                'team_members': 3,
                'posts_per_month': 500,
                'scheduled_posts': 100,
                'media_storage_gb': 1,
                'analytics_history_days': 90,
                'ai_captions_per_month': 50,
                'support_response_hours': 24,
                'api_access': True,
                'advanced_analytics': False,
                'competitor_analysis': False,
                'export_reports': True,
                'custom_integrations': False,
            }
        },
        {
            'name': 'business',
            'display_name': 'Business',
            'slug': 'business',
            'description': 'For agencies and larger teams',
            'monthly_price': 79.00,
            'annual_price': 790.00,  # 17% discount
            'trial_days': 30,
            'require_card_for_trial': True,
            'display_order': 2,
            'features': {
                'pages': 25,
                'team_members': 10,
                'posts_per_month': 2000,
                'scheduled_posts': 500,
                'media_storage_gb': 10,
                'analytics_history_days': 365,  # 1 year
                'ai_captions_per_month': 500,
                'support_response_hours': 4,
                'api_access': True,
                'advanced_analytics': True,
                'competitor_analysis': True,
                'export_reports': True,
                'custom_integrations': True,
            }
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise',
            'slug': 'enterprise',
            'description': 'Custom solutions for large organizations',
            'monthly_price': 0,  # Custom pricing
            'annual_price': 0,
            'trial_days': 0,
            'require_card_for_trial': False,
            'display_order': 3,
            'features': {
                'pages': -1,  # Unlimited
                'team_members': -1,  # Unlimited
                'posts_per_month': -1,  # Unlimited
                'scheduled_posts': -1,
                'media_storage_gb': -1,
                'analytics_history_days': -1,  # Unlimited
                'ai_captions_per_month': -1,
                'support_response_hours': 1,  # 1 hour SLA
                'api_access': True,
                'advanced_analytics': True,
                'competitor_analysis': True,
                'export_reports': True,
                'custom_integrations': True,
            }
        }
    ]
    
    app = create_app()
    with app.app_context():
        # Check if plans already exist
        existing = Plan.query.first()
        if existing:
            print("✅ Plans already exist in database. Skipping seed.")
            return
        
        print("Creating subscription plans...")
        for plan_data in plans:
            plan = Plan(**plan_data)
            db.session.add(plan)
            print(f"  ✓ Added {plan.display_name} plan")
        
        db.session.commit()
        print("\n✅ All plans created successfully!")
        
        # Print plan IDs for Stripe setup
        print("\nPlan IDs for reference:")
        for plan in Plan.query.all():
            print(f"  {plan.display_name}: ID={plan.id}")

if __name__ == '__main__':
    seed_plans()
