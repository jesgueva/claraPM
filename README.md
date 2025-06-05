# Clara Project Manager API

Clara PM is a project management application with a conversational interface powered by AI.

## Project Structure

```
claraPM/
├── intake_agent/           # Main application package
│   ├── auth.py             # Authentication and user management
│   ├── controller.py       # API route handlers
│   ├── db_operations.py    # Database operations
│   ├── langchain_service.py # AI service integration
│   ├── logger/             # Logging module
│   │   ├── __init__.py     # Logger initialization
│   │   └── config.py       # Logger configuration
│   └── server.py           # FastAPI server implementation
├── logs/                   # Log files directory
│   ├── agent.log           # Agent activity logs
│   ├── conversation.log    # Conversation logs
│   ├── db.log              # Database operation logs
│   └── system.log          # System logs
├── tests/                  # Test suite
│   ├── run_tests.py        # Test runner
│   ├── test_auth_sessions.py # Authentication and session tests
│   ├── test_logger_unit.py  # Logger unit tests
│   └── ...                 # Other test files
├── main.py                 # Main entry point
└── run.py                  # Run script
```

## Features

- **User Authentication**: JWT-based auth with role-based access control
- **Session Management**: Persistent user-specific conversation sessions
- **Conversation History**: Track and maintain conversation context
- **Comprehensive Logging**: Detailed logs for all system components
- **AI Integration**: LangChain integration for natural language processing

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python run.py
   ```
   
The API will be available at http://localhost:8000, with interactive documentation at http://localhost:8000/docs.

## API Endpoints

- `/token` - Get authentication token
- `/users/me` - Get current user info
- `/intake/query` - Submit a query to the AI agent
- `/intake/sessions` - List user sessions
- `/intake/sessions/{session_id}` - Get, update, or delete a specific session

## Testing

Run all tests:
```
python tests/run_tests.py
```

Or run a specific test:
```
python -m pytest tests/test_logger_unit.py -v
``` 