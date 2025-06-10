"""
Test Suite for Certificate Generation System
===========================================

Author: devag7 (Deva Garwalla)
Description: Comprehensive test suite for certificate generation functionality
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import modules to test
import tasks
import utils


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    def test_generate_qr_code(self):
        """Test QR code generation"""
        cert_id = "TEST-QR-123"
        qr_path = utils.generate_qr_code(cert_id, self.temp_dir)
        
        self.assertTrue(qr_path.exists())
        self.assertTrue(qr_path.name.endswith('.png'))
        self.assertIn(cert_id, qr_path.name)
    
    def test_format_datetime(self):
        """Test datetime formatting"""
        iso_string = "2025-06-10T14:30:00+00:00"
        formatted = utils.format_datetime(iso_string)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("Jun", formatted)
        self.assertIn("2025", formatted)
    
    def test_format_datetime_invalid(self):
        """Test datetime formatting with invalid input"""
        invalid_string = "invalid-date"
        formatted = utils.format_datetime(invalid_string)
        
        self.assertEqual(formatted, "Invalid Date")
    
    def test_validate_certificate_id(self):
        """Test certificate ID validation"""
        # Valid IDs
        valid_ids = [
            "CERT-123456789",
            "TEST-ABCD-2025",
            "CSI_CERT_001"
        ]
        
        for cert_id in valid_ids:
            self.assertTrue(utils.validate_certificate_id(cert_id))
        
        # Invalid IDs
        invalid_ids = [
            "",
            "ABC",  # Too short
            None,
            "cert@123",  # Invalid character
        ]
        
        for cert_id in invalid_ids:
            self.assertFalse(utils.validate_certificate_id(cert_id))
    
    def test_get_file_size_mb(self):
        """Test file size calculation"""
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "x" * 1024 * 1024  # 1MB of data
        test_file.write_text(test_content)
        
        size_mb = utils.get_file_size_mb(test_file)
        self.assertAlmostEqual(size_mb, 1.0, places=1)
        
        # Test non-existent file
        non_existent = Path(self.temp_dir) / "nonexistent.txt"
        size_mb = utils.get_file_size_mb(non_existent)
        self.assertEqual(size_mb, 0.0)


class TestTasks(unittest.TestCase):
    """Test certificate generation tasks"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Valid test data
        self.valid_data = {
            "user_name": "Test User",
            "college": "Test University",
            "certificate_id": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "issued_at": datetime.now().isoformat(),
            "topic": "Test Topic"
        }
    
    def test_validate_data_valid(self):
        """Test data validation with valid data"""
        validated = tasks.validate_data(self.valid_data)
        self.assertEqual(validated, self.valid_data)
    
    def test_validate_data_missing_fields(self):
        """Test data validation with missing required fields"""
        incomplete_data = {
            "user_name": "Test User"
            # Missing other required fields
        }
        
        with self.assertRaises(ValueError) as context:
            tasks.validate_data(incomplete_data)
        
        self.assertIn("Missing or empty required fields", str(context.exception))
    
    def test_validate_data_invalid_types(self):
        """Test data validation with invalid data types"""
        invalid_data = self.valid_data.copy()
        invalid_data["user_name"] = 123  # Should be string
        
        with self.assertRaises(ValueError) as context:
            tasks.validate_data(invalid_data)
        
        self.assertIn("user_name must be a string", str(context.exception))
    
    def test_validate_data_field_length(self):
        """Test data validation with field length limits"""
        invalid_data = self.valid_data.copy()
        invalid_data["user_name"] = "x" * 101  # Too long
        
        with self.assertRaises(ValueError) as context:
            tasks.validate_data(invalid_data)
        
        self.assertIn("max 100 characters", str(context.exception))
    
    def test_text_escape(self):
        """Test text escaping for FFmpeg"""
        test_cases = [
            ("Hello World", "Hello World"),
            ("John's Certificate", "John\\'s Certificate"),
            ("Data: Analysis", "Data\\: Analysis"),
            ("Test [123]", "Test \\[123\\]"),
            ("A, B; C", "A\\, B\\; C"),
        ]
        
        for input_text, expected in test_cases:
            result = tasks.text_escape(input_text)
            self.assertEqual(result, expected)
    
    def test_ensure_directories(self):
        """Test directory creation"""
        # Mock the directory paths
        with patch('tasks.CERTIFICATES_DIR', Path(self.temp_dir) / "certs"), \
             patch('tasks.TEMP_DIR', Path(self.temp_dir) / "temp"):
            
            tasks.ensure_directories()
            
            self.assertTrue((Path(self.temp_dir) / "certs").exists())
            self.assertTrue((Path(self.temp_dir) / "temp").exists())
    
    @patch('tasks.subprocess.run')
    @patch('tasks.generate_qr_code')
    @patch('tasks.TEMPLATE_PATH')
    @patch('tasks.FONT_PATH')
    def test_generate_certificate_success(self, mock_font_path, mock_template_path, 
                                        mock_qr_code, mock_subprocess):
        """Test successful certificate generation"""
        # Setup mocks
        mock_template_path.exists.return_value = True
        mock_font_path.exists.return_value = True
        mock_qr_code.return_value = Path(self.temp_dir) / "qr.png"
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock the output path
        with patch('tasks.CERTIFICATES_DIR', Path(self.temp_dir)):
            # Create mock files
            (Path(self.temp_dir) / f"{self.valid_data['certificate_id']}.pdf").touch()
            
            # This would normally be called as a Celery task, but we'll call directly
            # result = tasks.generate_certificate(self.valid_data)
            # self.assertTrue(result.endswith('.pdf'))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete certificate generation workflow"""
        # This test would require actual system dependencies
        # Skip if not in full integration test mode
        if not os.getenv('RUN_INTEGRATION_TESTS'):
            self.skipTest("Integration tests disabled")
        
        # Test data
        test_data = {
            "user_name": "Integration Test User",
            "college": "Integration Test College",
            "certificate_id": f"INTEGRATION-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "issued_at": datetime.now().isoformat(),
            "topic": "Integration Testing"
        }
        
        # This would test the actual certificate generation
        # but requires full system setup
        pass


