from main_flask import db, User

db.create_all()

db.session.commit()