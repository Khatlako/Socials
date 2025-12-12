from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Portfolio, Post
from app import db
from app.services.portfolio_service import portfolio_service
from app.services.media_service import media_service
from app.services.ai_service import ai_service
from werkzeug.utils import secure_filename
import os

portfolios_bp = Blueprint('portfolios', __name__, url_prefix='/portfolios')

@portfolios_bp.route('/')
@login_required
def index():
    """Portfolio management"""
    page = request.args.get('page', 1, type=int)
    
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).order_by(
        Portfolio.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('portfolios/index.html', portfolios=portfolios)

@portfolios_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload portfolio file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png'}
    
    if ext not in allowed_extensions:
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    try:
        # Save file
        file_path, filename = media_service.save_uploaded_file(file, current_user.id, 'portfolio')
        
        # Determine file type
        if ext == '.pdf':
            file_type = 'pdf'
        elif ext in ['.docx', '.doc']:
            file_type = 'docx' if ext == '.docx' else 'doc'
        elif ext == '.txt':
            file_type = 'txt'
        else:
            file_type = 'image'
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create portfolio record
        portfolio = Portfolio(
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            title=request.form.get('title', secure_filename(file.filename)),
            description=request.form.get('description', ''),
            status='processing'
        )
        
        # Extract text from document
        try:
            extracted_text = portfolio_service.extract_text_from_file(file_path, file_type)
            portfolio.extracted_text = extracted_text
        except Exception as e:
            portfolio.status = 'failed'
            print(f'Error extracting text: {e}')
        
        db.session.add(portfolio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'portfolio_id': portfolio.id,
            'filename': filename,
            'message': 'Portfolio uploaded successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@portfolios_bp.route('/<int:portfolio_id>')
@login_required
def view(portfolio_id):
    """View portfolio details"""
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    
    # Get related AI-generated posts
    ai_posts = Post.query.filter_by(source_id=portfolio_id).all()
    
    return render_template('portfolios/view.html', portfolio=portfolio, ai_posts=ai_posts)

@portfolios_bp.route('/<int:portfolio_id>/generate-posts', methods=['POST'])
@login_required
def generate_posts(portfolio_id):
    """Generate AI posts from portfolio"""
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    
    if not portfolio.extracted_text:
        return jsonify({'success': False, 'error': 'No content to generate posts from'}), 400
    
    try:
        num_posts = request.json.get('num_posts', 3)
        
        # Generate posts using AI
        generated_posts = ai_service.generate_posts_from_portfolio(
            portfolio.extracted_text, 
            num_posts=num_posts
        )
        
        # Save generated posts
        created_posts = []
        for post_data in generated_posts:
            if isinstance(post_data, dict):
                content = post_data.get('content', '')
                hashtags = post_data.get('hashtags', '')
            else:
                content = str(post_data)
                hashtags = ''
            
            post = Post(
                user_id=current_user.id,
                content=content,
                post_type='ai_generated',
                source_id=portfolio_id,
                hashtags=hashtags,
                original_content=content,
                status='pending',
                ai_model_used='claude-3-5-sonnet-20241022'
            )
            db.session.add(post)
            created_posts.append(post)
        
        portfolio.ai_posts_generated = len(created_posts)
        portfolio.is_processed = True
        portfolio.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'posts_generated': len(created_posts),
            'message': f'{len(created_posts)} posts generated and added to pending queue'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@portfolios_bp.route('/<int:portfolio_id>/delete', methods=['POST'])
@login_required
def delete(portfolio_id):
    """Delete portfolio"""
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete file
        if os.path.exists(portfolio.file_path):
            os.remove(portfolio.file_path)
        
        # Delete related posts
        Post.query.filter_by(source_id=portfolio_id).delete()
        
        db.session.delete(portfolio)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Portfolio deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
