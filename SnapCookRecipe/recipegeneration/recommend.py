from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required
import requests
import re

recommend_blueprint = Blueprint('recommend_blueprint', __name__)

api_key = "773db486d12d4950abb24b757a38f994"

# Function to get recipe details using the recipe ID
def get_recipe_details(recipe_id):
 #   api_key = 'cf26853d1bdd42f08151d6686b79f596' # Replace with your Spoonacular API key
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.status_code)
        return None

# Function to generate a grocery list from recipe details
def generate_grocery_list(recipe):
    ingredients = [ingredient['name'] for ingredient in recipe['extendedIngredients']]
    return ingredients

# Function to filter out non-food words from recipe titles
def filter_title(title):
    # Define a list of non-food words you want to filter out
    non_food_words = ['recipe', 'dish', 'meal', 'bread', 'cake', 'cookies', 'biscuits', 'pies', 'muffins', 'scones']  # Add more non-food words as needed

    # Compile a regular expression pattern to match any of the non-food words
    pattern = re.compile('|'.join(non_food_words), re.IGNORECASE)

    # Replace non-food words with an empty string in the title
    filtered_title = re.sub(pattern, '', title)

    # Remove leading and trailing whitespace
    filtered_title = filtered_title.strip()

    return filtered_title

# Function to recommend a recipe based on provided ingredients
def recommend_recipe(ingredients, cuisine='indian'):
   # api_key = 'cf26853d1bdd42f08151d6686b79f596'  # Replace with your Spoonacular API key
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={",".join(ingredients)}&cuisine={cuisine}&number=1&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return recipe data
    else:
        print('Error:', response.status_code)
        return None
    
# Function to filter out non-food words from recipe instructions
def filter_instructions(instructions):
    if instructions:
        # Remove the word "blog" from instructions
        filtered_instructions = instructions.replace('blog', '<a href="http://')
        return filtered_instructions
    return None

# Route for recommending recipe instructions
@recommend_blueprint.route('/recipe_recommend', methods=['GET', 'POST'])
@login_required
def recipe_recommend():
    if request.method == 'POST':
        # Get ingredients from form
        manual_ingredients = request.form.get('manual_ingredients')
        predefined_ingredients = request.form.getlist('ingredients[]')

        # Initialize ingredients list
        ingredients = set()

        # Process manual ingredients
        if manual_ingredients:
            ingredients.update([ing.strip() for ing in manual_ingredients.split(',')])

        # Process predefined ingredients
        if predefined_ingredients:
            predefined_set = set(predefined_ingredients)  # Convert to set to remove duplicates
            ingredients.update(predefined_set)  # Update the main set with unique predefined ingredients
        
        # Remove duplicates by converting the list to a set and back to a list
        ingredients = list(set(ingredients))

        # Check if any ingredients are provided
        if not ingredients:
            return render_template('instructions.html', error='Please provide ingredient names.')
        

        # Recommend recipe based on ingredients
        recipe_data = recommend_recipe(ingredients)
        if recipe_data:
            # Filter out non-food words from recipe titles
            title = filter_title(recipe_data[0]['title'])
            if title:
                recipe_id = recipe_data[0]['id']
                recipe_details = get_recipe_details(recipe_id)
                if recipe_details:
                    ingredients_list = generate_grocery_list(recipe_details)
                    instructions = recipe_details['instructions']  # Instructions are already HTML
                    return render_template('instructions.html', title=title, ingredients=ingredients_list, instructions=instructions, recipe_id=recipe_id)
                else:
                    return render_template('instructions.html', error='Recipe details not found.')
            else:
                return render_template('instructions.html', error='No suitable recipes found for the provided ingredients.')
        else:
            return render_template('instructions.html', error='No recipes found for the provided ingredients.')

    return render_template('instructions.html', error=None)

# Add this route definition
@recommend_blueprint.route('/get_cooking_time', methods=['GET'])
@login_required
def get_cooking_time():
    # Fetch the cooking time from Spoonacular API
    recipe_id = request.args.get('recipe_id')
 #   api_key = 'cf26853d1bdd42f08151d6686b79f596'  # Replace with your Spoonacular API key
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=false&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        recipe_info = response.json()
        cooking_time = recipe_info.get('readyInMinutes', 'Unknown')
        return jsonify({'cookingTime': cooking_time})
    else:
        return jsonify({'error': 'Failed to fetch cooking time'}), 500
    
#NUTRIENTS
@recommend_blueprint.route('/get_nutrients', methods=['GET'])
@login_required
def get_nutrients():
    recipe_id = request.args.get('recipe_id')
 #   api_key = 'cf26853d1bdd42f08151d6686b79f596'
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json?apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        nutrient_info = response.json()
        nutrients = nutrient_info.get('nutrients', [])
        
        # Find the nutrient data for carbohydrates, protein, calories, and fat
        carbohydrates = next((nutrient for nutrient in nutrients if nutrient['name'] == 'Carbohydrates'), None)
        protein = next((nutrient for nutrient in nutrients if nutrient['name'] == 'Protein'), None)
        calories = next((nutrient for nutrient in nutrients if nutrient['name'] == 'Calories'), None)
        fat = next((nutrient for nutrient in nutrients if nutrient['name'] == 'Fat'), None)
        
        # Modify the JSON format for each nutrient
        modified_nutrients = {}
        if carbohydrates:
            modified_nutrients['carbohydrates'] = {
                "amount": carbohydrates["amount"],
                "unit": carbohydrates["unit"],
                "percent_of_daily_needs": carbohydrates["percentOfDailyNeeds"]
            }
        if protein:
            modified_nutrients['protein'] = {
                "amount": protein["amount"],
                "unit": protein["unit"],
                "percent_of_daily_needs": protein["percentOfDailyNeeds"]
            }
        if calories:
            modified_nutrients['calories'] = {
                "amount": calories["amount"],
                "unit": calories["unit"],
                "percent_of_daily_needs": calories["percentOfDailyNeeds"]
            }
        if fat:
            modified_nutrients['fat'] = {
                "amount": fat["amount"],
                "unit": fat["unit"],
                "percent_of_daily_needs": fat["percentOfDailyNeeds"]
            }
        
        # Convert the modified nutrients to strings
        for nutrient_name, nutrient_data in modified_nutrients.items():
            modified_nutrients[nutrient_name]["amount"] = str(modified_nutrients[nutrient_name]["amount"])
            modified_nutrients[nutrient_name]["percent_of_daily_needs"] = str(modified_nutrients[nutrient_name]["percent_of_daily_needs"])
        
        return jsonify(modified_nutrients)
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch nutrient information: {e}'}), 500
