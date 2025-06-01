import unittest
import os
from ..codegen import render_template

class TestTemplateRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Test models fixture
        cls.test_models = {
            "User": {
                "table_name": "users",
                "fields": [
                    {
                        "name": "id",
                        "type": "Integer",
                        "primary_key": True,
                        "nullable": False
                    },
                    {
                        "name": "username",
                        "type": "String",
                        "length": 50,
                        "nullable": False
                    }
                ],
                "relationships": []
            },
            "Post": {
                "table_name": "posts",
                "fields": [
                    {
                        "name": "id",
                        "type": "Integer",
                        "primary_key": True,
                        "nullable": False
                    },
                    {
                        "name": "title",
                        "type": "String",
                        "length": 200,
                        "nullable": False
                    },
                    {
                        "name": "user_id",
                        "type": "Integer",
                        "foreign_key": {"target": "users.id"},
                        "nullable": False
                    }
                ],
                "relationships": [
                    {
                        "name": "user",
                        "kind": "many_to_one",
                        "target": "User",
                        "back_populates": "posts"
                    }
                ]
            }
        }
        
        # Create test output directory
        cls.test_output_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        os.makedirs(cls.test_output_dir, exist_ok=True)
        
        # Context for templates
        cls.context = {
            'models': cls.test_models,
            'is_test': True
        }

    def setUp(self):
        # Clean test output directory before each test
        for file in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, file))

    def test_models_template(self):
        """Test that models.py.jinja2 generates valid SQLAlchemy models"""
        output_file = os.path.join(self.test_output_dir, 'models.py')
        render_template('models.py.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('from sqlalchemy import Column, Integer, String', content)
        self.assertIn('class User(Base):', content)
        self.assertIn('class Post(Base):', content)
        self.assertIn('__tablename__ = "users"', content)
        self.assertIn('__tablename__ = "posts"', content)
        self.assertIn('primary_key=True', content)
        self.assertIn('ForeignKey("users.id")', content)
        
    def test_handlers_template(self):
        """Test that handlers.py.jinja2 generates valid FastAPI handlers"""
        output_file = os.path.join(self.test_output_dir, 'handlers.py')
        render_template('handlers.py.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('from fastapi import APIRouter', content)
        self.assertIn('router = APIRouter()', content)
        self.assertIn('"/user/query"', content)
        self.assertIn('"/post/query"', content)
        self.assertIn('async def query_user(', content)
        self.assertIn('async def query_post(', content)
        self.assertIn('-> List[UserSchema]:', content)
        self.assertIn('-> List[PostSchema]:', content)
        self.assertIn('response_model=List[UserSchema]', content)
        self.assertIn('response_model=List[PostSchema]', content)
        
    def test_schemas_template(self):
        """Test that schemas.py.jinja2 generates valid Pydantic models"""
        output_file = os.path.join(self.test_output_dir, 'schemas.py')
        render_template('schemas.py.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('from pydantic import BaseModel, ConfigDict', content)
        self.assertIn('from typing import Optional, List, Any, ForwardRef', content)
        self.assertIn('class UserSchema(BaseModel):', content)
        self.assertIn('class PostSchema(BaseModel):', content)
        self.assertIn('model_config = ConfigDict(from_attributes=True, exclude_defaults=True)', content)
        self.assertIn('username: str', content)  # Field definition
        self.assertIn('title: str', content)     # Field definition
        self.assertIn('UserSchema.model_rebuild()', content)  # Forward ref handling
        self.assertIn('PostSchema.model_rebuild()', content)  # Forward ref handling
        
    def test_query_processor_template(self):
        """Test that query_processor.py.jinja2 generates valid query processor"""
        output_file = os.path.join(self.test_output_dir, 'query_processor.py')
        render_template('query_processor.py.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('from typing import List, Type, Any, Dict', content)
        self.assertIn('def query_with_include(', content)
        self.assertIn('MODEL_REGISTRY: Dict[str, Type[Any]]', content)
        self.assertIn('"User": User', content)
        self.assertIn('"Post": Post', content)
        self.assertIn('def flatten_includes(', content)
        self.assertIn('def make_selectin_loaders(', content)

    def test_openapi_template(self):
        """Test that openapi.yaml.jinja2 generates valid OpenAPI spec"""
        output_file = os.path.join(self.test_output_dir, 'openapi.yaml')
        render_template('openapi.yaml.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('openapi:', content)
        self.assertIn('paths:', content)
        self.assertIn('/user/query:', content)
        self.assertIn('/post/query:', content)
        self.assertIn('components:', content)
        self.assertIn('schemas:', content)

    def test_database_template(self):
        """Test that database.py.jinja2 generates valid database configuration"""
        output_file = os.path.join(self.test_output_dir, 'database.py')
        render_template('database.py.jinja2', self.context, output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check for essential components
        self.assertIn('from sqlalchemy.orm import sessionmaker', content)
        self.assertIn('def get_session()', content)

if __name__ == '__main__':
    unittest.main() 