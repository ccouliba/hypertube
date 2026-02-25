"""Database instance - shared across all domains"""
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
