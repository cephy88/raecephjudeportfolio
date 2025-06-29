from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)