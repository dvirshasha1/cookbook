import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from datetime import datetime
import os

@dataclass
class Recipe:
    url: str
    title: str
    categories: List[str]
    date_added: str = None

    def __post_init__(self):
        if self.date_added is None:
            self.date_added = datetime.now().isoformat()

@dataclass
class Cookbook:
    name: str
    description: str
    recipes: List[Recipe]

class CookbookManager:
    def __init__(self):
        self.cookbooks: Dict[str, Cookbook] = {}
        self.filename = "cookbooks.json"
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for cookbook_data in data:
                    recipes = [Recipe(**r) for r in cookbook_data['recipes']]
                    cookbook = Cookbook(
                        name=cookbook_data['name'],
                        description=cookbook_data['description'],
                        recipes=recipes
                    )
                    self.cookbooks[cookbook.name] = cookbook
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading data: {str(e)}")
            self.cookbooks = {}

    def save_data(self):
        data = []
        for cookbook in self.cookbooks.values():
            cookbook_dict = {
                'name': cookbook.name,
                'description': cookbook.description,
                'recipes': [asdict(r) for r in cookbook.recipes]
            }
            data.append(cookbook_dict)
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except (PermissionError, OSError) as e:
            print(f"Error saving data: {str(e)}")
            return False
        return True

    def validate_cookbook_name(self, name: str) -> bool:
        """Validate cookbook name"""
        if not name or not name.strip():
            print("Cookbook name cannot be empty or whitespace")
            return False
        return True

    def validate_recipe(self, url: str, title: str) -> bool:
        """Validate recipe data"""
        if not url or not url.strip():
            print("Recipe URL cannot be empty")
            return False
        if not title or not title.strip():
            print("Recipe title cannot be empty")
            return False
        return True

    def create_cookbook(self, name: str, description: str) -> bool:
        """Create a new cookbook with validation"""
        if not self.validate_cookbook_name(name):
            return False
            
        if name in self.cookbooks:
            print(f"Cookbook '{name}' already exists!")
            return False
        
        self.cookbooks[name] = Cookbook(name=name, description=description, recipes=[])
        return self.save_data()

    def add_recipe(self, cookbook_name: str, url: str, title: str, categories: List[str]) -> bool:
        """Add a recipe with validation"""
        if cookbook_name not in self.cookbooks:
            print(f"Cookbook '{cookbook_name}' not found!")
            return False

        if not self.validate_recipe(url, title):
            return False

        recipe = Recipe(url=url, title=title, categories=categories)
        self.cookbooks[cookbook_name].recipes.append(recipe)
        return self.save_data()

    def list_cookbooks(self):
        if not self.cookbooks:
            print("No cookbooks found.")
            return

        print("\nAvailable Cookbooks:")
        print("-" * 40)
        for name, cookbook in self.cookbooks.items():
            print(f"Name: {name}")
            print(f"Description: {cookbook.description}")
            print(f"Number of recipes: {len(cookbook.recipes)}")
            print("-" * 40)

    def list_recipes(self, cookbook_name: str, category: Optional[str] = None):
        if cookbook_name not in self.cookbooks:
            print(f"Cookbook '{cookbook_name}' not found!")
            return

        cookbook = self.cookbooks[cookbook_name]
        recipes = cookbook.recipes

        if category:
            recipes = [r for r in recipes if category in r.categories]

        if not recipes:
            print(f"No recipes found{' in category ' + category if category else ''}.")
            return

        print(f"\nRecipes in '{cookbook_name}'{' (Category: ' + category + ')' if category else ''}:")
        print("-" * 40)
        for i, recipe in enumerate(recipes, 1):
            print(f"{i}. {recipe.title}")
            print(f"   URL: {recipe.url}")
            print(f"   Categories: {', '.join(recipe.categories)}")
            print(f"   Added: {recipe.date_added}")
            print()

    def search_recipes(self, query: str):
        results = []
        for cookbook in self.cookbooks.values():
            for recipe in cookbook.recipes:
                if query.lower() in recipe.title.lower():
                    results.append((cookbook.name, recipe))
        
        if not results:
            print(f"No recipes found matching '{query}'")
            return

        print(f"\nSearch results for '{query}':")
        print("-" * 40)
        for cookbook_name, recipe in results:
            print(f"Cookbook: {cookbook_name}")
            print(f"Title: {recipe.title}")
            print(f"URL: {recipe.url}")
            print(f"Categories: {', '.join(recipe.categories)}")
            print()

    def run(self):
        while True:
            print("\nCookbook Manager Menu:")
            print("1. Create New Cookbook")
            print("2. Add Recipe to Cookbook")
            print("3. List Cookbooks")
            print("4. List Recipes in Cookbook")
            print("5. Search Recipes")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                name = input("Enter cookbook name: ")
                description = input("Enter cookbook description: ")
                self.create_cookbook(name, description)
            
            elif choice == "2":
                cookbook_name = input("Enter cookbook name: ")
                url = input("Enter recipe URL: ")
                title = input("Enter recipe title: ")
                categories = input("Enter categories (comma-separated): ").split(',')
                categories = [c.strip() for c in categories if c.strip()]
                self.add_recipe(cookbook_name, url, title, categories)
            
            elif choice == "3":
                self.list_cookbooks()
            
            elif choice == "4":
                cookbook_name = input("Enter cookbook name: ")
                category = input("Enter category to filter (or press Enter for all): ").strip()
                self.list_recipes(cookbook_name, category if category else None)
            
            elif choice == "5":
                query = input("Enter search term: ")
                self.search_recipes(query)
            
            elif choice == "6":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = CookbookManager()
    app.run()