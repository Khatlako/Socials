from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Media
from app import db
from app.services.media_service import media_service
from werkzeug.utils import secure_filename
import os

media_bp = Blueprint('media', __name__, url_prefix='/media')

@media_bp.route('/')
@login_required
def index():
    """Media library"""
    page = request.args.get('page', 1, type=int)
    media_type = request.args.get('type', 'all')  # all, image, video
    
    query = Media.query.filter_by(user_id=current_user.id)
    
    if media_type in ['image', 'video']:
        query = query.filter_by(media_type=media_type)
    
    media = query.order_by(Media.created_at.desc()).paginate(page=page, per_page=12)
    
    return render_template('media/index.html', media=media, media_type=media_type)

@media_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload media file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Determine media type
    media_type = media_service.get_file_type(file.filename)
    
    if not media_type or not media_service.allowed_file(file.filename, media_type):
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    try:
        # Save file
        file_path, filename = media_service.save_uploaded_file(file, current_user.id, media_type)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        # Create media record
        media = Media(
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            media_type=media_type,
            file_extension=os.path.splitext(filename)[1].lower(),
            file_size=file_size,
            title=request.form.get('title', secure_filename(file.filename)),
            description=request.form.get('description', '')
        )
        
        # Process media
        if media_type == 'image':
            width, height = media_service.get_image_dimensions(file_path)
            media.width = width
            media.height = height
            
            # Create thumbnail
            thumb_path = media_service.create_thumbnail(file_path)
            if thumb_path:
                media.thumbnail_path = thumb_path
        
        db.session.add(media)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'media_id': media.id,
            'filename': filename,
            'media_type': media_type,
            'message': 'File uploaded successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@media_bp.route('/<int:media_id>')
@login_required
def view(media_id):
    """View media details"""
    media = Media.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    
    return render_template('media/view.html', media=media)

@media_bp.route('/<int:media_id>/edit', methods=['POST'])
@login_required
def edit(media_id):
    """Edit media metadata"""
    media = Media.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    
    media.title = request.json.get('title', media.title)
    media.description = request.json.get('description', media.description)
    media.tags = request.json.get('tags', media.tags)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Media updated'})

@media_bp.route('/<int:media_id>/delete', methods=['POST'])
@login_required
def delete(media_id):
    """Delete media"""
    media = Media.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete files
        if os.path.exists(media.file_path):
            os.remove(media.file_path)
        
        if media.thumbnail_path and os.path.exists(media.thumbnail_path):
            os.remove(media.thumbnail_path)
        
        db.session.delete(media)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Media deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@media_bp.route('/api/list')
@login_required
def api_list():
    """Get media list as JSON (for post creation)"""
    media_type = request.args.get('type', 'all')
    
    query = Media.query.filter_by(user_id=current_user.id)
    
    if media_type in ['image', 'video']:
        query = query.filter_by(media_type=media_type)
    
    media = query.order_by(Media.created_at.desc()).all()
    
    return jsonify([{
        'id': m.id,
        'filename': m.filename,
        'media_type': m.media_type,
        'title': m.title,
        'thumbnail_path': m.thumbnail_path or m.file_path,
        'width': m.width,
        'height': m.height
    } for m in media])
