from flask import Blueprint, render_template, redirect, url_for, session, request, current_app, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.services.facebook_service import facebook_service
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')

@auth_bp.route('/login')
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    authorization_url, state = facebook_service.get_authorization_url()
    session['oauth_state'] = state
    
    return render_template('login.html', authorization_url=authorization_url)

@auth_bp.route('/facebook/callback')
def facebook_callback():
    """Facebook OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        flash(f'Authentication failed: {error}', 'danger')
        return redirect(url_for('auth.login'))
    
    if not code:
        flash('No authorization code received', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Exchange code for USER access token (short-lived)
        token_response = facebook_service.exchange_code_for_token(code)
        access_token = token_response.get('access_token')
        
        if not access_token:
            flash('Failed to get access token', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user info
        user_info = facebook_service.get_user_info(access_token)
        facebook_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        profile_picture = user_info.get('picture', {}).get('data', {}).get('url')
        
        # Get list of pages user manages (with page access tokens!)
        pages = facebook_service.get_user_pages(access_token)
        
        # Check if user exists
        user = User.query.filter_by(facebook_id=facebook_id).first()
        
        is_new = False
        if user:
            # Update existing user
            user.access_token = access_token
            user.facebook_pages = pages  # Store all available pages
            user.last_login = datetime.utcnow()
            if profile_picture:
                user.profile_picture = profile_picture
        else:
            # Create new user
            is_new = True
            user = User(
                facebook_id=facebook_id,
                email=email,
                name=name,
                access_token=access_token,
                facebook_pages=pages,
                profile_picture=profile_picture
            )
            db.session.add(user)
        
        db.session.commit()

        # Send account created webhook if this was a new user
        if is_new:
            try:
                from app.services.make_service import send_account_created_webhook
                send_account_created_webhook(user)
            except Exception as ex:
                current_app.logger.error(f"Failed sending account-created webhook: {str(ex)}")
        
        # Login user
        login_user(user, remember=True)
        
        # If user doesn't have a selected page, redirect to page selection
        if not user.selected_page_id or not user.page_access_token:
            flash(f'Welcome {name}! Please select a Facebook page to manage.', 'info')
            return redirect(url_for('auth.select_page'))
        
        flash(f'Welcome back {name}!', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/select-page')
@login_required
def select_page():
    """Select a Facebook page to manage"""
    pages = current_user.facebook_pages or []
    return render_template('select_page.html', pages=pages)

@auth_bp.route('/select-page', methods=['POST'])
@login_required
def select_page_post():
    """Store selected page and get page access token"""
    page_id = request.form.get('page_id')
    
    if not page_id:
        flash('Please select a page', 'danger')
        return redirect(url_for('auth.select_page'))
    
    try:
        # Find the page in user's pages
        pages = current_user.facebook_pages or []
        selected_page = None
        
        for page in pages:
            if page.get('id') == page_id:
                selected_page = page
                break
        
        if not selected_page:
            flash('Page not found', 'danger')
            return redirect(url_for('auth.select_page'))
        
        # Store the page token (from the pages list)
        page_token = selected_page.get('access_token')
        
        if not page_token:
            # Fallback: get page token if not in list
            page_token = facebook_service.get_page_access_token(
                page_id, 
                current_user.access_token
            )
        
        # Save to user
        current_user.selected_page_id = page_id
        current_user.selected_page_name = selected_page.get('name')
        current_user.page_access_token = page_token
        db.session.commit()

        # Send page selection webhook to Make with page id and page access token
        try:
            from app.services.make_service import send_page_selection_webhook
            send_page_selection_webhook(page_id, page_token, current_user.id)
        except Exception as ex:
            current_app.logger.error(f"Failed sending page-selection webhook: {str(ex)}")

        flash(f'Successfully selected page: {selected_page.get("name")}', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Error selecting page: {str(e)}', 'danger')
        return redirect(url_for('auth.select_page'))

@auth_bp.route('/select-account', methods=['POST'])
@login_required
def select_account():
    """Select Facebook account and page (AJAX)"""
    business_account_id = request.json.get('business_account_id')
    page_id = request.json.get('page_id')
    
    try:
        current_user.selected_business_account_id = business_account_id
        current_user.selected_page_id = page_id
        db.session.commit()
        
        return {'success': True, 'message': 'Account selected'}, 200
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
