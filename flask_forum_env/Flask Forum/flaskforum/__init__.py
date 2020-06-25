from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SECRET_KEY'] = '482ddd77134754f904a4059804e9cd81' #security for forms 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #create database file
#app.config['SQLALCHEMY_ECHO'] = True # display all sql statements been made 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login' #any routes marked with @login_required will return to the login page which will also have '?next=' attached to the url which will direct you to that page with the next parameter
# configurations to migrate database
migrate = Migrate(app, db) 
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# import blueprint instance
from flaskforum.users.routes import users 
from flaskforum.forums.routes import forums
from flaskforum.main.routes import main
#register the blueprint to the app instance
app.register_blueprint(users) 
app.register_blueprint(forums)
app.register_blueprint(main)