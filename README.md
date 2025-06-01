# FastAPI Code Generator

A code generation tool that creates FastAPI applications from OpenAPI/Swagger specifications. This tool automatically generates SQLAlchemy models, Pydantic schemas, and FastAPI route handlers based on your API specification.

## Features

- Generate complete FastAPI applications from OpenAPI/Swagger specifications
- Automatic generation of:
  - SQLAlchemy models with relationships
  - Pydantic schemas for request/response validation
  - FastAPI route handlers with proper typing
- Support for complex data relationships (one-to-many, many-to-many)
- Customizable templates for code generation
- Built-in support for common API patterns

## Installation

```bash
pip install fastapi-code-generator
```

## Quick Start

1. Create an OpenAPI/Swagger specification file (YAML or JSON)
2. Run the code generator:

```bash
fastapi-codegen generate --input your_spec.yaml --output ./generated_app
```

## Example

Check out the `examples/blog_app` directory for a complete example of a generated blog application with:
- User management
- Blog posts
- Comments
- Authentication
- Database relationships

## Project Structure

```
fastapi_code_generator/
├── templates/           # Jinja2 templates for code generation
│   ├── models.py.jinja2
│   ├── database.py.jinja2
│   ├── openapi.py.jinja2
│   ├── query_processor.py.jinja2
│   ├── schemas.py.jinja2
│   └── handlers.py.jinja2
└── tests/             # Test suite
```

## Template Customization

The generator uses Jinja2 templates that can be customized to match your project's needs. Templates are located in the `templates` directory

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
