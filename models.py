from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.Enum('draft', 'published', name='post_status'), default='draft')
    featured_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def save(self):
        if not self.slug:
            self.slug = self.generate_slug()
        db.session.add(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<Post {self.title}>'

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'