# Ques Backend Testing Suite

## 🧪 Overview

This directory contains all testing and verification scripts for the Ques backend system, organized by test type and purpose.

## 📁 Structure

```
tests/
├── run_tests.py              # Main test runner script
├── database/                 # Database verification tests
│   ├── check_db_state.py     # Database state verification
│   ├── check_new_tables.py   # New tables validation
│   ├── check_user_swipes.py  # User swipes table verification
│   └── verify_chat_tables.py # Chat system tables verification
├── integration/              # Integration tests
│   ├── test_api_endpoints.py    # API endpoints testing
│   ├── test_chat_integration.py # Chat system integration
│   ├── test_final_integration.py # Complete system integration
│   └── test_tpns_integration.py  # TPNS integration testing
└── unit/                     # Unit tests (if any)
```

## 🚀 Quick Start

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Category
```bash
# Database verification only
python tests/run_tests.py database

# Integration tests only
python tests/run_tests.py integration

# Unit tests only
python tests/run_tests.py unit
```

### Run Individual Tests
```bash
# Database tests
python tests/database/check_db_state.py
python tests/database/verify_chat_tables.py

# Integration tests
python tests/integration/test_final_integration.py
python tests/integration/test_chat_integration.py
```

## 🔍 Test Categories

### Database Tests (`database/`)
These tests verify database schema, table structure, and data integrity:

- **`check_db_state.py`** - Verifies overall database health and connectivity
- **`check_new_tables.py`** - Validates newly created tables and schema
- **`check_user_swipes.py`** - Checks user swipes table structure and constraints
- **`verify_chat_tables.py`** - Verifies chat system tables and relationships

### Integration Tests (`integration/`)
These tests verify system components working together:

- **`test_api_endpoints.py`** - Tests all API endpoints for correct responses
- **`test_chat_integration.py`** - Tests AI-powered chat system integration
- **`test_final_integration.py`** - Complete end-to-end system testing
- **`test_tpns_integration.py`** - Tests push notification system integration

## 📋 Pre-test Requirements

### Environment Setup
Ensure these are configured before running tests:

1. **Database Connection**
   ```bash
   # Check database environment variables
   echo $DATABASE_URL
   # or check .env file
   ```

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **API Keys** (for integration tests)
   - GLM-4 API key
   - TPNS credentials
   - Other service keys in `.env`

### Database State
- Database should be properly migrated
- Required tables should exist
- Sample data may be needed for some tests

## 🛠️ Test Runner Features

The `run_tests.py` script provides:

- **Parallel Execution**: Runs tests efficiently
- **Detailed Reporting**: Shows pass/fail status with timing
- **Error Capture**: Captures and displays error details
- **Summary Statistics**: Overall test success rate
- **Selective Running**: Run specific test categories

### Example Output
```
============================================================
 QUES BACKEND TEST SUITE
============================================================

🧪 Running: Database State Verification
   File: tests/database/check_db_state.py
   ✅ PASSED (1.23s)

🧪 Running: Chat System Integration
   File: tests/integration/test_chat_integration.py
   ✅ PASSED (3.45s)

============================================================
 TEST EXECUTION SUMMARY
============================================================
Total Tests Run: 8
✅ Passed: 7
❌ Failed: 1
📊 Success Rate: 87.5%
```

## 🐛 Debugging Failed Tests

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database is running
   python -c "from config.database import engine; print('DB OK')"
   ```

2. **Missing Environment Variables**
   ```bash
   # Check .env file exists and has required variables
   cat .env | grep -E "(DATABASE_URL|GLM_4_API_KEY)"
   ```

3. **API Service Errors**
   ```bash
   # Test external services manually
   python -c "from services.glm4_client import GLM4Client; print('GLM4 OK')"
   ```

### Debug Individual Tests
```bash
# Run with verbose output
python tests/database/check_db_state.py --verbose

# Run with debug logging
PYTHONPATH=. python tests/integration/test_chat_integration.py --debug
```

## 📊 Test Coverage

### Current Coverage Areas
- ✅ Database schema validation
- ✅ API endpoint functionality
- ✅ Chat system with AI integration
- ✅ User authentication flow
- ✅ Swipe mechanics
- ✅ Push notification system

### Areas for Expansion
- 🔄 Performance testing
- 🔄 Load testing
- 🔄 Security testing
- 🔄 Mock external services

## 🔄 Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: python tests/run_tests.py
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests before commits
echo "python tests/run_tests.py" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 📝 Adding New Tests

### Database Tests
1. Create test file in `tests/database/`
2. Follow naming convention: `check_*.py` or `verify_*.py`
3. Include database connection and cleanup
4. Add to test runner if needed

### Integration Tests
1. Create test file in `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Include setup/teardown for test data
4. Test real API endpoints and services

### Best Practices
- Use descriptive test names
- Include proper error handling
- Clean up test data
- Document test purpose and requirements
- Add timeout handling for long-running tests

---

*Last Updated: October 17, 2025*
*Test suite organized for comprehensive backend verification*