from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import os
from models import db, Post, Category, AdminUser
from forms import PostForm, CategoryForm, LoginForm
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration (use your real credentials in .env)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

# Original portfolio routes
@app.route('/')
def home():
    # Get latest 3 blog posts for homepage
    latest_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(3).all()
    return render_template('index.html', latest_posts=latest_posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    # General projects data 
    projects = [
        {
            'title': 'Document Scoring System',
            'description': 'Designed automated document analysis and scoring system using advanced AI frameworks',
            'tech': ['Python', 'AWS', 'LLM', 'Machine Learning'],
            'company': 'Azeus Philippines Inc',
            'year': '2024'
        },
        {
            'title': 'RAG Question & Answer System',
            'description': 'Built interactive Q&A system reducing document processing times by 30% through optimization',
            'tech': ['Python', 'RAG', 'LangChain', 'Vector Database', 'LLM'],
            'company': 'Lanex Corporation',
            'year': '2024'
        },
        {
            'title': 'Video Classification System',
            'description': 'Architected automated video analysis system achieving 80% reduction in manual processing',
            'tech': ['TensorFlow', 'PyTorch', 'OpenCV', 'Python'],
            'company': 'Zero Formation UK',
            'year': '2023-2024'
        },
        {
            'title': 'Custom LLM Solutions',
            'description': 'Developed specialized language models achieving 90% accuracy in domain-specific predictions',
            'tech': ['Llama2', 'Mistral', 'Hugging Face', 'PyTorch', 'RAG'],
            'company': 'Avarni',
            'year': '2022-2024'
        },
        {
            'title': 'OCR Document Detection',
            'description': 'Built intelligent document recognition system using computer vision and AI',
            'tech': ['Python', 'OCR', 'Computer Vision', 'LLM'],
            'company': 'Azeus Philippines Inc',
            'year': '2024'
        },
        {
            'title': 'Sentiment Analysis Platform',
            'description': 'Developed text analysis system with API integration for enhanced processing accuracy',
            'tech': ['Python', 'NLP', 'NLTK', 'Flask', 'Django'],
            'company': 'Alliance Software Inc',
            'year': '2018-2020'
        }
    ]
    return render_template('projects.html', projects=projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        subscribe = request.form.get('subscribe')

        # Basic validation
        if not name or not email or not subject or not message:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('contact'))

        # Email sending disabled: prompt to use LinkedIn
        flash('Email sending is currently disabled. For urgent matters, please reach out via LinkedIn: https://www.linkedin.com/in/raeceph-jude-sayson/', 'info')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Blog routes
@app.route('/blog')
def blog_index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    query = Post.query.filter_by(status='published')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    categories = Category.query.all()
    selected_category = db.session.get(Category, category_id) if category_id else None
    
    return render_template('blog/index.html', 
                         posts=posts, 
                         categories=categories, 
                         selected_category=selected_category)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Get related posts from same category
    related_posts = Post.query.filter(
        Post.category_id == post.category_id,
        Post.id != post.id,
        Post.status == 'published'
    ).limit(3).all()
    
    return render_template('blog/post.html', post=post, related_posts=related_posts)

@app.route('/blog/category/<int:category_id>')
def blog_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        abort(404)
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(
        category_id=category_id, 
        status='published'
    ).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    return render_template('blog/category.html', posts=posts, category=category)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'total_posts': Post.query.count(),
        'published_posts': Post.query.filter_by(status='published').count(),
        'draft_posts': Post.query.filter_by(status='draft').count(),
        'categories': Category.query.count()
    }
    
    recent_posts = Post.query.order_by(Post.updated_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_posts=recent_posts)

@app.route('/admin/posts')
@login_required
def admin_posts():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = Post.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    posts = query.order_by(Post.updated_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/posts.html', posts=posts, status_filter=status_filter)

@app.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def admin_post_new():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            status=form.status.data,
            featured_image=form.featured_image.data
        )
        post.save()
        flash('Post created successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_form.html', form=form, title='New Post')

@app.route('/admin/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def admin_post_edit(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.category_id = form.category_id.data if form.category_id.data != 0 else None
        post.status = form.status.data
        post.featured_image = form.featured_image.data
        post.slug = post.generate_slug()
        
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_form.html', form=form, post=post, title='Edit Post')

@app.route('/admin/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def admin_post_delete(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('admin_posts'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/new', methods=['GET', 'POST'])
@login_required
def admin_category_new():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data or '#007bff'
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='New Category')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def admin_category_edit(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        abort(404)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.color = form.color.data or '#007bff'
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, category=category, title='Edit Category')

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def admin_category_delete(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        abort(404)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('admin_categories'))

# Database initialization
def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if doesn't exist
        if not AdminUser.query.first():
            admin = AdminUser(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                email='admin@example.com'
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            
            # Create sample categories
            categories = [
                Category(name='AI & Machine Learning', description='Posts about AI/ML development', color='#007bff'),
                Category(name='Python Development', description='Python programming tutorials and tips', color='#28a745'),
                Category(name='Technology', description='General technology discussions', color='#ffc107'),
                Category(name='Career', description='Career advice and experiences', color='#6f42c1')
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)