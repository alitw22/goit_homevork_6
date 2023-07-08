def get_recipe(path, search_id):
    with open(path, 'r') as file:
        for line in file:
            recipe_data = line.strip().split(', ')
            if recipe_data[0] == search_id:
                recipe = {
                    "id": recipe_data[0],
                    "name": recipe_data[1],
                    "ingredients": recipe_data[2:],
                }
                return recipe
    return None


recipe = get_recipe("C:\\111\ingredients.csv", "60b90c1c13067a15887e1ae1")
print(recipe)