from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required
import requests
import re
import json

grocery_blueprint = Blueprint('grocery_blueprint', __name__)

#GROCERY GENERATE
with open("recipegeneration/data/recipes1.json", "r") as file:
    recipes_data = json.load(file)
@grocery_blueprint.route('/grocery', methods=['GET', 'POST'])
def grocery():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            print("Received JSON data:", data)  # Add this line for debugging
            recipe_name = data.get('recipe_name')

            # Check if the recipe name is in the loaded recipe data
            if recipe_name in recipes_data:
                grocery_list = [ingredient["name"] for ingredient in recipes_data[recipe_name]]
                return jsonify({'grocery_list': grocery_list})
            else:
                return jsonify({'error': 'Recipe not found'}), 404
        else:
            return jsonify({'error': 'No JSON data received'}), 400

    # Handle GET request
    return render_template('grocery.html')

