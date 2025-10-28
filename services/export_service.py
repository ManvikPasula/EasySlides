import os
import tempfile
import logging
from flask import render_template_string
import weasyprint
from jinja2 import Template

logger = logging.getLogger(__name__)

class ExportService:
    def __init__(self):
        self.base_css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
        
        @page {
            size: 11in 6.1875in;
            margin: 0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #1A202C;
            background: #F7FAFC;
            margin: 0;
            padding: 0;
        }
        
        .slide {
            width: 11in;
            height: 6.1875in;
            margin: 0;
            background: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            page-break-after: always;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .slide:last-child {
            page-break-after: avoid;
        }
        
        .slide-title {
            font-family: 'Poppins', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #DE7C00;
            margin-bottom: 0.75rem;
            text-align: center;
        }
        
        .slide-subtitle {
            font-size: 1.1rem;
            color: #2D3748;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .content-title {
            font-family: 'Poppins', sans-serif;
            font-size: 1.8rem;
            font-weight: 600;
            color: #DE7C00;
            margin-bottom: 1rem;
            border-bottom: 3px solid #DE7C00;
            padding-bottom: 0.3rem;
        }
        
        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .slide-content ul {
            list-style: none;
            padding: 0;
        }
        
        .slide-content li {
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            padding-left: 1.75rem;
            position: relative;
        }
        
        .slide-content li:before {
            content: "•";
            color: #DE7C00;
            font-size: 1.3rem;
            position: absolute;
            left: 0;
            top: -0.1rem;
        }
        
        .speaker-notes {
            background: #F7FAFC;
            padding: 0.75rem;
            margin-top: auto;
            border-left: 3px solid #4299E1;
            font-size: 0.8rem;
            color: #2D3748;
        }
        
        .speaker-notes h4 {
            color: #4299E1;
            margin-bottom: 0.3rem;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        /* Enhanced Layout Styles */
        .slide-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .slide-icon svg {
            width: 100%;
            height: 100%;
        }
        
        .title-slide {
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .content-slide-with-image {
            display: flex;
            align-items: flex-start;
            gap: 2rem;
            height: 100%;
        }
        
        .slide-content-area {
            flex: 2;
            display: flex;
            flex-direction: column;
        }
        
        .slide-image-area {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 200px;
        }
        
        .slide-image-area svg {
            width: 100%;
            height: auto;
            max-width: 150px;
            max-height: 150px;
        }
        
        .comparison-slide {
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .comparison-columns {
            flex: 1;
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .comparison-column {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .column-title {
            font-family: 'Poppins', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            color: #DE7C00;
            margin-bottom: 0.75rem;
            text-align: center;
            padding-bottom: 0.25rem;
            border-bottom: 2px solid #DE7C00;
        }
        
        .column-bullets {
            list-style: none;
            padding: 0;
            flex: 1;
        }
        
        .column-bullets li {
            font-size: 1rem;
            margin-bottom: 0.5rem;
            padding-left: 1.2rem;
            position: relative;
            line-height: 1.3;
        }
        
        .column-bullets li:before {
            content: "•";
            color: #DE7C00;
            font-size: 1.1rem;
            position: absolute;
            left: 0;
            top: 0;
        }

        @media print {
            .slide {
                box-shadow: none;
                margin: 0;
            }
        }
        """
    
    def export_html(self, presentation):
        """Export presentation as HTML file"""
        try:
            slides = presentation.get_slides()
            html_content = self._generate_html_content(presentation, slides)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name
            
            logger.info(f"HTML export created: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Error exporting HTML: {str(e)}")
            raise
    
    def export_pdf(self, presentation):
        """Export presentation as PDF file"""
        try:
            slides = presentation.get_slides()
            html_content = self._generate_pdf_html_content(presentation, slides)
            
            # Generate PDF using WeasyPrint
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            weasyprint.HTML(string=html_content).write_pdf(temp_file_path)
            
            logger.info(f"PDF export created: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            raise
    
    def _generate_html_content(self, presentation, slides):
        """Generate complete HTML content for the presentation"""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ presentation.title }}</title>
            <style>
                {{ css }}
                
                /* Navigation controls */
                .nav-controls {
                    position: fixed;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    display: flex;
                    gap: 20px;
                    align-items: center;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 10px 20px;
                    border-radius: 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 1000;
                }
                
                .nav-button {
                    background: #DE7C00;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                }
                
                .nav-button:hover {
                    background: #B45309;
                    transform: scale(1.05);
                }
                
                .nav-button:disabled {
                    background: #CBD5E0;
                    cursor: not-allowed;
                    transform: scale(1);
                }
                
                .slide-counter {
                    font-weight: 500;
                    color: #4A5568;
                    padding: 0 10px;
                }
                
                /* Notes toggle button */
                .notes-toggle {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #4299E1;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
                    z-index: 1000;
                    transition: all 0.3s ease;
                }
                
                .notes-toggle:hover {
                    background: #3182CE;
                    transform: scale(1.05);
                }
                
                /* Hide slides by default except first */
                .slide {
                    display: none;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                }
                
                .slide.active {
                    display: flex;
                }
                
                /* Body styling for centered presentation */
                body {
                    height: 100vh;
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                /* Speaker notes visibility */
                .speaker-notes.hidden {
                    display: none !important;
                }
                
                /* Keyboard hint */
                .keyboard-hint {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(255, 255, 255, 0.9);
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-size: 12px;
                    color: #718096;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="keyboard-hint">
                Use ← → arrow keys or buttons to navigate
            </div>
            
            {% for slide in slides %}
            <div class="slide {% if loop.first %}active{% endif %}" data-slide="{{ loop.index }}" data-layout="{{ slide.layout if slide.layout else 'text_only' }}">
                {% if slide.type == 'title' or slide.type == 'ending' %}
                    <div class="slide-content title-slide">
                        {% if slide.svg_icon %}
                        <div class="slide-icon">
                            {{ slide.svg_icon|safe }}
                        </div>
                        {% endif %}
                        <h1 class="slide-title">{{ slide.title }}</h1>
                        {% if slide.subtitle %}
                        <h2 class="slide-subtitle">{{ slide.subtitle }}</h2>
                        {% endif %}
                    </div>
                {% elif slide.type == 'comparison' %}
                    <div class="slide-content comparison-slide">
                        <h2 class="content-title">{{ slide.title }}</h2>
                        <div class="comparison-columns">
                            <div class="comparison-column">
                                {% if slide.left_column %}
                                <h3 class="column-title">{{ slide.left_column.title }}</h3>
                                <ul class="column-bullets">
                                    {% for item in slide.left_column.content %}
                                    <li>{{ item }}</li>
                                    {% endfor %}
                                </ul>
                                {% endif %}
                            </div>
                            <div class="comparison-column">
                                {% if slide.right_column %}
                                <h3 class="column-title">{{ slide.right_column.title }}</h3>
                                <ul class="column-bullets">
                                    {% for item in slide.right_column.content %}
                                    <li>{{ item }}</li>
                                    {% endfor %}
                                </ul>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                {% else %}
                    {% if slide.layout == 'text_with_image' and slide.svg_icon %}
                    <div class="slide-content content-slide-with-image">
                        <div class="slide-content-area">
                            <h2 class="content-title">{{ slide.title }}</h2>
                            {% if slide.content %}
                            <ul>
                                {% for item in slide.content %}
                                <li>{{ item }}</li>
                                {% endfor %}
                            </ul>
                            {% endif %}
                        </div>
                        <div class="slide-image-area">
                            {{ slide.svg_icon|safe }}
                        </div>
                    </div>
                    {% else %}
                    <div class="slide-content">
                        <h2 class="content-title">{{ slide.title }}</h2>
                        {% if slide.content %}
                        <ul>
                            {% for item in slide.content %}
                            <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    {% endif %}
                {% endif %}
                
                {% if slide.speaker_notes %}
                <div class="speaker-notes">
                    <h4>Speaker Notes:</h4>
                    <p>{{ slide.speaker_notes }}</p>
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <!-- Navigation Controls -->
            <div class="nav-controls">
                <button class="nav-button" id="prevBtn" onclick="changeSlide(-1)">← Previous</button>
                <span class="slide-counter">
                    <span id="currentSlide">1</span> / {{ slides|length }}
                </span>
                <button class="nav-button" id="nextBtn" onclick="changeSlide(1)">Next →</button>
            </div>
            
            <!-- Notes Toggle Button -->
            <button class="notes-toggle" onclick="toggleNotes()">
                <span id="notesToggleText">Hide Notes</span>
            </button>
            
            <script>
                let currentSlideIndex = 1;
                const totalSlides = {{ slides|length }};
                let notesVisible = true;
                
                function showSlide(n) {
                    const slides = document.querySelectorAll('.slide');
                    
                    // Wrap around
                    if (n > totalSlides) currentSlideIndex = 1;
                    if (n < 1) currentSlideIndex = totalSlides;
                    
                    // Hide all slides
                    slides.forEach(slide => slide.classList.remove('active'));
                    
                    // Show current slide
                    slides[currentSlideIndex - 1].classList.add('active');
                    
                    // Update counter
                    document.getElementById('currentSlide').textContent = currentSlideIndex;
                    
                    // Update button states
                    document.getElementById('prevBtn').disabled = currentSlideIndex === 1;
                    document.getElementById('nextBtn').disabled = currentSlideIndex === totalSlides;
                }
                
                function changeSlide(n) {
                    currentSlideIndex += n;
                    showSlide(currentSlideIndex);
                }
                
                function toggleNotes() {
                    const notes = document.querySelectorAll('.speaker-notes');
                    const toggleBtn = document.getElementById('notesToggleText');
                    
                    notesVisible = !notesVisible;
                    
                    notes.forEach(note => {
                        if (notesVisible) {
                            note.classList.remove('hidden');
                            toggleBtn.textContent = 'Hide Notes';
                        } else {
                            note.classList.add('hidden');
                            toggleBtn.textContent = 'Show Notes';
                        }
                    });
                }
                
                // Keyboard navigation
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowLeft') changeSlide(-1);
                    if (e.key === 'ArrowRight') changeSlide(1);
                    if (e.key === 'n' || e.key === 'N') toggleNotes();
                });
                
                // Initialize
                showSlide(1);
                
                // Hide keyboard hint after 5 seconds
                setTimeout(() => {
                    const hint = document.querySelector('.keyboard-hint');
                    if (hint) hint.style.display = 'none';
                }, 5000);
            </script>
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(
            presentation=presentation,
            slides=slides,
            css=self.base_css
        )
    
    def _generate_pdf_html_content(self, presentation, slides):
        """Generate HTML content specifically for PDF export"""
        pdf_css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
        
        @page {
            size: 11in 6.1875in;
            margin: 0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #1A202C;
            margin: 0;
            padding: 0;
        }
        
        .slide {
            width: 11in;
            height: 6.1875in;
            margin: 0;
            background: white;
            padding: 1.5in 1in;
            page-break-after: always;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }
        
        .slide:last-child {
            page-break-after: avoid;
        }
        
        .title-slide {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            text-align: center;
        }
        
        .slide-title {
            font-family: 'Poppins', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            color: #DE7C00;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .slide-subtitle {
            font-size: 1.5rem;
            color: #2D3748;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .content-title {
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            font-weight: 600;
            color: #DE7C00;
            margin-bottom: 1.5rem;
            border-bottom: 4px solid #DE7C00;
            padding-bottom: 0.5rem;
        }
        
        .content-slide {
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .slide-content ul {
            list-style: none;
            padding: 0;
        }
        
        .slide-content li {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-left: 2rem;
            position: relative;
            line-height: 1.6;
        }
        
        .slide-content li:before {
            content: "•";
            color: #DE7C00;
            font-size: 1.8rem;
            position: absolute;
            left: 0;
            top: 0;
        }
        """
        
        pdf_html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{{ presentation.title }}</title>
            <style>
                {{ css }}
            </style>
        </head>
        <body>
            {% for slide in slides %}
            <div class="slide">
                {% if slide.type == 'title' %}
                    <div class="title-slide">
                        <h1 class="slide-title">{{ slide.title }}</h1>
                        {% if slide.subtitle %}
                        <h2 class="slide-subtitle">{{ slide.subtitle }}</h2>
                        {% endif %}
                    </div>
                {% else %}
                    <div class="content-slide">
                        <h2 class="content-title">{{ slide.title }}</h2>
                        <div class="slide-content">
                            {% if slide.content %}
                            <ul>
                                {% for item in slide.content %}
                                <li>{{ item }}</li>
                                {% endfor %}
                            </ul>
                            {% endif %}
                        </div>
                    </div>
                {% endif %}
            </div>
            {% endfor %}
        </body>
        </html>
        """
        
        template = Template(pdf_html_template)
        return template.render(
            presentation=presentation,
            slides=slides,
            css=pdf_css
        )
