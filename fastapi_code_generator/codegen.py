import os
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_code(input_path: str, output_dir: str):
    """
    Generate FastAPI code from an OpenAPI/Swagger specification file.
    
    Args:
        input_path: Path to the input YAML/JSON specification file
        output_dir: Directory where generated code should be placed
    """
    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    # Load YAML model spec
    with open(input_path) as f:
        spec = yaml.safe_load(f)
        models = spec.get('models', {})

    # Initialize Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['py', 'yaml'])
    )

    def render_template(template_name: str, context: dict, output_name: str):
        """
        Render a Jinja2 template to a file in output_dir
        """
        template = env.get_template(template_name)
        content = template.render(context)
        out_path = os.path.join(output_dir, output_name)
        with open(out_path, 'w') as out:
            out.write(content)
        print(f"Generated {out_path}")

    # Context for templates
    context = {
        'models': models,
    }

    # Generate ORM models
    render_template('models.py.jinja2', context, 'models.py')
    # Generate Pydantic schemas
    render_template('schemas.py.jinja2', context, 'schemas.py')
    # Generate query processor
    render_template('query_processor.py.jinja2', context, 'query_processor.py')
    # Generate FastAPI handlers
    render_template('handlers.py.jinja2', context, 'handlers.py')
    # Generate OpenAPI overrides
    render_template('openapi.yaml.jinja2', context, 'openapi.yaml')
    # Generate database
    render_template('database.py.jinja2', context, 'database.py')

    print("Code generation complete.")
