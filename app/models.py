from app import db
from datetime import datetime
from enum import Enum

class SplitType(str, Enum):
    EQUAL = 'equal'
    PERCENTAGE = 'percentage'
    EXACT = 'exact'

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    paid_by = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    split_type = db.Column(db.String(20), default=SplitType.EQUAL)
    category = db.Column(db.String(100), nullable=True)
    
    # Relationship with participants
    participants = db.relationship('Participant', backref='expense', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'paid_by': self.paid_by,
            'date': self.date.isoformat(),
            'split_type': self.split_type,
            'category': self.category,
            'participants': [p.to_dict() for p in self.participants]
        }

class Participant(db.Model):
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    share = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'name': self.name,
            'share': self.share
        }
