#!/usr/bin/env python3
"""
Unit tests for XML Generator System
생성기 리팩토링 - Generator Refactoring Tests

This module contains tests to validate the XML generator functionality.
"""

import unittest
import tempfile
import os
import xml.etree.ElementTree as ET
from generator import (
    GeneratorConfig, XMLGenerator, DataGenerator, TableGenerator, 
    ReportGenerator, GeneratorFactory, generate_xml
)


class TestGeneratorConfig(unittest.TestCase):
    """Test GeneratorConfig class"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = GeneratorConfig.default()
        self.assertEqual(config.root_element, 'document')
        self.assertEqual(config.encoding, 'UTF-8')
        self.assertTrue(config.pretty_print)
        self.assertIn('generated_by', config.metadata)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config_data = {
            'root_element': 'test_root',
            'namespace': 'http://test.com',
            'encoding': 'UTF-16',
            'pretty_print': False
        }
        config = GeneratorConfig(config_data)
        self.assertEqual(config.root_element, 'test_root')
        self.assertEqual(config.namespace, 'http://test.com')
        self.assertEqual(config.encoding, 'UTF-16')
        self.assertFalse(config.pretty_print)
    
    def test_config_from_file(self):
        """Test loading configuration from file"""
        config_data = {'root_element': 'file_test', 'encoding': 'UTF-8'}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            config = GeneratorConfig.from_file(config_file)
            self.assertEqual(config.root_element, 'file_test')
        finally:
            os.unlink(config_file)


class TestDataGenerator(unittest.TestCase):
    """Test DataGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GeneratorConfig.default()
        self.generator = DataGenerator(self.config)
    
    def test_simple_data_generation(self):
        """Test generating XML from simple data"""
        data = {"name": "test", "value": 123}
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('name', xml_string)
        self.assertIn('test', xml_string)
        self.assertIn('value', xml_string)
        self.assertIn('123', xml_string)
    
    def test_nested_data_generation(self):
        """Test generating XML from nested data"""
        data = {
            "user": {
                "name": "홍길동",
                "age": 30,
                "address": {
                    "city": "서울",
                    "district": "강남"
                }
            }
        }
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('user', xml_string)
        self.assertIn('홍길동', xml_string)
        self.assertIn('address', xml_string)
        self.assertIn('강남', xml_string)
    
    def test_list_data_generation(self):
        """Test generating XML from list data"""
        data = {
            "items": ["apple", "banana", "cherry"],
            "numbers": [1, 2, 3]
        }
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('apple', xml_string)
        self.assertIn('banana', xml_string)
        self.assertIn('cherry', xml_string)


class TestTableGenerator(unittest.TestCase):
    """Test TableGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GeneratorConfig.default()
        self.generator = TableGenerator(self.config)
    
    def test_table_generation(self):
        """Test generating XML table"""
        data = [
            {"id": 1, "name": "Alice", "score": 95},
            {"id": 2, "name": "Bob", "score": 87}
        ]
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('table', xml_string)
        self.assertIn('header', xml_string)
        self.assertIn('row', xml_string)
        self.assertIn('Alice', xml_string)
        self.assertIn('87', xml_string)
    
    def test_empty_table_generation(self):
        """Test generating XML from empty table"""
        data = []
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('table', xml_string)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GeneratorConfig.default()
        self.generator = ReportGenerator(self.config)
    
    def test_report_generation(self):
        """Test generating XML report"""
        data = {
            "title": "테스트 보고서",
            "sections": [
                {
                    "name": "intro",
                    "title": "소개",
                    "content": "이것은 테스트 보고서입니다."
                }
            ]
        }
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('report', xml_string)
        self.assertIn('테스트 보고서', xml_string)
        self.assertIn('section', xml_string)
        self.assertIn('소개', xml_string)
    
    def test_report_with_subsections(self):
        """Test generating report with subsections"""
        data = {
            "title": "상세 보고서",
            "sections": [
                {
                    "name": "main",
                    "title": "주요 내용",
                    "content": "메인 섹션",
                    "subsections": [
                        {
                            "name": "sub1",
                            "content": "서브섹션 1"
                        }
                    ]
                }
            ]
        }
        self.generator.generate_content(data)
        
        xml_string = self.generator.to_string()
        self.assertIn('subsection', xml_string)
        self.assertIn('서브섹션 1', xml_string)


class TestGeneratorFactory(unittest.TestCase):
    """Test GeneratorFactory class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = GeneratorConfig.default()
    
    def test_create_data_generator(self):
        """Test creating data generator"""
        generator = GeneratorFactory.create_generator('data', self.config)
        self.assertIsInstance(generator, DataGenerator)
    
    def test_create_table_generator(self):
        """Test creating table generator"""
        generator = GeneratorFactory.create_generator('table', self.config)
        self.assertIsInstance(generator, TableGenerator)
    
    def test_create_report_generator(self):
        """Test creating report generator"""
        generator = GeneratorFactory.create_generator('report', self.config)
        self.assertIsInstance(generator, ReportGenerator)
    
    def test_invalid_generator_type(self):
        """Test error handling for invalid generator type"""
        with self.assertRaises(ValueError):
            GeneratorFactory.create_generator('invalid', self.config)
    
    def test_available_types(self):
        """Test getting available generator types"""
        types = GeneratorFactory.available_types()
        self.assertIn('data', types)
        self.assertIn('table', types)
        self.assertIn('report', types)


class TestConvenienceFunction(unittest.TestCase):
    """Test convenience function"""
    
    def test_generate_xml_function(self):
        """Test convenience function for XML generation"""
        data = {"test": "value"}
        xml_output = generate_xml('data', data)
        
        self.assertIn('<?xml', xml_output)
        self.assertIn('test', xml_output)
        self.assertIn('value', xml_output)
    
    def test_generate_xml_with_custom_config(self):
        """Test convenience function with custom config"""
        config = GeneratorConfig({'root_element': 'custom_root'})
        data = {"test": "value"}
        xml_output = generate_xml('data', data, config)
        
        self.assertIn('custom_root', xml_output)


class TestXMLValidation(unittest.TestCase):
    """Test XML output validation"""
    
    def test_generated_xml_is_valid(self):
        """Test that generated XML is well-formed"""
        config = GeneratorConfig.default()
        generator = DataGenerator(config)
        
        data = {"test": "value", "nested": {"key": "data"}}
        generator.generate_content(data)
        
        xml_string = generator.to_string()
        
        # Try to parse the generated XML
        try:
            ET.fromstring(xml_string)
        except ET.ParseError as e:
            self.fail(f"Generated XML is not well-formed: {e}")
    
    def test_namespace_handling(self):
        """Test XML namespace handling"""
        config = GeneratorConfig({
            'namespace': 'http://test.example.com',
            'root_element': 'test_root'
        })
        generator = DataGenerator(config)
        
        data = {"test": "value"}
        generator.generate_content(data)
        
        xml_string = generator.to_string()
        self.assertIn('xmlns', xml_string)
        self.assertIn('http://test.example.com', xml_string)


def run_tests():
    """Run all tests"""
    print("Running XML Generator Tests...")
    print("=" * 40)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestGeneratorConfig,
        TestDataGenerator,
        TestTableGenerator,
        TestReportGenerator,
        TestGeneratorFactory,
        TestConvenienceFunction,
        TestXMLValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)