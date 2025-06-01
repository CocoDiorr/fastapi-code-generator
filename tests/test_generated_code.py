import unittest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

from ..codegen import render_template

class TestGeneratedCode(unittest.TestCase):
    query_with_include = None  # Will be set in setUpClass
    
    @classmethod
    def setUpClass(cls):
        """Generate code and set up database"""
        # Test models fixture - same as in test_templates.py
        cls.test_models = {
            "User": {
                "table_name": "users",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True, "nullable": False},
                    {"name": "username", "type": "String", "length": 50, "nullable": False},
                    {"name": "email", "type": "String", "length": 100, "nullable": False}
                ],
                "relationships": [
                    {
                        "name": "posts",
                        "kind": "one_to_many",
                        "target": "Post",
                        "back_populates": "user"
                    }
                ]
            },
            "Post": {
                "table_name": "posts",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True, "nullable": False},
                    {"name": "title", "type": "String", "length": 200, "nullable": False},
                    {"name": "content", "type": "String", "nullable": False},
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
        
        # Create test output directory and make it a package
        cls.test_output_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        os.makedirs(cls.test_output_dir, exist_ok=True)
        init_file = os.path.join(cls.test_output_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Generated code package"""')
        
        # Generate all necessary files
        context = {
            'models': cls.test_models,
            'is_test': True  # Flag to indicate test environment
        }
        cls.generate_code_files(context)
        
        # Add test_output to Python path
        if cls.test_output_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(cls.test_output_dir))
        
        # Import generated modules
        from test_output.models import Base, User, Post
        from test_output.query_processor import query_with_include, MODEL_REGISTRY
        from test_output.schemas import UserSchema, PostSchema
        
        # Store imports as class attributes
        cls.Base = Base
        cls.User = User
        cls.Post = Post
        cls.MODEL_REGISTRY = MODEL_REGISTRY
        cls.UserSchema = UserSchema
        cls.PostSchema = PostSchema
        cls.query_with_include = staticmethod(query_with_include)  # Make it a static method
        
        # Set up in-memory SQLite database
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def generate_code_files(cls, context: Dict[str, Any]) -> None:
        """Generate all necessary code files"""
        templates = [
            ('models.py.jinja2', 'models.py'),
            ('schemas.py.jinja2', 'schemas.py'),
            ('query_processor.py.jinja2', 'query_processor.py'),
            ('database.py.jinja2', 'database.py')
        ]
        
        for template, output in templates:
            output_path = os.path.join(cls.test_output_dir, output)
            render_template(template, context, output_path)

    def setUp(self):
        """Set up test database with sample data"""
        self.session = self.Session()
        
        # Create test users
        self.user1 = self.User(username="testuser1", email="test1@example.com")
        self.user2 = self.User(username="testuser2", email="test2@example.com")
        self.session.add_all([self.user1, self.user2])
        self.session.commit()
        
        # Create test posts
        self.post1 = self.Post(
            title="Test Post 1",
            content="Content 1",
            user_id=self.user1.id
        )
        self.post2 = self.Post(
            title="Test Post 2",
            content="Content 2",
            user_id=self.user1.id
        )
        self.post3 = self.Post(
            title="Test Post 3",
            content="Content 3",
            user_id=self.user2.id
        )
        self.session.add_all([self.post1, self.post2, self.post3])
        self.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        self.session.close()
        self.Base.metadata.drop_all(self.engine)
        self.Base.metadata.create_all(self.engine)

    def test_basic_query(self):
        """Test basic query without includes or filters"""
        results = self.query_with_include(
            self.session,
            self.User,
            filters={},
            fields=[],
            include_spec={}
        )
        self.assertEqual(len(results), 2)  # Should return both users
        self.assertIsInstance(results[0], self.User)

    def test_query_with_filter(self):
        """Test querying with filters"""
        results = self.query_with_include(
            self.session,
            self.User,
            filters={"username": "testuser1"},
            fields=[],
            include_spec={}
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, "testuser1")

    def test_query_with_include(self):
        """Test querying with relationship includes"""
        results = self.query_with_include(
            self.session,
            self.User,
            filters={"username": "testuser1"},
            fields=[],
            include_spec={"posts": {}}
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0].posts), 2)  # User1 has 2 posts
            

    def test_query_with_nested_filter(self):
        """Test querying with filters on related models"""
        results = self.query_with_include(
            self.session,
            self.Post,
            filters={},
            fields=[],
            include_spec={
                "user": {
                    "filters": {"username": "testuser1"}
                }
            }
        )
        self.assertEqual(len(results), 2)  # Should find 2 posts by testuser1
        self.assertEqual(results[0].user.username, "testuser1")

    def test_query_with_field_selection(self):
        """Test querying with specific field selection"""
        results = self.query_with_include(
            self.session,
            self.User,
            filters={},
            fields=["username"],
            include_spec={}
        )
        self.assertEqual(len(results), 2)

    def test_query_with_complex_include(self):
        """Test querying with nested includes and field selection"""
        results = self.query_with_include(
            self.session,
            self.Post,
            filters={},
            fields=["title"],
            include_spec={
                "user": {
                    "fields": ["username"],
                    "include": {}
                }
            }
        )
        self.assertEqual(len(results), 3)  # Should find all posts
        # Check nested data
        self.assertIsNotNone(results[0].user)
        self.assertIsNotNone(results[0].user.username)

    def test_schema_serialization(self):
        """Test that generated Pydantic schemas work correctly"""
        user = self.session.query(self.User).first()
        # Only validate the user without loading relationships
        user_schema = self.UserSchema.model_validate(user, from_attributes=True)
        self.assertEqual(user_schema.username, user.username)
        self.assertEqual(user_schema.email, user.email)
        
        # Test relationship serialization separately
        post = self.session.query(self.Post).first()
        post_schema = self.PostSchema.model_validate(post, from_attributes=True)
        self.assertEqual(post_schema.title, post.title)
        self.assertEqual(post_schema.content, post.content)
        
        # Test that relationships are properly typed
        self.assertIsInstance(user_schema.posts, list)

if __name__ == '__main__':
    unittest.main() 