import csv

with open("Rezept_SQL.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=";")
    for index, row in enumerate(csv_reader):
        if index == 0:
            pass
        if row[3] == "N/A":
            row[3] = ""

        recipe = Recipes(recipe_name=row[1], owner=1, form_of_diet=row[0],
                         source_of_recipe=row[2],
                         additional_information=row[3], duration=row[4],
                         balanced_nutrients=row[6],
                         kind_of_meal=row[7], season=row[8], cuisine=row[9])
        db.session.add(recipe)
        db.session.commit()
        list_of_ingredients = row[5].split(", ")
        for element in list_of_ingredients:
            ingredients = Ingredients(ingredient=element, amount=1, unit="Einheit", recipe_name=row[1],
                                      owner=1)
            db.session.add(ingredients)
            db.session.commit()