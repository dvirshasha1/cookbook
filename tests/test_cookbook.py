import pytest
from datetime import datetime
import json
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_path))

from cookbook import Recipe, Cookbook, CookbookManager

@pytest.fixture
def sample_recipe():
    return Recipe(
        url="https://example.com/recipe1",
        title="Test Recipe",
        categories=["Italian", "Pasta"]
    )

@pytest.fixture
def sample_cookbook(sample_recipe):
    return Cookbook(
        name="Test Cookbook",
        description="Test Description",
        recipes=[sample_recipe]
    )

@pytest.fixture
def cookbook_manager(tmp_path):
    # Create manager with temporary file path
    manager = CookbookManager()
    manager.filename = str(tmp_path / "test_cookbooks.json")
    return manager

class TestRecipe:
    def test_recipe_creation(self):
        recipe = Recipe(
            url="https://example.com/recipe1",
            title="Spaghetti",
            categories=["Italian", "Pasta"]
        )
        assert recipe.url == "https://example.com/recipe1"
        assert recipe.title == "Spaghetti"
        assert "Italian" in recipe.categories
        assert recipe.date_added is not None

    def test_recipe_post_init(self):
        recipe = Recipe(
            url="https://example.com/recipe1",
            title="Spaghetti",
            categories=["Italian"]
        )
        # Verify date_added is in ISO format
        datetime.fromisoformat(recipe.date_added)

class TestCookbook:
    def test_cookbook_creation(self, sample_recipe):
        cookbook = Cookbook(
            name="Italian Dishes",
            description="Collection of Italian recipes",
            recipes=[sample_recipe]
        )
        assert cookbook.name == "Italian Dishes"
        assert cookbook.description == "Collection of Italian recipes"
        assert len(cookbook.recipes) == 1
        assert cookbook.recipes[0].title == "Test Recipe"

class TestCookbookManager:

    def test_create_cookbook(self, cookbook_manager):
        # Test creating a new cookbook
        assert cookbook_manager.create_cookbook("Italian", "Italian recipes")
        assert "Italian" in cookbook_manager.cookbooks
        
        # Test creating duplicate cookbook
        assert not cookbook_manager.create_cookbook("Italian", "Another description")

    def test_add_recipe(self, cookbook_manager):
        # Create cookbook first
        cookbook_manager.create_cookbook("Italian", "Italian recipes")
        
        # Test adding recipe
        assert cookbook_manager.add_recipe(
            "Italian",
            "https://example.com/recipe1",
            "Spaghetti",
            ["Pasta"]
        )
        
        # Verify recipe was added
        assert len(cookbook_manager.cookbooks["Italian"].recipes) == 1
        recipe = cookbook_manager.cookbooks["Italian"].recipes[0]
        assert recipe.title == "Spaghetti"
        assert recipe.categories == ["Pasta"]

    def test_add_recipe_nonexistent_cookbook(self, cookbook_manager):
        # Test adding recipe to non-existent cookbook
        assert not cookbook_manager.add_recipe(
            "NonExistent",
            "https://example.com/recipe1",
            "Spaghetti",
            ["Pasta"]
        )

    def test_save_and_load(self, cookbook_manager, tmp_path):
        # Create and add data
        cookbook_manager.create_cookbook("Italian", "Italian recipes")
        cookbook_manager.add_recipe(
            "Italian",
            "https://example.com/recipe1",
            "Spaghetti",
            ["Pasta"]
        )
        
        # Save data
        cookbook_manager.save_data()
        
        # Create new manager instance
        new_manager = CookbookManager()
        new_manager.filename = cookbook_manager.filename
        new_manager.load_data()
        
        # Verify data was loaded correctly
        assert "Italian" in new_manager.cookbooks
        assert len(new_manager.cookbooks["Italian"].recipes) == 1
        recipe = new_manager.cookbooks["Italian"].recipes[0]
        assert recipe.title == "Spaghetti"

    def test_search_recipes(self, cookbook_manager):
        # Setup test data
        cookbook_manager.create_cookbook("Italian", "Italian recipes")
        cookbook_manager.add_recipe(
            "Italian",
            "https://example.com/recipe1",
            "Spaghetti Carbonara",
            ["Pasta"]
        )
        cookbook_manager.add_recipe(
            "Italian",
            "https://example.com/recipe2",
            "Pizza Margherita",
            ["Pizza"]
        )
        
        # Test search functionality
        cookbook_manager.search_recipes("spag")  # Should find Spaghetti
        cookbook_manager.search_recipes("pizza")  # Should find Pizza
        cookbook_manager.search_recipes("burger")  # Should find nothing

