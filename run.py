#!/usr/bin/env python
"""Main application entry point"""

import os
from app import create_app, db
from app.models import User, Portfolio, Media, Post, ScheduledPost, PostAnalytics

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Register models for flask shell"""
    return {
        'db': db,
        'User': User,
        'Portfolio': Portfolio,
        'Media': Media,
        'Post': Post,
        'ScheduledPost': ScheduledPost,
        'PostAnalytics': PostAnalytics
    }

if __name__ == '__main__':
    app.run(debug=True)
