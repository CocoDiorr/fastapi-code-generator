import argparse
from .codegen import generate_code  # adjust if needed

def main():
    parser = argparse.ArgumentParser(description='Generate FastAPI code from OpenAPI spec.')
    parser.add_argument('--input', '-i', required=True, help='Path to OpenAPI spec file (YAML/JSON)')
    parser.add_argument('--output', '-o', required=True, help='Output directory for generated code')
    args = parser.parse_args()
    generate_code(args.input, args.output)

if __name__ == '__main__':
    main() 
