import json
import random
from flask import Flask, Response, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, UserMixin, LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:M43hdr3sch3r@localhost/cookers"
app.config["SECRET_KEY"] = "test1234"
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    recipes = db.relationship("Recipes", backref="owner", lazy=True)
    ingredients = db.relationship("Ingredients", backref="owner", lazy=True)

    #def __repr__(self):
     #   return f"{self.username}"


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(50), unique=False, nullable=False)
    form_of_diet = db.Column(db.String(50), unique=False, nullable=False)
    source_of_recipe = db.Column(db.String(50), unique=False, nullable=False)
    additional_information = db.Column(db.Text, unique=False, nullable=True)
    duration = db.Column(db.String(50), unique=False, nullable=True)
    balanced_nutrients = db.Column(db.String(50), unique=False, nullable=False)
    kind_of_meal = db.Column(db.String(50), unique=False, nullable=False)
    season = db.Column(db.String(50), unique=False, nullable=False)
    cuisine = db.Column(db.String(50), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ingredients = db.relationship("Ingredients", backref="recipe_name", lazy=True)

    #def __repr__(self):
    #    return f"{self.recipe_name}"


class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(30), unique=False, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    recipes_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    #def __repr__(self):
    #    return f"{self.ingredient}, {self.amount},{self.unit}"


class RecipeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Recipes


class IngredientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ingredients


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if request.form.get("register_user"):
            username = request.form.get("username").lower()
            email = request.form.get("email").lower()
            password = request.form.get("password")
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            if User.query.filter_by(username=username).first():
                flash("Benutzername ist schon vergeben, bitte gib einen anderen ein.")
                return redirect(url_for("register"))
            elif User.query.filter_by(email=email).first():
                flash("Email ist schon vergeben, bitte gib einen anderen ein.")
                return redirect(url_for("register"))
            else:
                user = User(username=username, password=hashed_password, email=email)
                db.session.add(user)
                db.session.commit()
                # flash message that account was created and you can log in.
                return redirect(url_for("login"))
        else:
            return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("register.html")


@app.route("/", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("redirect_users"):
            return redirect(url_for("login"))
        elif request.form.get("redirect_add_recipes"):
            return redirect(url_for("add_ingredient"))
        else:
            return redirect(url_for("random_recipes"))
    else:
        return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form.get("redirect_index"):
            return redirect(url_for("index"))
        elif request.form.get("random_meal_plan"):
            username = request.form.get("username").lower()
            email = request.form.get("email").lower()
            password = request.form.get("password")
            user = User.query.filter_by(username=username, email=email).first()     #TODO: maybe not working bc of email=email
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("index"))
            else:
                # flash Login unsuccessful. Please check entries or register
                return redirect(url_for("login"))
        else:
            pass
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        else:
            return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/add_ingredients", methods=["POST", "GET"])
@login_required
def add_ingredient():
    if request.method == "POST":
        if request.form.get("redirect_index"):
            return redirect(url_for("index"))
        else:
            recipe_name = request.form.get("recipe_name")
            form_of_diet = request.form.get("form_of_diet")
            source_of_recipe = request.form.get("source_of_recipe")
            additional_information = request.form.get("additional_information")
            duration = request.form.get("duration")
            balanced_nutrients = request.form.get("balanced_nutrients")
            kind_of_meal = request.form.get("kind_of_meal")
            season = request.form.get("season")
            cuisine = request.form.get("cuisine")
            ingredient = request.form.get("ingredient")
            amount = request.form.get("amount")
            unit = request.form.get("unit")
            recipe = Recipes(recipe_name=recipe_name, owner=current_user, form_of_diet=form_of_diet, source_of_recipe=source_of_recipe,
                             additional_information=additional_information, duration=duration, balanced_nutrients=balanced_nutrients,
                             kind_of_meal=kind_of_meal, season=season, cuisine=cuisine)
            db.session.add(recipe)
            db.session.commit()
            current_recipe = Recipes.query.filter_by(recipe_name=recipe_name).first()
            ingredients = Ingredients(ingredient=ingredient, amount=amount, unit=unit, recipe_name=current_recipe, owner=current_user)
            db.session.add(ingredients)
            db.session.commit()
            return render_template("add_ingredients.html")
    else:
        return render_template("add_ingredients.html")


@app.route("/generate_recipes", methods=["POST", "GET"])
@login_required
def random_recipes():
    recipe_list = []
    if request.method == "POST":
        if request.form.get("redirect_index"):
            return redirect(url_for("index"))
        else:
            recipe_list_db = Recipes.query.filter_by(user_id=current_user.id).all()
            recipe_schema = RecipeSchema(many=True)
            recipe_list_json = recipe_schema.dump(recipe_list_db)
            for recipe in recipe_list_json:
                recipe_list.append(recipe["recipe_name"])
            random_list = []
            response = []
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            while len(random_list) != 7:
                n = random.randint(0, len(recipe_list) - 1)
                if n in random_list:
                    pass
                else:
                    random_list.append(n)
            for i, weekday in enumerate(weekdays):
                response.append({"weekday": weekday, "recipe": recipe_list[random_list[i]]})
            return Response(json.dumps(response), mimetype="application/json")
    else:
        return render_template("generate_random_recipes.html")


@app.route("/show_ingredients", methods=["POST", "GET"])
@login_required
def show_ingredients():
    if request.method == "POST":
        if request.form.get("redirect_index"):
            return redirect(url_for("index"))
        else:
            recipe_name = request.form.get("recipe")
            recipe_name_id = Recipes.query.filter_by(recipe_name=recipe_name, user_id=current_user.id).first()
            ingredient_list_db = Ingredients.query.filter_by(recipes_id=recipe_name_id.id, user_id=current_user.id).all()
            ingredient_schema = IngredientSchema(many=True)
            ingredient_list_json = ingredient_schema.dump(ingredient_list_db)
            return Response(json.dumps(ingredient_list_json), mimetype="application/json")
    else:
        return render_template("show_ingredients.html")

@app.route("/import", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        if request.form.get("import_csv"):
            with open(r"Rezept_SQL.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                for index, row in enumerate(csv_reader):
                    if index == 0:
                        pass
                    else:
                        if row[3] == "N/A":
                            row[3] = ""

                        recipe = Recipes(recipe_name=row[1], owner=current_user, form_of_diet=row[0],
                                         source_of_recipe=row[2],
                                         additional_information=row[3], duration=row[4],
                                         balanced_nutrients=row[6],
                                         kind_of_meal=row[7], season=row[8], cuisine=row[9])
                        db.session.add(recipe)
                        db.session.commit()
                        current_recipe = Recipes.query.filter_by(recipe_name=row[1], user_id=current_user.get_id()).first()
                        list_of_ingredients = row[5].split(", ")
                        for element in list_of_ingredients:
                            ingredients = Ingredients(ingredient=element, amount=1, unit="Einheit", recipe_name=current_recipe,
                                                      owner=current_user)
                            db.session.add(ingredients)
                            db.session.commit()
            return redirect(url_for("index"))
    else:
        return render_template("import.html")

@app.route("/filter_recipes", methods=["GET", "POST"])
def filter_recipes():
    if request.method == "POST":
        possible_recipes = ["Linsensuppe"]
        return Response(json.dumps(possible_recipes), mimetype="application/json")
    else:
        unique_ingredients = []
        #render_template("filter_recipes.html")
        list_of_ingredients = Ingredients.query.filter_by(user_id=current_user.get_id()).all()
        ingredient_schema = IngredientSchema(many=True)
        ingredient_list_json = ingredient_schema.dump(list_of_ingredients)
        for ingredient in ingredient_list_json:
            if ingredient.get("ingredient") not in unique_ingredients:
                unique_ingredients.append(ingredient.get("ingredient"))
            else:
                pass
        return render_template("filter.html", unique_ingredients=unique_ingredients)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port="5000")

