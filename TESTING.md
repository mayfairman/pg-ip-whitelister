# Testing Guide

This guide covers the testing strategy and how to run tests for the PG IP Whitelister application.

## Testing Strategy

The application uses a comprehensive testing approach with multiple layers:

### **🧪 Test Types**

1. **Unit Tests** - Test individual functions and classes in isolation
2. **Integration Tests** - Test the interaction between components
3. **API Tests** - Test the Flask API endpoints
4. **Configuration Tests** - Test different environment configurations

### **📁 Test Structure**

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_routes.py           # API endpoint tests
├── test_pangolin_api.py     # PangolinAPI class tests
├── test_config.py           # Configuration system tests
├── test_utils.py            # Utility function tests
└── test_integration.py      # Integration workflow tests
```

## Running Tests

### **🚀 Quick Start**

```bash
# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh coverage
```

### **🔧 Manual Test Execution**

```bash
# Install test dependencies
uv pip install -e ".[dev]"

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_routes.py -v

# Run specific test function
uv run pytest tests/test_routes.py::test_index_route -v
```

## Test Categories

### **🔬 Unit Tests**

Unit tests focus on testing individual components in isolation:

- **PangolinAPI Class** (`test_pangolin_api.py`)
  - API client initialization
  - HTTP request handling
  - Error handling
  - Resource management
  - IP whitelist operations

- **Configuration System** (`test_config.py`)
  - Environment variable loading
  - Configuration inheritance
  - Environment-specific settings
  - Logging setup

- **Utility Functions** (`test_utils.py`)
  - IP address validation
  - Input sanitization
  - Edge case handling

### **🔗 Integration Tests**

Integration tests verify that components work together correctly:

- **API Workflow** (`test_integration.py`)
  - Complete whitelisting workflow
  - Error handling scenarios
  - Concurrent request handling
  - Frontend integration simulation

### **🌐 API Tests**

API tests verify the Flask endpoints:

- **Route Testing** (`test_routes.py`)
  - HTTP status codes
  - Response format validation
  - Error handling
  - Input validation

## Test Fixtures

### **🔧 Available Fixtures**

```python
@pytest.fixture
def app():
    """Create application for testing."""
    # Returns Flask app with TestingConfig

@pytest.fixture
def client(app):
    """Create test client."""
    # Returns Flask test client

@pytest.fixture
def runner(app):
    """Create test runner."""
    # Returns Flask CLI test runner
```

### **🎭 Mocking Strategy**

The tests use extensive mocking to isolate components:

```python
# Mock PangolinAPI class
@patch('app.routes.PangolinAPI')
def test_resources_route(mock_pangolin_api_class, client):
    mock_api = MagicMock()
    mock_pangolin_api_class.return_value = mock_api
    mock_api.get_resources.return_value = [...]
```

## Coverage

### **📊 Coverage Reports**

```bash
# Generate HTML coverage report
uv run pytest tests/ --cov=app --cov-report=html

# View coverage in terminal
uv run pytest tests/ --cov=app --cov-report=term-missing
```

### **🎯 Coverage Targets**

- **Overall Coverage**: >90%
- **Critical Paths**: 100%
- **Error Handling**: >95%

## Continuous Integration

### **🔄 CI/CD Integration**

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    uv pip install -e ".[dev]"
    uv run pytest tests/ --cov=app --cov-report=xml
```

### **🚦 Test Quality Gates**

- All tests must pass
- Coverage must be >90%
- No linting errors
- Type checking must pass

## Debugging Tests

### **🐛 Common Issues**

1. **Import Errors**: Ensure test dependencies are installed
2. **Mock Issues**: Check mock setup and return values
3. **Configuration**: Verify TestingConfig is used

### **🔍 Debug Commands**

```bash
# Run tests with debug output
uv run pytest tests/ -v -s

# Run single test with debug
uv run pytest tests/test_routes.py::test_index_route -v -s

# Run with print statements
uv run pytest tests/ -s
```

## Best Practices

### **✅ Test Writing Guidelines**

1. **Descriptive Names**: Use clear, descriptive test names
2. **Arrange-Act-Assert**: Structure tests in AAA pattern
3. **Isolation**: Each test should be independent
4. **Mocking**: Mock external dependencies
5. **Edge Cases**: Test boundary conditions and error scenarios

### **📝 Test Documentation**

```python
def test_whitelist_success(mock_pangolin_api_class, client):
    """Test successful IP whitelisting.
    
    This test verifies that:
    - Valid IP addresses are accepted
    - API calls are made correctly
    - Success responses are returned
    """
```

## Performance Testing

### **⚡ Load Testing**

For performance testing, consider:

```python
def test_concurrent_requests(client):
    """Test handling of concurrent requests."""
    # Uses threading to simulate concurrent users
```

### **📈 Performance Metrics**

- Response time < 500ms
- Concurrent request handling
- Memory usage under load

## Security Testing

### **🔒 Security Considerations**

- Input validation testing
- Authentication/authorization (if added)
- SQL injection prevention (if using databases)
- XSS prevention (frontend validation)

## Future Enhancements

### **🚀 Planned Improvements**

1. **Property-based Testing**: Using Hypothesis for property-based tests
2. **Contract Testing**: API contract validation
3. **Performance Testing**: Load and stress testing
4. **Security Testing**: Automated security scanning
5. **Visual Testing**: Frontend visual regression testing

## Troubleshooting

### **❌ Common Problems**

1. **Test Environment**: Ensure proper test configuration
2. **Dependencies**: Install all test dependencies
3. **Mocking**: Verify mock setup and teardown
4. **Database**: Use test database or mocks
5. **External APIs**: Mock all external API calls

### **🔧 Debug Tools**

- `pytest --pdb`: Drop into debugger on failures
- `pytest --lf`: Run only failed tests
- `pytest --durations=10`: Show slowest tests 