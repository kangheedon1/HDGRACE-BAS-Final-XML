#!/usr/bin/env python3
"""
XML Generator Module
생성기 리팩토링 - Generator Refactoring

This module provides a flexible XML generator system with support for:
- Template-based XML generation
- Configuration-driven output
- Multiple generator types
- Error handling and validation
"""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class GeneratorConfig:
    """Configuration class for XML generators"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.root_element = config_data.get('root_element', 'root')
        self.namespace = config_data.get('namespace', None)
        self.encoding = config_data.get('encoding', 'UTF-8')
        self.pretty_print = config_data.get('pretty_print', True)
        self.custom_attributes = config_data.get('custom_attributes', {})
        self.metadata = config_data.get('metadata', {})
    
    @classmethod
    def from_file(cls, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return cls(config_data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    @classmethod
    def default(cls):
        """Create default configuration"""
        return cls({
            'root_element': 'document',
            'namespace': None,
            'encoding': 'UTF-8',
            'pretty_print': True,
            'custom_attributes': {},
            'metadata': {'generated_by': 'HDGRACE-BAS-XML-Generator'}
        })


class XMLGenerator(ABC):
    """Abstract base class for XML generators"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.root = None
        self._setup_root()
    
    def _setup_root(self):
        """Setup root element with namespace and attributes"""
        if self.config.namespace:
            self.root = ET.Element(self.config.root_element, 
                                 attrib={'xmlns': self.config.namespace})
        else:
            self.root = ET.Element(self.config.root_element)
        
        # Add custom attributes
        for key, value in self.config.custom_attributes.items():
            self.root.set(key, str(value))
        
        # Add metadata
        if self.config.metadata:
            meta_elem = ET.SubElement(self.root, 'metadata')
            for key, value in self.config.metadata.items():
                meta_child = ET.SubElement(meta_elem, key)
                meta_child.text = str(value)
            
            # Add generation timestamp
            timestamp_elem = ET.SubElement(meta_elem, 'generated_at')
            timestamp_elem.text = datetime.now().isoformat()
    
    @abstractmethod
    def generate_content(self, data: Any) -> None:
        """Generate XML content based on input data"""
        pass
    
    def to_string(self) -> str:
        """Convert XML tree to string"""
        if self.config.pretty_print:
            self._indent(self.root)
        
        return ET.tostring(self.root, 
                          encoding=self.config.encoding, 
                          method='xml').decode(self.config.encoding)
    
    def save_to_file(self, filepath: str) -> None:
        """Save XML to file"""
        xml_string = self.to_string()
        with open(filepath, 'w', encoding=self.config.encoding) as f:
            f.write('<?xml version="1.0" encoding="{}"?>\n'.format(self.config.encoding))
            f.write(xml_string)
    
    def _indent(self, elem, level=0):
        """Add pretty printing indentation"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class DataGenerator(XMLGenerator):
    """Generator for structured data XML"""
    
    def generate_content(self, data: Dict[str, Any]) -> None:
        """Generate XML from dictionary data"""
        data_elem = ET.SubElement(self.root, 'data')
        self._dict_to_xml(data, data_elem)
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element) -> None:
        """Convert dictionary to XML elements"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)


class TableGenerator(XMLGenerator):
    """Generator for table-like XML structures"""
    
    def generate_content(self, data: List[Dict[str, Any]]) -> None:
        """Generate XML table from list of dictionaries"""
        table_elem = ET.SubElement(self.root, 'table')
        
        # Add header if data exists
        if data:
            header_elem = ET.SubElement(table_elem, 'header')
            for column in data[0].keys():
                col_elem = ET.SubElement(header_elem, 'column')
                col_elem.text = str(column)
        
        # Add rows
        for row_data in data:
            row_elem = ET.SubElement(table_elem, 'row')
            for key, value in row_data.items():
                cell_elem = ET.SubElement(row_elem, 'cell')
                cell_elem.set('column', key)
                cell_elem.text = str(value)


class ReportGenerator(XMLGenerator):
    """Generator for report-style XML documents"""
    
    def generate_content(self, data: Dict[str, Any]) -> None:
        """Generate report XML with sections and content"""
        report_elem = ET.SubElement(self.root, 'report')
        
        # Add title
        if 'title' in data:
            title_elem = ET.SubElement(report_elem, 'title')
            title_elem.text = str(data['title'])
        
        # Add sections
        sections = data.get('sections', [])
        for section_data in sections:
            section_elem = ET.SubElement(report_elem, 'section')
            
            if 'name' in section_data:
                section_elem.set('name', str(section_data['name']))
            
            if 'title' in section_data:
                section_title = ET.SubElement(section_elem, 'title')
                section_title.text = str(section_data['title'])
            
            if 'content' in section_data:
                content_elem = ET.SubElement(section_elem, 'content')
                content_elem.text = str(section_data['content'])
            
            # Add subsections if any
            if 'subsections' in section_data:
                for subsection in section_data['subsections']:
                    sub_elem = ET.SubElement(section_elem, 'subsection')
                    sub_elem.set('name', str(subsection.get('name', '')))
                    sub_elem.text = str(subsection.get('content', ''))


class GeneratorFactory:
    """Factory class for creating appropriate generators"""
    
    _generators = {
        'data': DataGenerator,
        'table': TableGenerator,
        'report': ReportGenerator
    }
    
    @classmethod
    def create_generator(cls, generator_type: str, config: GeneratorConfig) -> XMLGenerator:
        """Create generator instance based on type"""
        if generator_type not in cls._generators:
            raise ValueError(f"Unknown generator type: {generator_type}. "
                           f"Available types: {list(cls._generators.keys())}")
        
        generator_class = cls._generators[generator_type]
        return generator_class(config)
    
    @classmethod
    def register_generator(cls, name: str, generator_class: type):
        """Register a new generator type"""
        if not issubclass(generator_class, XMLGenerator):
            raise ValueError("Generator class must inherit from XMLGenerator")
        cls._generators[name] = generator_class
    
    @classmethod
    def available_types(cls) -> List[str]:
        """Get list of available generator types"""
        return list(cls._generators.keys())


def generate_xml(generator_type: str, data: Any, config: Optional[GeneratorConfig] = None, include_declaration: bool = True) -> str:
    """Convenience function to generate XML"""
    if config is None:
        config = GeneratorConfig.default()
    
    generator = GeneratorFactory.create_generator(generator_type, config)
    generator.generate_content(data)
    
    xml_content = generator.to_string()
    
    if include_declaration:
        return '<?xml version="1.0" encoding="{}"?>\n{}'.format(config.encoding, xml_content)
    else:
        return xml_content


if __name__ == "__main__":
    # Example usage
    sample_data = {
        "name": "HDGRACE-BAS System",
        "version": "1.0",
        "components": {
            "database": "PostgreSQL",
            "framework": "Django",
            "language": "Python"
        },
        "features": ["XML Generation", "Data Processing", "Report Creation"]
    }
    
    # Generate with default configuration
    xml_output = generate_xml('data', sample_data)
    print("Generated XML:")
    print(xml_output)