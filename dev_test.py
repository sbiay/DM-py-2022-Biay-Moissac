from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # On peut trouver flask.ext.sqlalchemy

app = Flask("Nom")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/libMoissac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# .config est un dict
db = SQLAlchemy(app)

query = db.engine.execute("SELECT * FROM codices")
print(query)
# Vous pouvez remplacer fetchmany par fetchall ou fetchone en supprimant le 2
for x in query.fetchall():
    print(x)
