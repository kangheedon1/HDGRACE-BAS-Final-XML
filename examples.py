#!/usr/bin/env python3
"""
Example usage of the XML Generator System
생성기 리팩토링 - Generator Refactoring Examples

This script demonstrates various use cases of the XML generator.
"""

from generator import GeneratorFactory, GeneratorConfig, generate_xml


def example_data_generation():
    """Example: Generate XML from structured data"""
    print("=== Data Generation Example ===")
    
    config = GeneratorConfig.from_file('config.json')
    
    sample_data = {
        "system_info": {
            "name": "HDGRACE-BAS",
            "version": "1.0.0",
            "environment": "production"
        },
        "modules": {
            "xml_generator": {
                "status": "active",
                "version": "1.0"
            },
            "data_processor": {
                "status": "active", 
                "version": "1.2"
            }
        },
        "settings": {
            "debug": False,
            "logging_level": "INFO",
            "max_connections": 100
        }
    }
    
    generator = GeneratorFactory.create_generator('data', config)
    generator.generate_content(sample_data)
    
    output_file = 'output_data.xml'
    generator.save_to_file(output_file)
    print(f"Data XML saved to: {output_file}")
    print(generator.to_string()[:500] + "...\n")


def example_table_generation():
    """Example: Generate XML table from tabular data"""
    print("=== Table Generation Example ===")
    
    config = GeneratorConfig.default()
    config.root_element = 'employee_data'
    
    table_data = [
        {"id": 1, "name": "김철수", "department": "개발팀", "salary": 5000},
        {"id": 2, "name": "이영희", "department": "디자인팀", "salary": 4500},
        {"id": 3, "name": "박민수", "department": "개발팀", "salary": 5200},
        {"id": 4, "name": "정수연", "department": "마케팅팀", "salary": 4800}
    ]
    
    generator = GeneratorFactory.create_generator('table', config)
    generator.generate_content(table_data)
    
    output_file = 'output_table.xml'
    generator.save_to_file(output_file)
    print(f"Table XML saved to: {output_file}")
    print(generator.to_string()[:500] + "...\n")


def example_report_generation():
    """Example: Generate XML report"""
    print("=== Report Generation Example ===")
    
    config = GeneratorConfig.default()
    config.root_element = 'system_report'
    
    report_data = {
        "title": "HDGRACE-BAS 시스템 월간 보고서",
        "sections": [
            {
                "name": "summary",
                "title": "요약",
                "content": "시스템이 안정적으로 운영되고 있으며, 성능 지표가 목표치를 달성했습니다."
            },
            {
                "name": "performance",
                "title": "성능 분석",
                "content": "평균 응답시간: 200ms, 처리량: 1000 req/sec",
                "subsections": [
                    {
                        "name": "cpu_usage",
                        "content": "CPU 사용률: 평균 65%"
                    },
                    {
                        "name": "memory_usage", 
                        "content": "메모리 사용률: 평균 70%"
                    }
                ]
            },
            {
                "name": "issues",
                "title": "이슈 및 개선사항",
                "content": "총 3건의 마이너 이슈가 발견되었으며, 모두 해결되었습니다."
            }
        ]
    }
    
    generator = GeneratorFactory.create_generator('report', config)
    generator.generate_content(report_data)
    
    output_file = 'output_report.xml'
    generator.save_to_file(output_file)
    print(f"Report XML saved to: {output_file}")
    print(generator.to_string()[:500] + "...\n")


def example_convenience_function():
    """Example: Using convenience function"""
    print("=== Convenience Function Example ===")
    
    simple_data = {
        "message": "안녕하세요 HDGRACE-BAS!",
        "timestamp": "2024-01-15T10:30:00",
        "status": "success"
    }
    
    xml_output = generate_xml('data', simple_data)
    print("Generated XML using convenience function:")
    print(xml_output + "\n")


def main():
    """Run all examples"""
    print("HDGRACE-BAS XML Generator Examples")
    print("===================================\n")
    
    try:
        example_data_generation()
        example_table_generation()  
        example_report_generation()
        example_convenience_function()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()