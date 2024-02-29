from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Import db from models.py
from .model import db

#food imports
from flask import Blueprint, render_template, redirect, request, session, abort, jsonify

from recipegeneration.output import output
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import json
import requests  # Add this import

routes = Blueprint('routes', __name__)

@routes.route('/',methods=['GET'])
@login_required
def home():
    return render_template('home.html')

@routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


#about page
@routes.route('/about',methods=['GET'])
@login_required
def about():
    return render_template('about.html')
