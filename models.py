from app import db
from datetime import datetime
import json

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    audio_filename = db.Column(db.String(255))
    transcript = db.Column(db.Text)
    slides_data = db.Column(db.Text)  # JSON string of slides
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='processing')  # processing, completed, error
    
    def get_slides(self):
        """Return slides data as Python object"""
        if self.slides_data:
            return json.loads(self.slides_data)
        return []
    
    def set_slides(self, slides):
        """Set slides data from Python object"""
        self.slides_data = json.dumps(slides)
