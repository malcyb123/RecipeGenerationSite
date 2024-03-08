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
    # Fetch logs for the current user
    logs = Log.query.filter_by(user_id=current_user.id).order_by(Log.date.desc()).all()

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


@mealplan_blueprint.route('/mealplan/create_log', methods=['POST'])
def create_log():
    date = request.form.get('date')

    log = Log(date=datetime.strptime(date, '%Y-%m-%d'), user_id=current_user.id)

    db.session.add(log)
    db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log.id))

@mealplan_blueprint.route('/mealplan/add')
@login_required
def add():
    # Fetch food items for the current user
    current_user_foods = Food.query.filter_by(user_id=current_user.id).all()
    # Fetch logs for the current user
    current_user_logs = Log.query.filter_by(user_id=current_user.id).all()

    return render_template('add.html', foods=current_user_foods, logs=current_user_logs, food=None)

@mealplan_blueprint.route('/mealplan/add', methods=['POST'])
@login_required
def add_post():
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    food_id = request.form.get('food-id')

    # If food_id is provided, it means the user is editing an existing food item
    if food_id:
        food = Food.query.get_or_404(food_id)

        # Check if the food name is being changed to another existing food name
        existing_food = Food.query.filter_by(name=food_name, user_id=current_user.id).first()
        if existing_food and existing_food.id != food.id:
            return "Another food with the same name already exists.", 409  # HTTP status code 409 for Conflict

        # Update the existing food item
        food.name = food_name
        food.proteins = proteins if proteins else 0  # Ensure proteins is set to 0 if not provided
        food.carbs = carbs if carbs else 0  # Ensure carbs is set to 0 if not provided
        food.fats = fats if fats else 0  # Ensure fats is set to 0 if not provided
    else:
        # Create a new food item
        new_food = Food(
            name=food_name,
            proteins=proteins if proteins else 0, 
            carbs=carbs if carbs else 0, 
            fats=fats if fats else 0,
            user_id=current_user.id
        )
        db.session.add(new_food)

    db.session.commit()
    return redirect(url_for('mealplan_blueprint.add'))


@mealplan_blueprint.route('/edit_food/<int:food_id>')
def edit_food(food_id):
    food = Food.query.get(food_id)
    # Ensure the food belongs to the current user
    if food.user_id != current_user.id:
        abort(403)  # Return a 403 error if the food does not belong to the current user
    foods = Food.query.filter_by(user_id=current_user.id).all()
    return render_template('add.html', food=food, foods=foods)


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

    foods = Food.query.filter_by(user_id=current_user.id).all()

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

    # Ensure the selected food belongs to the current user
    food = Food.query.filter_by(id=int(selected_food), user_id=current_user.id).first()

    if food:
        log.foods.append(food)
        db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log_id))


@mealplan_blueprint.route('/mealplan/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.filter_by(id=food_id, user_id=current_user.id).first()

    if food:
        log.foods.remove(food)
        db.session.commit()

    return redirect(url_for('mealplan_blueprint.view', log_id=log_id))
