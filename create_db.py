from app import db, User

admin = User('admin', 'password')
user1 = User('user1', 'password')
user2 = User('user2', 'password')

db.session.add(admin)
db.session.add(user1)
db.session.add(user2)

db.session.commit()

print('User table entries:\n{}'.format(User.query.all()))
