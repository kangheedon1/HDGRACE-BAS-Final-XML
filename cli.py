#!/usr/bin/env python3
"""
HDGRACE-BAS XML Generator CLI
생성기 리팩토링 - Generator Refactoring Command Line Interface

Command line interface for the XML generator system.
"""

import argparse
import json
import sys
import os
from generator import GeneratorFactory, GeneratorConfig, generate_xml


def load_data_from_file(filepath):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in data file '{filepath}': {e}")
        sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="HDGRACE-BAS XML Generator CLI - 생성기 리팩토링",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate data XML with default config
  python cli.py data sample_data.json -o output.xml
  
  # Generate table XML with custom config
  python cli.py table table_data.json -c config.json -o table.xml
  
  # Generate report XML with pretty printing disabled
  python cli.py report report_data.json --no-pretty -o report.xml
  
  # List available generator types
  python cli.py --list-types
        """
    )
    
    parser.add_argument(
        'type',
        nargs='?',
        choices=['data', 'table', 'report'],
        help='Generator type to use'
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input JSON file containing data'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output.xml',
        help='Output XML file (default: output.xml)'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Configuration JSON file (optional)'
    )
    
    parser.add_argument(
        '--no-pretty',
        action='store_true',
        help='Disable pretty printing'
    )
    
    parser.add_argument(
        '--no-declaration',
        action='store_true',
        help='Exclude XML declaration'
    )
    
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List available generator types'
    )
    
    parser.add_argument(
        '--encoding',
        default='UTF-8',
        help='XML encoding (default: UTF-8)'
    )
    
    parser.add_argument(
        '--root-element',
        help='Custom root element name'
    )
    
    parser.add_argument(
        '--namespace',
        help='XML namespace URI'
    )
    
    args = parser.parse_args()
    
    # Handle list types command
    if args.list_types:
        print("Available generator types:")
        for gen_type in GeneratorFactory.available_types():
            print(f"  - {gen_type}")
        sys.exit(0)
    
    # Validate required arguments
    if not args.type or not args.input:
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    if args.config:
        try:
            config = GeneratorConfig.from_file(args.config)
        except ValueError as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    else:
        config = GeneratorConfig.default()
    
    # Override config with command line arguments
    if args.no_pretty:
        config.pretty_print = False
    
    if args.encoding:
        config.encoding = args.encoding
    
    if args.root_element:
        config.root_element = args.root_element
    
    if args.namespace:
        config.namespace = args.namespace
    
    # Load input data
    data = load_data_from_file(args.input)
    
    try:
        # Generate XML
        print(f"Generating {args.type} XML from {args.input}...")
        
        generator = GeneratorFactory.create_generator(args.type, config)
        generator.generate_content(data)
        
        # Save output
        generator.save_to_file(args.output)
        
        print(f"XML generated successfully: {args.output}")
        
        # Show file size
        file_size = os.path.getsize(args.output)
        print(f"Output file size: {file_size} bytes")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()