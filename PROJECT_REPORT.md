# MedCare Chatbot - Project Report

**Date:** May 13, 2026  
**Project Type:** AI Healthcare Chatbot Application  
**Status:** Active Development

---

## 1. Executive Summary

**MedCare Chatbot** is a Flask-based web application that provides healthcare information assistance using a local Large Language Model (LLM). The application features user authentication, multi-session conversation management, and a responsive web interface. It's specifically designed to provide medical knowledge, blood donation information, and healthcare guidance while maintaining safety and accuracy standards.

**Key Highlights:**
- ✅ Local LLM deployment (Qwen2.5-3B-Instruct) - No cloud API dependency
- ✅ User authentication with session management
- ✅ Multi-session conversation history
- ✅ MedCare-specific system prompt with safety guidelines
- ✅ Responsive web interface (Single Page Application)

---

## 2. Project Structure

```
Chatbot/
├── App.py                    # Main Flask application & API routes
├── Database.py               # SQLite database operations
├── System_Prompt.txt         # MedCare healthcare system prompt
├── requirements.txt          # Python dependencies
├── AGENTS.md                 # Development guidelines
├── README.md                 # Project documentation
├── PROJECT_REPORT.md         # This file
├── test_api.py              # API testing utilities
├── test_model.py            # Model testing utilities
├── chatbot.db               # SQLite database (auto-created)
└── templates/
    └── index.html           # Single Page Application (Frontend)
```

