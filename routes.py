import os
import uuid
from flask import render_template, request, jsonify, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from app import app, db
from models import Presentation
from services.audio_processor import AudioProcessor
from services.slide_generator import SlideGenerator
from services.export_service import ExportService
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a valid audio file.'}), 400
        
        # Create upload folder if it doesn't exist
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Create presentation record
        presentation = Presentation(
            title=f"Presentation {filename}",
            audio_filename=filename,
            status='processing'
        )
        db.session.add(presentation)
        db.session.commit()
        
        # Process audio in background (for now, process immediately)
        success = process_audio_file(presentation.id, filepath)
        
        if success:
            return jsonify({
                'success': True,
                'presentation_id': presentation.id,
                'message': 'Audio uploaded and processed successfully'
            })
        else:
            presentation.status = 'error'
            db.session.commit()
            return jsonify({'error': 'Failed to process audio file'}), 500
            
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/process_transcript', methods=['POST'])
def process_transcript():
    try:
        data = request.get_json()
        transcript = data.get('transcript', '').strip()
        
        if not transcript:
            return jsonify({'error': 'No transcript provided', 'success': False}), 400
        
        if len(transcript.split()) < 10:
            return jsonify({'error': 'Transcript too short. Please provide at least 10 words.', 'success': False}), 400
        
        # Generate a meaningful title based on transcript content
        from services.slide_generator import SlideGenerator
        slide_generator = SlideGenerator()
        meaningful_title = slide_generator.generate_presentation_title(transcript)
        
        # Create presentation record
        presentation = Presentation(
            title=meaningful_title,
            transcript=transcript,
            status='processing'
        )
        db.session.add(presentation)
        db.session.commit()
        
        # Generate slides
        success = generate_slides_for_presentation(presentation.id)
        
        if success:
            return jsonify({
                'success': True,
                'presentation_id': presentation.id,
                'message': 'Slides generated successfully'
            })
        else:
            presentation.status = 'error'
            db.session.commit()
            return jsonify({'error': 'Failed to generate slides. Please try again with a shorter transcript or check your API key.', 'success': False}), 500
            
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request', 'success': False}), 500

@app.route('/presentation/<int:presentation_id>')
def view_presentation(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    
    if presentation.status == 'processing':
        flash('Presentation is still being processed. Please wait...', 'info')
        return redirect(url_for('index'))
    elif presentation.status == 'error':
        flash('An error occurred while processing your presentation.', 'error')
        return redirect(url_for('index'))
    
    slides = presentation.get_slides()
    return render_template('slides_preview.html', presentation=presentation, slides=slides)

@app.route('/export/<int:presentation_id>/<format>')
def export_presentation(presentation_id, format):
    presentation = Presentation.query.get_or_404(presentation_id)
    
    if presentation.status != 'completed':
        return jsonify({'error': 'Presentation not ready for export'}), 400
    
    export_service = ExportService()
    
    try:
        if format == 'html':
            file_path = export_service.export_html(presentation)
            return send_file(file_path, as_attachment=True, download_name=f"{presentation.title}.html")
        elif format == 'pdf':
            file_path = export_service.export_pdf(presentation)
            return send_file(file_path, as_attachment=True, download_name=f"{presentation.title}.pdf")
        else:
            return jsonify({'error': 'Invalid export format'}), 400
    except Exception as e:
        logger.error(f"Error exporting presentation: {str(e)}")
        return jsonify({'error': 'Failed to export presentation'}), 500

def process_audio_file(presentation_id, filepath):
    """Process audio file and generate slides"""
    try:
        presentation = Presentation.query.get(presentation_id)
        if not presentation:
            return False
        
        # Transcribe audio
        audio_processor = AudioProcessor()
        transcript = audio_processor.transcribe_audio(filepath)
        
        if not transcript:
            logger.error("Failed to transcribe audio")
            return False
        
        presentation.transcript = transcript
        db.session.commit()
        
        # Generate slides
        return generate_slides_for_presentation(presentation_id)
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        return False

def generate_slides_for_presentation(presentation_id):
    """Generate slides from transcript"""
    try:
        presentation = Presentation.query.get(presentation_id)
        if not presentation or not presentation.transcript:
            return False
        
        # Generate slides using Anthropic
        slide_generator = SlideGenerator()
        slides = slide_generator.generate_slides(presentation.transcript)
        
        if not slides:
            logger.error("Failed to generate slides")
            return False
        
        presentation.set_slides(slides)
        presentation.status = 'completed'
        db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating slides: {str(e)}")
        return False

@app.route('/api/presentations/<int:presentation_id>/status')
def get_presentation_status(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    return jsonify({
        'status': presentation.status,
        'title': presentation.title
    })

@app.route('/presentation/<int:presentation_id>/update', methods=['POST'])
def update_presentation(presentation_id):
    """Update presentation slides content"""
    try:
        presentation = Presentation.query.get_or_404(presentation_id)
        data = request.get_json()
        
        if 'slides' not in data:
            return jsonify({'error': 'No slides data provided'}), 400
        
        # Update the slides data
        presentation.set_slides(data['slides'])
        db.session.commit()
        
        logger.info(f"Updated presentation {presentation_id} with edited slides")
        return jsonify({
            'success': True,
            'message': 'Presentation updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating presentation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update presentation'}), 500
