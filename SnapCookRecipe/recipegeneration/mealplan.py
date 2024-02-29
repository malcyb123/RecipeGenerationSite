from flask import Blueprint, render_template, request, current_app, jsonify, url_for, redirect, abort
from flask_login import login_required, current_user
from datetime import datetime
import requests
import re
from recipegeneration.model import Food, db, Log
mealplan_blueprint = Blueprint('mealplan_blueprint', __name__)

from sqlalchemy import desc

@mealplan_blueprint.route('/mealplan/index')
@login_required
def index():
    logs = Log.query.order_by(Log.date.desc()).all()

    log_dates = []

    for log in logs:
        proteins = 0
        carbs = 0
        fats = 0
        calories = 0

        for food in log.foods:
            proteins += int(food.proteins)
            carbs += int(food.carbs)
            fats += int(food.fats)
            calories += int(food.calories)

        log_dates.append({
            'log_date' : log,
            'proteins' : proteins,
            'carbs' : carbs,
            'fats' : fats,
            'calories' : calories
        })

    # Assuming you want to pass the first log to the template
    first_log = logs[0] if logs else None

    return render_template('index.html', log_dates=log_dates, log=first_log)


#LOG FOR DATE
@mealplan_blueprint.route('/mealplan/create_log', methods=['POST'])
def create_log():
    date = request.form.get('date')

    log = Log(date=datetime.strptime(date, '%Y-%m-%d'))

    db.session.add(log)
    db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log.id))

@mealplan_blueprint.route('/mealplan/add')
@login_required
def add():
      # Fetch food items for the current user
    current_user_foods = Food.query.filter_by(user_id=current_user.id).all()
    #foods = Food.query.all()
    logs = Log.query.all()  # Fetch all logs

    return render_template('add.html', foods=current_user_foods, food=None, logs=logs)  # Pass logs to the template context



@mealplan_blueprint.route('/mealplan/add', methods=['POST'])
@login_required
def add_post():
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    food_id = request.form.get('food-id')

    if food_id:
        food = Food.query.get_or_404(food_id)
        food.name = food_name
        food.proteins = proteins
        food.carbs = carbs
        food.fats = fats

    else:
        new_food = Food(
            name=food_name,
            proteins=proteins, 
            carbs=carbs, 
            fats=fats,
             user_id=current_user.id  # Set the user_id attribute to the current user's id
        )
    
        db.session.add(new_food)

    db.session.commit()
    return redirect(url_for('mealplan_blueprint.add'))
# EDIT

@mealplan_blueprint.route('/edit_food/<int:food_id>')
def edit_food(food_id):
    food = Food.query.get(food_id)
    # Ensure the food belongs to the current user
    if food.user_id != current_user.id:
        abort(403)  # Return a 403 error if the food does not belong to the current user
    foods = Food.query.filter_by(user_id=current_user.id).all()
    return render_template('add.html', food=food, foods=foods)

# DELETE
@mealplan_blueprint.route('/delete_food/<int:food_id>')
def delete_food(food_id):
    food = Food.query.get(food_id)
    # Ensure the food belongs to the current user
    if food.user_id != current_user.id:
        abort(403)  # Return a 403 error if the food does not belong to the current user
    if food:
        db.session.delete(food)
        db.session.commit()
        return redirect(url_for('mealplan_blueprint.add'))
    else:
        abort(404)  # Return a 404 error if the food item does not exist

@mealplan_blueprint.route('/mealplan/view/<int:log_id>')
@login_required
def view(log_id):
    log = Log.query.get_or_404(log_id)

    foods = Food.query.all()

    totals = {
        'protein' : 0,
        'carbs' : 0,
        'fat' : 0,
        'calories' : 0
    }

    for food in log.foods:
        totals['protein'] += int(food.proteins)
        totals['carbs'] += int(food.carbs)
        totals['fat'] += int(food.fats)
        totals['calories'] += int(food.calories)

    return render_template('view.html', foods=foods, log=log, totals=totals)

@mealplan_blueprint.route('/mealplan/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)

    selected_food = request.form.get('food-select')

    food = Food.query.get(int(selected_food))

    log.foods.append(food)
    db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log_id))

@mealplan_blueprint.route('/mealplan/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log_id))
