from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_organisation = db.Table('user_organisation',
    db.Column('user_id', db.String(80), db.ForeignKey('user.userId'), primary_key=True),
    db.Column('organisation_id', db.String(80), db.ForeignKey('organisation.orgId'), primary_key=True)
)

class User(db.Model):
    userId = db.Column(db.String(80), unique=True, primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80))

    def __repr__(self):
        return f'<User {self.firstName} {self.lastName}>'

class Organisation(db.Model):
    orgId = db.Column(db.String(80), unique=True, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Organisation {self.name}>'