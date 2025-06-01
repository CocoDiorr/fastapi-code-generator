from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi_codegen",
    version="0.1.0",
    author="Kolesnikov Aleksandr",
    description="A code generator for FastAPI applications with SQLAlchemy and Pydantic",
    url="https://github.com/CocoDiorr/fastapi_codegen",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "fastapi_code_generator": ["templates/*.jinja2"],
    },
    install_requires=[
        "fastapi>=0.104.0",  # Latest stable FastAPI
        "uvicorn>=0.24.0",   # ASGI server
        "sqlalchemy>=2.0.23", # Latest SQLAlchemy with improved typing
        "pydantic>=2.5.1",   # Latest Pydantic v2
        "python-multipart>=0.0.6",  # For form data handling
        "aiosqlite>=0.19.0",  # Async SQLite support
        "jinja2>=3.1.2",      # Template engine
        "pyyaml>=6.0.1",      # YAML support for config
        "typer>=0.9.0",       # CLI interface
        "rich>=13.7.0"        # Rich text and formatting
    ],
    extras_require={
        'test': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'pytest-asyncio>=0.21.1',
            'httpx>=0.25.1',  # For async HTTP testing
            'black>=23.11.0',  # Code formatting
            'isort>=5.12.0',  # Import sorting
            'mypy>=1.7.0',    # Type checking
            'ruff>=0.1.5',    # Fast Python linter
        ],
        'dev': [
            'pre-commit>=3.5.0',
            'tox>=4.11.3',
            'bump2version>=1.0.1',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.9",
    entry_points={
        'console_scripts': [
            'fastapi-codegen=fastapi_code_generator.cli:main',
        ],
    },
)