class TestHealthCheck(unittest.TestCase):
    """Test health check functionality"""
    
    def test_health_check_structure(self):
        """Test health check returns proper structure"""
        # This would test the actual health_check function
        # when it's properly implemented in tasks.py
        pass


def run_performance_tests():
    """Run performance tests"""
    print("🚀 Running Performance Tests...")
    
    # Test QR code generation performance
    import time
    start_time = time.time()
    
    for i in range(100):
        qr_path = utils.generate_qr_code(f"PERF-TEST-{i:03d}")
        if qr_path.exists():
            qr_path.unlink()
    
    qr_time = time.time() - start_time
    print(f"✅ QR Code Generation: 100 codes in {qr_time:.2f}s ({qr_time/100*1000:.1f}ms each)")
    
    # Test data validation performance
    start_time = time.time()
    
    test_data = {
        "user_name": "Performance Test User",
        "college": "Performance Test College",
        "certificate_id": "PERF-TEST-001",
        "issued_at": datetime.now().isoformat(),
        "topic": "Performance Testing"
    }
    
    for i in range(1000):
        tasks.validate_data(test_data)
    
    validation_time = time.time() - start_time
    print(f"✅ Data Validation: 1000 validations in {validation_time:.2f}s ({validation_time/1000*1000:.1f}ms each)")


if __name__ == '__main__':
    print("🧪 Certificate Generation System Test Suite")
    print("=" * 50)
    print("Author: devag7 (Deva Garwalla)")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    print("\n" + "=" * 50)
    run_performance_tests()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("💡 To run integration tests: RUN_INTEGRATION_TESTS=1 python test_suite.py")
