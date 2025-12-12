from PIL import Image
import os
from flask import current_app
import mimetypes

class MediaService:
    """Handle media uploads and processing"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    ALLOWED_PORTFOLIO_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png'}
    
    @staticmethod
    def allowed_file(filename, file_type='image'):
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        
        ext = os.path.splitext(filename)[1].lower()
        
        if file_type == 'image':
            return ext in MediaService.ALLOWED_IMAGE_EXTENSIONS
        elif file_type == 'video':
            return ext in MediaService.ALLOWED_VIDEO_EXTENSIONS
        elif file_type == 'portfolio':
            return ext in MediaService.ALLOWED_PORTFOLIO_EXTENSIONS
        
        return False
    
    @staticmethod
    def get_file_type(filename):
        """Determine if file is image or video"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in MediaService.ALLOWED_IMAGE_EXTENSIONS:
            return 'image'
        elif ext in MediaService.ALLOWED_VIDEO_EXTENSIONS:
            return 'video'
        
        return None
    
    @staticmethod
    def create_thumbnail(file_path, max_size=(200, 200)):
        """Create thumbnail for image"""
        try:
            img = Image.open(file_path)
            img.thumbnail(max_size)
            
            # Save thumbnail
            thumb_path = file_path.rsplit('.', 1)[0] + '_thumb.jpg'
            img.save(thumb_path, 'JPEG', quality=85)
            
            return thumb_path
        except Exception as e:
            print(f'Error creating thumbnail: {e}')
            return None
    
    @staticmethod
    def get_image_dimensions(file_path):
        """Get image dimensions"""
        try:
            img = Image.open(file_path)
            return img.width, img.height
        except Exception:
            return None, None
    
    @staticmethod
    def save_uploaded_file(file, user_id, file_type='image'):
        """Save uploaded file to disk"""
        try:
            # Create user upload directory
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            import time
            ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            file.save(file_path)
            
            return file_path, filename
        except Exception as e:
            raise Exception(f'Error saving file: {str(e)}')

media_service = MediaService()
