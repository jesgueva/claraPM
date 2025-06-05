# Clara PM Tests

This directory contains tests for the Clara Project Manager system.

## Test Structure

- `run_tests.py` - Main test runner that executes all tests and provides a summary
- `test_logger_unit.py` - Unit tests for the logger module
- `test_logging.py` - Standalone test for the logging system
- `test_session.py` - Standalone test for session management

## Running Tests

### Running All Tests

To run all tests at once, use the test runner:

```bash
cd tests
python run_tests.py
```

This will:
1. Run all unittest-based tests
2. Run all standalone tests
3. Provide a summary of the results

### Running Individual Tests

You can also run individual test files directly:

```bash
# Run logger unit tests
python test_logger_unit.py

# Run logging standalone test
python test_logging.py

# Run session management test (requires server to be running)
python test_session.py
```

## Test Types

### Unit Tests

Unit tests are based on the Python `unittest` framework and test individual components in isolation. These tests use assertions to verify the behavior of the system.

### Standalone Tests

Standalone tests are script-based tests that verify specific functionality through a series of operations. These tests typically print their results rather than using assertions.

## Adding New Tests

When adding new tests:

1. For unit tests:
   - Create a new file with the naming pattern `test_*.py`
   - Use the `unittest` framework
   - Add test methods with names starting with `test_`

2. For standalone tests:
   - Create a new file with the naming pattern `test_*.py`
   - Include a main function that runs the test
   - Make sure the script can be run directly

3. Make sure to add the parent directory to the Python path:
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   ```

## Test Logs

Some tests may create temporary log files in a `test_logs` directory. These are automatically cleaned up after the tests run. 