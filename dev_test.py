app = Flask("Nom")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////cours-flask/db.sqlite'
db = SQLAlchemy(app)