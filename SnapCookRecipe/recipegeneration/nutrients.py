from flask import Blueprint, request, render_template
import requests

nutrients_blueprint = Blueprint('nutrients_blueprint', __name__)

@nutrients_blueprint.route('/nutrients_value', methods=['GET', 'POST'])
def nutrients_value():
    if request.method == 'POST':
        # Get the food name from the form
        food_name = request.form.get('food_name')
        
        # Send a request to Spoonacular API to search for the food
        response = requests.get("https://api.spoonacular.com/recipes/complexSearch", params={'query': food_name, 'apiKey': "773db486d12d4950abb24b757a38f994"})
        data = response.json()
        print("API Response:", data)  # Debugging
        # Extract the nutrient information if available
        nutrients = None
        if data:
            for item in data:
                if 'nutrition' in item and 'nutrients' in item['nutrition']:
                    nutrients = item['nutrition']['nutrients']
                    break  # Stop iterating once nutrients are found
        print("Nutrient Data:", nutrients)  # Debugging
        # Handle case when no nutrients are found
        if nutrients is None:
            error_message = f"No nutrient information found for {food_name}."
            return render_template('nutrients.html', food_name=food_name, error_message=error_message)
        
        return render_template('nutrients.html', food_name=food_name, nutrients=nutrients)
    else:
        return render_template('nutrients.html')
