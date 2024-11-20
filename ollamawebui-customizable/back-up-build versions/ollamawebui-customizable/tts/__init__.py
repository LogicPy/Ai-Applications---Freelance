# tts/__init__.py

from flask import Blueprint
from app import db, migrate  # Assuming 'app' is now a package

tts_bp = Blueprint('tts', __name__)

from .xtts import send_tts_request_xtts
