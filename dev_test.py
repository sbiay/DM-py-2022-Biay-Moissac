from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("lib-moissac")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

query = db.engine.execute('SELECT * FROM codices')
print(query)
for x in query.fetchall():
    for donnes in x:
        print(donnes)
