from flask import Flask
from flask_login import LoginManager
from .model import db, init_app

def create_app():
    app = Flask(__name__, template_folder='Templates')

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.foodsqlite'
    

    init_app(app)  # Use the modified init_app function

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .model import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import routes and blueprints
    from .routes import routes as main_blueprint
    from .auth import auth as auth_blueprint
    from .food import food_blueprint
    from .recommend import recommend_blueprint
    from .nutrients import nutrients_blueprint
    from .grocery import grocery_blueprint
    from .mealplan import mealplan_blueprint

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(food_blueprint)
    app.register_blueprint(recommend_blueprint)
    app.register_blueprint(nutrients_blueprint)
    app.register_blueprint(grocery_blueprint)
    app.register_blueprint(mealplan_blueprint)

    return app
