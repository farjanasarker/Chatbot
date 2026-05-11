# Chatbot Development Agent Instructions

## Project Overview
This is a Flask-based AI chatbot with user authentication, session management, and Groq API integration using Llama 3.1 models. The app provides a web interface for conversational AI interactions with persistent chat history.

## Architecture
- **Backend**: Flask web framework with SQLite database
- **Frontend**: Single-page HTML/CSS/JavaScript application
- **AI**: Groq API with Llama 3.1-8b-instant model
- **Database**: SQLite with users, sessions, and messages tables

## Current Context Handling Issues
- All conversation messages sent to API on every request (no windowing)
- No message summarization or semantic search
- Linear message retrieval without prioritization
- No context compression for long conversations

## Development Conventions
- **Routes**: RESTful JSON APIs with `/api/` prefix
- **Auth**: Flask session-based with ownership validation
- **Database**: Simple functions in `Database.py` (no ORM)
- **Error Handling**: Basic try/catch with user-friendly messages
- **Security**: SHA256 password hashing (upgrade to bcrypt recommended)

## Build & Run
```bash
python App.py  # Runs on http://localhost:5000
```
Requires: `GROQ_API_KEY` and `SECRET_KEY` environment variables.

## Context Understanding Framework Goals
When implementing context improvements:
1. **Windowing**: Limit messages sent to API (last 10-15 turns)
2. **Summarization**: Compress old conversation segments
3. **Semantic Search**: Enable retrieval of relevant past context
4. **Caching**: Avoid re-encoding unchanged message history
5. **Metadata**: Add message tags, intent classification, timestamps

## Key Files
- [App.py](App.py) - Main Flask application and API routes
- [Database.py](Database.py) - SQLite database operations
- [templates/index.html](templates/index.html) - Frontend SPA
- [.env](.env) - Environment configuration

## Implementation Priorities
1. **Safety**: Upgrade password hashing, improve error handling
2. **Performance**: Message windowing, API retry logic
3. **Context Quality**: Summarization, semantic retrieval
4. **Scalability**: Database optimization, caching layer

## Testing
- Manual testing via browser interface
- API testing with curl/Postman
- Database integrity checks after changes

## Deployment Considerations
- Environment variables for production secrets
- Database migrations for schema changes
- Static file serving optimization
- Rate limiting for API endpoints</content>
<parameter name="filePath">d:\Git\New folder\Chatbot\AGENTS.md