import json
from dataclasses import dataclass, asdict
from typing import List
import os

@dataclass
class Recipe:
    """
    A class to represent a recipe.

    Attributes:
    ----------
    url : str
        The URL of the recipe.
    title : str
        The title of the recipe.
    """
    url: str
    title: str

class CookbookApp:
    """
    A class to represent the Cookbook application.

    Attributes:
    ----------
    recipes : List[Recipe]
        A list to store the recipes.
    filename : str
        The name of the file where recipes are saved.

    Methods:
    -------
    load_recipes():
        Loads recipes from a file.
    save_recipes():
        Saves recipes to a file.
    add_recipe(url: str, title: str):
        Adds a new recipe to the list and saves it.
    list_recipes():
        Lists all the recipes.
    run():
        Runs the main loop of the application.
    """
    def __init__(self):
        """
        Initializes the CookbookApp with an empty recipe list and loads recipes from a file.
        """
        self.recipes: List[Recipe] = []
        self.filename = "recipes.json"
        self.load_recipes()

    def load_recipes(self):
        """
        Loads recipes from a JSON file if it exists.
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.recipes = [Recipe(**r) for r in data]

    def save_recipes(self):
        """
        Saves the current list of recipes to a JSON file.
        """
        with open(self.filename, 'w') as f:
            json.dump([asdict(r) for r in self.recipes], f, indent=2)

    def add_recipe(self, url: str, title: str):
        """
        Adds a new recipe to the list and saves it to the file.

        Parameters:
        ----------
        url : str
            The URL of the recipe.
        title : str
            The title of the recipe.
        """
        recipe = Recipe(url=url, title=title)
        self.recipes.append(recipe)
        self.save_recipes()
        print(f"Added recipe: {title}")

    def list_recipes(self):
        """
        Lists all the recipes in the cookbook.
        """
        if not self.recipes:
            print("No recipes found.")
            return
        
        print("\nCurrent Recipes:")
        print("-" * 40)
        for i, recipe in enumerate(self.recipes, 1):
            print(f"{i}. {recipe.title}")
            print(f"   URL: {recipe.url}")
            print()

    def remove_recipe(self, number: int):
        """
        Removes a recipe from the list by its number.

        Parameters:
        ----------
        number : int
            The number of the recipe to remove.
        """
        if number < 1 or number > len(self.recipes):
            print("Invalid recipe number.")
            return
        
        recipe = self.recipes.pop(number - 1)
        self.save_recipes()
        print(f"Removed recipe: {recipe.title}")

    def run(self):
        """
        Runs the main loop of the application, displaying the menu and handling user input.
        """
        while True:
            print("\nCookbook Menu:")
            print("1. Add Recipe")
            print("2. List Recipes")
            print("3. Remove Recipe")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                url = input("Enter recipe URL: ")
                if not url.strip():
                    continue
                title = input("Enter recipe title: ")
                if not title.strip():
                    continue
                self.add_recipe(url, title)
            
            elif choice == "2":
                self.list_recipes()

            elif choice == "3":
                number = int(input("Enter the recipe number to remove: "))
                self.remove_recipe(number)

            elif choice == "4":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = CookbookApp()
    app.run()