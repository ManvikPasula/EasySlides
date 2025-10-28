# EasySlides

## Overview

This is a Flask-based web application that converts voice recordings into professional presentation slides using AI. Users can either upload audio files or record directly in their browser, and the system automatically transcribes the audio and generates structured slide content using Anthropic's Claude AI. The application supports multiple export formats including HTML and PDF.

## User Preferences

Preferred communication style: Simple, everyday language.
Presentation titles: Generate meaningful titles based on content instead of generic "Voice Recording Presentation".

## System Architecture

### Web Framework
- **Flask**: Lightweight web framework serving as the main application server
- **SQLAlchemy**: ORM for database operations with declarative base model
- **Jinja2**: Template engine for rendering HTML views
- **Bootstrap 5**: Frontend CSS framework for responsive design

### Database Layer
- **SQLite**: Default database for development (configurable via DATABASE_URL)
- **Models**: Single `Presentation` model storing audio files, transcripts, and slide data
- **JSON Storage**: Slides data stored as JSON text in the database for flexibility

### Audio Processing Pipeline
- **Speech Recognition**: Google Web Speech API for audio-to-text transcription
- **PyDub**: Audio format conversion and processing
- **File Upload**: Secure file handling with size limits (50MB) and format validation
- **Real-time Recording**: Browser-based voice recording with live transcription

### AI Integration
- **Anthropic Claude**: Uses claude-sonnet-4-20250514 model for slide generation
- **Structured Output**: AI generates JSON-formatted slide content with titles, bullets, and formatting
- **Content Processing**: Intelligent parsing of transcripts into presentation-ready content

### Export System
- **HTML Export**: Template-based slide rendering for web viewing
- **PDF Generation**: WeasyPrint integration for high-quality PDF output
- **Custom Styling**: Professional slide templates with Inter and Poppins fonts

### Frontend Architecture
- **Progressive Enhancement**: Works with basic uploads, enhanced with JavaScript
- **Real-time Features**: Live audio recording and transcription display
- **Responsive Design**: Mobile-friendly interface with Bootstrap components
- **Interactive Controls**: Slide navigation, preview, and export options
- **Smooth Transitions**: Professional slide transition animations with CSS transforms and JavaScript

### Security & Configuration
- **Environment Variables**: API keys and database URLs stored securely
- **File Security**: Filename sanitization and upload directory isolation
- **Session Management**: Flask sessions with configurable secret keys
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

## External Dependencies

### AI Services
- **Anthropic API**: Claude AI for slide content generation (requires ANTHROPIC_API_KEY)
- **Google Speech Recognition**: Free speech-to-text service for audio transcription

### Audio Processing
- **SpeechRecognition**: Python library for various speech recognition engines
- **PyDub**: Audio manipulation and format conversion
- **Web Speech API**: Browser-based real-time voice recording

### Export & Rendering
- **WeasyPrint**: HTML to PDF conversion engine
- **Google Fonts**: Inter and Poppins font families for professional typography

### Frontend Libraries
- **Bootstrap 5**: CSS framework and components
- **Feather Icons**: Lightweight icon library
- **JavaScript Speech API**: Browser native speech recognition

### Development Tools
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: WSGI utilities and file handling
- **Jinja2**: Template rendering engine