class TestRecipeEdgeCases:
    def test_empty_categories(self):
        recipe = Recipe(
            url="https://example.com/recipe1",
            title="Test Recipe",
            categories=[]
        )
        assert recipe.categories == []

    def test_special_characters_in_title(self):
        special_title = "Crème brûlée & other café treats!"
        recipe = Recipe(
            url="https://example.com/recipe1",
            title=special_title,
            categories=["Dessert"]
        )
        assert recipe.title == special_title

    def test_very_long_title(self):
        long_title = "A" * 1000  # Very long title
        recipe = Recipe(
            url="https://example.com/recipe1",
            title=long_title,
            categories=["Test"]
        )
        assert recipe.title == long_title

class TestCookbookManagerFiltering:
    def test_filter_by_category(self, cookbook_manager):
        # Setup
        cookbook_manager.create_cookbook("Mixed", "Mixed recipes")
        cookbook_manager.add_recipe(
            "Mixed",
            "https://example.com/recipe1",
            "Pasta Dish",
            ["Italian", "Pasta"]
        )
        cookbook_manager.add_recipe(
            "Mixed",
            "https://example.com/recipe2",
            "Rice Dish",
            ["Asian", "Rice"]
        )

        # Test filtering
        cookbook_manager.list_recipes("Mixed", category="Italian")
        cookbook_manager.list_recipes("Mixed", category="Asian")
        cookbook_manager.list_recipes("Mixed", category="NonExistent")

    def test_case_insensitive_search(self, cookbook_manager):
        # Setup
        cookbook_manager.create_cookbook("Test", "Test cookbook")
        cookbook_manager.add_recipe(
            "Test",
            "https://example.com/recipe1",
            "Spaghetti Carbonara",
            ["Italian"]
        )

        # Test searches
        cookbook_manager.search_recipes("SPAGHETTI")
        cookbook_manager.search_recipes("carbonara")
        cookbook_manager.search_recipes("SpAgHeTtI")

class TestDataValidation:
    def test_duplicate_cookbook_names(self, cookbook_manager):
        # First creation should succeed
        assert cookbook_manager.create_cookbook("Italian", "First Italian cookbook")
        # Second creation with same name should fail
        assert not cookbook_manager.create_cookbook("Italian", "Second Italian cookbook")

    def test_invalid_cookbook_name(self, cookbook_manager):
        # Test empty name
        assert not cookbook_manager.create_cookbook("", "Empty name cookbook")
        
        # Test whitespace name
        assert not cookbook_manager.create_cookbook("   ", "Whitespace name cookbook")

    def test_empty_recipe_fields(self, cookbook_manager):
        cookbook_manager.create_cookbook("Test", "Test cookbook")
        
        # Test empty URL
        assert not cookbook_manager.add_recipe(
            "Test",
            "",
            "Title",
            ["Category"]
        )
        
        # Test empty title
        assert not cookbook_manager.add_recipe(
            "Test",
            "https://example.com",
            "",
            ["Category"]
        )

class TestErrorHandling:
    def test_load_corrupted_file(self, tmp_path):
        # Create corrupted JSON file
        corrupted_file = tmp_path / "corrupted.json"
        corrupted_file.write_text("{Invalid JSON")
        
        manager = CookbookManager()
        manager.filename = str(corrupted_file)
        
        # Should handle corrupted file gracefully
        manager.load_data()
        assert len(manager.cookbooks) == 0

    def test_save_to_readonly_location(self, tmp_path):
        readonly_file = tmp_path / "readonly.json"
        readonly_file.touch()
        readonly_file.chmod(0o444)  # Make file readonly
        
        manager = CookbookManager()
        manager.filename = str(readonly_file)
        
        # Should handle permission error gracefully
        manager.create_cookbook("Test", "Test cookbook")