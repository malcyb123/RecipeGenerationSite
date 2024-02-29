from flask import Blueprint, render_template, request, current_app
from .output import output
import os
from flask_login import login_required
food_blueprint = Blueprint('food_blueprint', __name__)

@food_blueprint.route('/', methods=['POST', 'GET'])
@login_required
def predict():
    try:
        imagefile = request.files['imagefile']
        print("Received image file:", imagefile.filename)
        image_path = os.path.join(current_app.root_path, 'static', 'images', imagefile.filename)
        print("Image path:", image_path)
        imagefile.save(image_path)
        print("Image saved successfully.")
        img = "/static/images/" + imagefile.filename
        title, ingredients, recipe = output(image_path, current_app.root_path)
        print("Output received:", title, ingredients, recipe)
        # Pass the img variable to the predict.html template
        return render_template('predict.html', title=title, ingredients=ingredients, recipe=recipe, img=img)
    except Exception as e:
        print(f"Error processing image: {e}")
        return render_template('predict.html', title="Error", ingredients=[], recipe=[], img=None)

@food_blueprint.route('/<samplefoodname>')
@login_required
def predictsample(samplefoodname):
 try:
    # Processing the image and generating the recipe
    imagefile = request.files['imagefile']
    image_path = os.path.join(current_app.root_path, 'static', 'images', imagefile.filename)
    imagefile.save(image_path)
    img = "/static/images/" + imagefile.filename
    title, ingredients, recipe = output(image_path, current_app.root_path)
    return render_template('predict.html', title=title, ingredients=ingredients, recipe=recipe, img=img)
 except Exception as e:
    print(f"Error processing image: {e}")
    # Handling the exception and rendering the template without the img variable
    return render_template('predict.html', title="Error", ingredients=[], recipe=[], img=None)

    