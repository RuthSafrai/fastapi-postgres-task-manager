# Team Task Manager API

A RESTful API for managing development team projects, tasks, and comments, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Alembic**.  
Features **JWT authentication**, **Role-Based Access Control (RBAC)**, filtering, pagination, and database schema migrations.

---

## Key Features

- **JWT Authentication:** OAuth2 password flow (`POST /auth/login`) supporting login via either **username** or **email**, with `bcrypt` password hashing.
- **Role-Based Access Control (RBAC):** Fine-grained permissions for **Admin**, **Secretary**, and **Developer** roles, including resource ownership checks.
- **Projects, Tasks & Comments:** Full CRUD for tasks, project assignment, task status/priority validation via Enums, and task-scoped comments with automatic cascade deletion.
- **Filtering & Pagination:** Filter tasks by status, priority, assignee, or project, with `skip` and `limit` pagination across list endpoints.
- **Database Migrations:** Managed with **Alembic** and SQLAlchemy ORM.

---

## Tech Stack

- **Framework:** FastAPI, Uvicorn
- **Database & ORM:** PostgreSQL, SQLAlchemy 2.x, Alembic
- **Validation:** Pydantic v2 (`EmailStr`, Enums, custom validators)
- **Security:** `python-jose` (HS256 JWT), `bcrypt`, `python-dotenv`

---

## Project Structure

```text
├── alembic/
│   ├── versions/          # Database migration scripts
│   └── env.py             # Alembic environment configuration
├── auth.py                # Login endpoint, JWT bearer dependency & role guards
├── create_admin.py        # CLI script to bootstrap or promote an admin user
├── create_db.py           # Initial table creation helper
├── database.py            # SQLAlchemy engine, SessionLocal & get_db dependency
├── enums.py               # Role, TaskStatus, and TaskPriority enums
├── main.py                # Application routes (Users, Projects, Tasks, Comments)
├── models.py              # SQLAlchemy ORM models
├── permissions.py         # Ownership and role-based permission helpers
├── schemas.py             # Pydantic request/response schemas
├── security.py            # Password hashing & JWT encoding/decoding
├── requirements.txt       # Python dependencies
└── sample.env             # Environment variables template
```

---

## Setup & Installation

### 1. Clone & Install Dependencies

```bash
git clone [https://github.com/RuthSafrai/fastapi-postgres-task-manager.git](https://github.com/RuthSafrai/fastapi-postgres-task-manager.git)
cd fastapi-postgres-task-manager
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `sample.env` to `.env` and fill in your values:

```bash
cp sample.env .env
```

```env
DATABASE_URL=postgresql://user:password@localhost:5432/task_manager_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Initialize the Database

- **For a fresh database:**
  ```bash
  python create_db.py
  alembic stamp head
  ```
- **For an existing database (applying schema updates):**
  ```bash
  alembic upgrade head
  ```

### 4. Create the First Admin User

Since creating users via the API requires an `admin` account, run the interactive CLI helper to create your first admin (or promote an existing user):

```bash
python create_admin.py
```

### 5. Run the Server

```bash
uvicorn main:app --reload
```

Interactive API documentation (Swagger UI) is available at:  
**http://127.0.0.1:8000/docs**

---

## Roles & Permissions

| Role | Users | Projects | Tasks | Comments |
|------|-------|----------|-------|----------|
| **`admin`** | Full CRUD (blocks deletion if user has tasks/comments) | Create & read all | Full CRUD & reassign across all users | Read & post on any task |
| **`secretary`** | Read all | Read all | Read-only across all tasks | Read-only across all tasks |
| **`developer`** | Read own profile | Read projects with assigned tasks | Create for self; read/update/delete own tasks | Read & post on own tasks |

---

## API Endpoints

All endpoints except `POST /auth/login` require a valid `Authorization: Bearer <token>` header.

### Auth
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/auth/login` | Authenticate with `username` (or `email`) & `password` to receive a JWT | Public |
| `GET` | `/auth/me` | Get the currently authenticated user's profile | Authenticated |

### Users
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/users` | Create a new user | Admin |
| `GET` | `/users` | List users (supports `skip`, `limit`) | Admin/Secretary (all), Developer (self) |
| `GET` | `/users/{user_id}` | Get user details by ID | Admin/Secretary, or self |
| `DELETE` | `/users/{user_id}` | Delete user (`409` if user has tasks or comments) | Admin |

### Projects
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/projects` | Create a new project | Admin |
| `GET` | `/projects` | List projects (supports `skip`, `limit`) | Admin/Secretary (all), Developer (assigned) |
| `GET` | `/projects/{project_id}` | Get project details by ID | Admin/Secretary, or Developer with task in project |

### Tasks
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/tasks` | Create a new task | Admin, Developer (self only) |
| `GET` | `/tasks` | List tasks with filters (`status_filter`, `priority`, `user_id`, `project_id`) & pagination (`skip`, `limit`) | Admin/Secretary (all), Developer (own) |
| `GET` | `/tasks/{task_id}` | Get task details by ID | Admin/Secretary, or task owner |
| `PUT` | `/tasks/{task_id}` | Partially update a task | Admin, or task owner |
| `DELETE` | `/tasks/{task_id}` | Delete a task (cascades its comments) | Admin, or task owner |

### Comments
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/tasks/{task_id}/comments` | Add a comment to a task (author is set automatically from JWT) | Admin, or task owner |
| `GET` | `/tasks/{task_id}/comments` | List comments on a task ordered chronologically (supports `skip`, `limit`) | Admin/Secretary, or task owner |

---

## Data Model

- **`users`**: `id`, `name`, `username` (unique), `email` (unique), `password` (hashed), `role` (`admin` / `secretary` / `developer`), `is_active`, `created_at`
- **`projects`**: `id`, `name`, `description`, `created_at`
- **`tasks`**: `id`, `title`, `description`, `status` (`todo` / `in_progress` / `done`), `priority` (`low` / `medium` / `high`), `due_date`, `estimated_hours`, `user_id` (FK), `project_id` (FK), `created_at`
- **`comments`**: `id`, `content`, `task_id` (FK, `ON DELETE CASCADE`), `user_id` (FK), `created_at`