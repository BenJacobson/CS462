from main_flask import db, User

db.create_all()

first_user = User(foursquareid=401184008, firstname='Ben', lastname='Jacobson', email='bentjacobson@gmail.com')

db.session.add(first_user)
db.session.commit()