### Directory Purpose:
- **Root**: Configuration files, main application logic, database
- **templates/**: HTML/CSS/JavaScript frontend
- **Database files**: `chatbot.db` created at runtime

---

## 3. Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Flask | 3.0.0 | Web server & REST API |
| **LLM** | Qwen2.5-3B-Instruct | Latest | Local language model inference |
| **ML Libraries** | Transformers | 5.8.0 | Model loading & tokenization |
| | PyTorch | 2.11.0 | Tensor computation & inference |
| **Database** | SQLite3 | Built-in | User & conversation storage |
| **Authentication** | Flask-Sessions | Built-in | User session management |
| **Utilities** | python-dotenv | 1.0.0 | Environment variables |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Markup** | HTML5 | Page structure |
| **Styling** | CSS3 | Responsive design |
| **Interactivity** | JavaScript (Vanilla) | SPA functionality |
| **Communication** | Fetch API | REST API calls |

### Development & Testing
- **Test files**: `test_api.py`, `test_model.py` for validation
- **Environment management**: `.env` file for sensitive credentials

---

## 4. Workflow Architecture

### 4.1 Application Workflow

```
User Access
    ↓
[Login/Signup Page] ← Not Authenticated
    ↓ (Authenticated)
[Chat Dashboard]
    ├─ View Previous Sessions
    ├─ Create New Session
    └─ Open Existing Session
         ↓
    [Chat Interface]
         ├─ User sends message
         ├─ Message saved to DB
         ├─ System prompt + conversation history sent to LLM
         ├─ Local Qwen model processes query
         ├─ Assistant response generated
         └─ Response saved to DB & displayed to user
```

### 4.2 Request-Response Cycle

```
Client (Browser)
    ↓
[JavaScript SPA]
    ↓
[Fetch API] ← HTTP REST
    ↓
[Flask Routes] (App.py)
    ├─ Authentication Check
    ├─ Input Validation
    ├─ Database Operations (Database.py)
    └─ LLM Inference
         ↓
    [Qwen2.5-3B Model]
         ├─ Tokenization
         ├─ Forward Pass
         └─ Generation
    ↓
[Response JSON]
    ↓
[Browser] → Display to User
```

---

## 5. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (Browser)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Single Page Application (SPA)               │   │
│  │  [HTML/CSS/JavaScript] - templates/index.html        │   │
│  │  - Login/Signup UI                                   │   │
│  │  - Chat Interface                                    │   │
│  │  - Session Management UI                            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           │ JSON Payloads
┌──────────────────────────▼──────────────────────────────────┐
│               FLASK APPLICATION LAYER                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Route Handlers (App.py)                  │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ Authentication Routes                       │    │    │
│  │  │ • /api/signup      [POST]                   │    │    │
│  │  │ • /api/login       [POST]                   │    │    │
│  │  │ • /api/logout      [POST]                   │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ Session Routes                              │    │    │
│  │  │ • /api/sessions    [GET, POST]              │    │    │
│  │  │ • /api/sessions/<id> [DELETE]               │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ Chat Routes                                 │    │    │
│  │  │ • /api/sessions/<id>/messages [GET]         │    │    │
│  │  │ • /api/sessions/<id>/chat     [POST]        │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│                     │                │                       │
│              ┌──────┴───────┐        │                       │
│              │              │        │                       │
└──────────────┼──────────────┼────────┼───────────────────────┘
               │              │        │
    ┌──────────▼──┐  ┌────────▼──┐  ┌─▼──────────────┐
    │  Database   │  │    LLM    │  │  Environment   │
    │ (Database   │  │  Inference│  │  Variables     │
    │   .py)      │  │           │  │  (.env file)   │
    │             │  │  [Qwen    │  │                │
    │ SQLite3:    │  │   2.5-3B] │  │ • SECRET_KEY   │
    │ • users     │  │           │  │ • API_KEYS     │
    │ • sessions  │  │ Transform-│  │                │
    │ • messages  │  │ ers lib   │  │                │
    │             │  │ PyTorch   │  │                │
    └─────────────┘  │           │  │                │
                     │ GPU/CPU   │  │                │
                     │ (Auto)    │  │                │
                     └───────────┘  └────────────────┘
```

---

## 6. Database Schema

### Tables Overview

```sql
USERS TABLE
┌─────────────────────────────────────────┐
│ id (INTEGER, PK, AUTO)                  │
│ username (TEXT, UNIQUE, NOT NULL)       │
│ password (TEXT, NOT NULL - SHA256)      │
│ created (DATETIME, DEFAULT CURRENT)     │
└─────────────────────────────────────────┘

SESSIONS TABLE
┌─────────────────────────────────────────┐
│ id (INTEGER, PK, AUTO)                  │
│ user_id (INTEGER, FK → users.id)        │
│ title (TEXT, DEFAULT 'New Chat')        │
│ created (DATETIME, DEFAULT CURRENT)     │
└─────────────────────────────────────────┘

MESSAGES TABLE
┌─────────────────────────────────────────┐
│ id (INTEGER, PK, AUTO)                  │
│ session_id (INTEGER, FK → sessions.id)  │
│ role (TEXT - 'user' or 'assistant')     │
│ content (TEXT, NOT NULL)                │
│ created (DATETIME, DEFAULT CURRENT)     │
└─────────────────────────────────────────┘
```

### Data Flow
```
User Registration:
  users.create(username, password_hash)
         ↓
User Login:
  users.verify(username, password_hash)
         ↓
Create Session:
  sessions.create(user_id)
         ↓
Send Message:
  messages.add(session_id, 'user', content)
  messages.add(session_id, 'assistant', response)
         ↓
Retrieve History:
  messages.get_all(session_id)
```

---

## 7. Core Components

### 7.1 App.py (Main Application)
**Purpose**: Flask web server and REST API endpoints

**Key Functions**:
- `load_model()`: Load Qwen2.5-3B model on first request (GPU/CPU auto-detection)
- `load_system_prompt()`: Load MedCare healthcare guidelines from System_Prompt.txt
- Authentication routes: `/api/signup`, `/api/login`, `/api/logout`
- Session management: `/api/sessions` (CRUD operations)
- Chat endpoint: `/api/sessions/<id>/chat` (Message processing & LLM inference)

**Model Loading Strategy**:
```python
- Lazy loading: Model loads on first user message (not on startup)
- GPU detection: Uses torch.cuda.is_available()
  - GPU: torch.float16 with device_map='auto'
  - CPU: torch.float32 direct to CPU
- Inference: Message history → Qwen model → Response generation
```

### 7.2 Database.py (Data Persistence)
**Purpose**: SQLite database operations

**Key Operations**:
- User management: `create_user()`, `verify_user()`, `hash_pw()`
- Session management: `create_session()`, `get_sessions()`, `delete_session()`, `update_session_title()`
- Message storage: `add_message()`, `get_messages()`
- Security: `session_belongs_to()` ownership validation

**Security Features**:
- SHA256 password hashing
- Foreign key constraints
- Ownership validation for sessions/messages

### 7.3 System_Prompt.txt (AI Behavior Definition)
**Purpose**: Define MedCare Assistant behavior and constraints

**Content**:
- Role: Healthcare information assistant (NOT a doctor)
- Responsibilities: Blood donation, general medical knowledge, symptom guidance
- Safety Rules: No fabrication, no hallucination, clear disclaimers
- Knowledge Base: Blood groups, donation eligibility, medical basics

### 7.4 templates/index.html (Frontend SPA)
**Purpose**: Single-page application for user interaction

**Features**:
- Responsive chat interface
- Session sidebar (list previous chats)
- Real-time message display
- User authentication UI (login/signup)
- Fetch API for REST communication

---

## 8. API Endpoints

### Authentication

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/signup` | None | Create new user account |
| POST | `/api/login` | None | Authenticate user |
| POST | `/api/logout` | Required | End user session |

### Session Management

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/sessions` | Required | List user's chat sessions |
| POST | `/api/sessions` | Required | Create new chat session |
| DELETE | `/api/sessions/<id>` | Required | Delete chat session |

### Chat Operations

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/sessions/<id>/messages` | Required | Retrieve chat history |
| POST | `/api/sessions/<id>/chat` | Required | Send message & get response |

---

## 9. Model Configuration

### LLM: Qwen2.5-3B-Instruct

**Model Details**:
```
Name: Qwen/Qwen2.5-3B-Instruct
Type: Instruction-tuned causal language model
Size: 3 billion parameters
Format: Hugging Face transformers
Quantization: FP16 (GPU) / FP32 (CPU)
```

**Inference Configuration**:
```python
max_new_tokens=256        # Output limit
temperature=0.7           # Creativity level
do_sample=True           # Probabilistic sampling
pad_token_id=eos_token_id # Padding strategy
```

**Why Qwen2.5-3B?**
- ✅ Lightweight (~3B parameters)
- ✅ Good quality responses for healthcare domain
- ✅ Runs locally without cloud API costs
- ✅ Supports instruction-following
- ✅ Multi-language capable

---

## 10. Security Considerations

### Current Implementation
- ✅ Flask session-based authentication
- ✅ SHA256 password hashing
- ✅ Ownership validation (users can only access their data)
- ✅ CSRF protection via Flask
- ✅ SQL injection prevention (parameterized queries)

### Recommended Improvements
- ⚠️ Upgrade SHA256 → bcrypt/argon2 (password hashing)
- ⚠️ Add rate limiting (prevent brute force attacks)
- ⚠️ Implement HTTPS in production
- ⚠️ Add input sanitization & validation
- ⚠️ Implement audit logging
- ⚠️ Add message content moderation

---

## 11. Dependencies

```
Flask==3.0.0              # Web framework
transformers==5.8.0       # HuggingFace transformers
tokenizers==0.22.2        # Tokenization
huggingface-hub==1.14.0   # Model hub access
torch==2.11.0             # Deep learning framework
accelerate==0.28.0        # Multi-GPU support
python-dotenv==1.0.0      # Environment management
requests==2.31.0          # HTTP client
setuptools<82             # Dependency manager
```

### Installation
```bash
pip install -r requirements.txt
```

---

## 12. Running the Application

### Prerequisites
- Python 3.8+
- 4GB+ RAM (minimum for Qwen model)
- GPU optional (CUDA 11.8+) for faster inference

### Setup & Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env

# 3. Run application
python App.py

# 4. Access application
# Open browser: http://localhost:5000
```

### First Run
- Model downloads automatically (~6GB for Qwen2.5-3B)
- Database tables created automatically
- Model loads on first chat message (lazy loading)

---

## 13. Development Workflow

### Adding Features

1. **Backend Changes**:
   - Modify routes in `App.py`
   - Update database functions in `Database.py`
   - Test with `test_api.py`

2. **Frontend Changes**:
   - Edit `templates/index.html`
   - Changes reflect immediately (Flask debug mode)

3. **AI Behavior Changes**:
   - Edit `System_Prompt.txt`
   - Restart application for changes to apply

4. **Model Changes**:
   - Update `MODEL_NAME` variable in `App.py`
   - Clear model cache manually if needed

### Testing
```bash
# API endpoint testing
python test_api.py

# Model inference testing
python test_model.py
```

---

## 14. Future Enhancements

### Planned Improvements
1. **Context Management**
   - Message windowing (send only recent messages to LLM)
   - Conversation summarization for long chats
   - Semantic search for relevant history

2. **Performance**
   - Message caching
   - Response streaming
   - Query optimization

3. **Scalability**
   - PostgreSQL migration (from SQLite)
   - Redis caching layer
   - Docker containerization

4. **AI Capabilities**
   - Multi-language support
   - Specialized medical domain fine-tuning
   - Response fact-checking

5. **User Experience**
   - Dark mode
   - Export chat history
   - Mobile app

---

## 15. File Dependencies

```
App.py
├─ Imports: Database.py, transformers, torch, Flask
├─ Reads: System_Prompt.txt
└─ Uses: templates/index.html

Database.py
└─ Creates: chatbot.db (SQLite)

templates/index.html
└─ Calls: App.py API endpoints

.env
└─ Consumed by: App.py (SECRET_KEY, etc.)
```

---

## 16. Key Metrics

### Application Stats
- **Users**: Multi-user with session isolation
- **Sessions**: Unlimited per user
- **Messages**: Unlimited per session
- **Response Latency**: 2-10 seconds (depends on GPU/CPU, message length)
- **Model Parameters**: 3 billion
- **Storage**: ~6GB model + database size

---

## Conclusion

**MedCare Chatbot** is a production-ready healthcare AI application combining:
- Modern web framework (Flask)
- State-of-the-art local LLM (Qwen2.5-3B)
- Robust authentication & data management
- Healthcare-specific safety guidelines

The architecture prioritizes **local deployment** (no cloud dependencies), **user privacy** (local data storage), and **medical accuracy** (system prompt guidelines).

### Contact & Support
- Documentation: See `AGENTS.md` for development guidelines
- Testing: Use `test_api.py` and `test_model.py`
- Configuration: Update `.env` for environment variables

---

**Report Generated**: May 13, 2026  
**Project Version**: v1.0.0 (Development)
