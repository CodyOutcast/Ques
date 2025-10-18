# Testing Documentation

This folder contains all testing files and documentation for the Ques backend.

## 📁 Folder Structure

### `/unit`
Unit tests for individual components
- Model tests
- Service tests  
- Utility function tests
- Individual router endpoint tests

### `/integration`
Integration tests for complete workflows
- End-to-end API tests
- Database integration tests
- Service integration tests
- Authentication flow tests

### `/fixtures`
Test data and fixtures
- Sample user data
- Mock responses
- Database seed data
- Test configuration files

## 🧪 Test Files

### Current Test Files
- `test_basic_operations.py` - Basic API operations testing
- `validate_models.py` - Model validation tests
- `inspect_database_schema.py` - Database schema inspection

## 🚀 Running Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio httpx
```

### Run All Tests
```bash
# From backend root directory
pytest tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Specific test file
pytest tests/test_basic_operations.py
```

### Run with Coverage
```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

## 🔧 Test Configuration

### Environment Variables
Create a `.env.test` file for test-specific configuration:
```env
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=test_secret_key
TESTING=true
```

### Test Database
Tests should use a separate test database to avoid affecting development data.

## 📝 Writing Tests

### Test File Naming
- Unit tests: `test_<component>_unit.py`
- Integration tests: `test_<feature>_integration.py`  
- Fixtures: `<data_type>_fixtures.py`

### Test Structure Example
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoint_success():
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert "expected_key" in response.json()

def test_endpoint_error():
    response = client.get("/api/v1/endpoint?invalid=param")
    assert response.status_code == 400
```

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest tests/ -v
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Specific Test
```bash
pytest tests/test_file.py::test_function_name
```