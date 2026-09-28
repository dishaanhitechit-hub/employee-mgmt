# HR Portal — SaaS Employee Management System

A multi-tenant HR ERP portal with RBAC, JWT authentication, and module-level permissions.

## Tech Stack
- **Backend** Python 3.11 · Flask · psycopg2 · flask-jwt-extended · bcrypt
- **Database** PostgreSQL
- **Frontend** Vanilla HTML / CSS / JavaScript

## Project Structure
```
employee-mgmt/
├── backend/
│   ├── app.py                  # Flask app factory + blueprint registration
│   ├── config.py               # Environment config
│   ├── extensions.py           # DB helper (query / execute)
│   ├── models/                 # Data access layer (raw SQL)
│   │   ├── organization.py
│   │   ├── module.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── employee.py
│   │   └── skill.py
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── organization_service.py
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   ├── permission_service.py
│   │   ├── employee_service.py
│   │   └── department_service.py
│   ├── routes/                 # HTTP layer (one Blueprint per module)
│   │   ├── auth_routes.py
│   │   ├── organization_routes.py
│   │   ├── user_routes.py
│   │   ├── role_routes.py
│   │   ├── permission_routes.py
│   │   ├── employee_routes.py
│   │   ├── department_routes.py
│   │   └── stats_routes.py
│   ├── middleware/
│   │   ├── auth_middleware.py       # @require_auth
│   │   └── permission_middleware.py # @require_permission(MODULE, action)
│   ├── utils/
│   │   ├── response.py             # Standardised JSON responses
│   │   └── validators.py
│   ├── migrations/
│   │   └── schema.sql              # Run this first
│   ├── seeding.py                  # Seed 20 employees + demo users
│   └── requirements.txt
└── frontend/
    ├── index.html              # Login page
    ├── dashboard.html
    ├── employees.html
    ├── employee-detail.html
    ├── departments.html
    ├── users.html
    └── roles.html
```

## Prerequisites
- Python 3.11+
- PostgreSQL 14+

## Setup

### 1. Create database
```sql
CREATE DATABASE hr_portal;
```

### 2. Run schema
```bash
psql -U postgres -d hr_portal -f backend/migrations/schema.sql
```

### 3. Configure environment
```bash
cp .env.example backend/.env
# Edit backend/.env with your DATABASE_URL and JWT_SECRET
```

### 4. Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Seed demo data
```bash
cd backend
python seeding.py
```

### 6. Start the server
```bash
cd backend
python app.py
```

Open **http://localhost:5000**

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@acmecorp.io | Admin@123 | Super Admin |
| hrmanager@acmecorp.io | Admin@123 | HR Manager |
| manager@acmecorp.io | Admin@123 | Manager |
| employee@acmecorp.io | Admin@123 | Employee |

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login → access + refresh tokens |
| POST | /api/auth/refresh | Refresh access token |
| GET | /api/auth/me | Current user + permissions |
| POST | /api/auth/logout | Logout |

### Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/employees | List (search, department, status filters) |
| GET | /api/employees/:id | Single employee profile |
| POST | /api/employees | Create |
| PUT | /api/employees/:id | Update |
| DELETE | /api/employees/:id | Delete |

### Departments
| GET/POST | /api/departments | List / Create |
| GET/PUT/DELETE | /api/departments/:id | Read / Update / Delete |

### Roles & Permissions
| GET/POST | /api/roles | List roles / Create |
| GET/PUT/DELETE | /api/roles/:id | Role detail / Update / Delete |
| PUT | /api/roles/:id/permissions | Set full permission matrix |

### Users
| GET/POST | /api/users | List / Create |
| GET/PUT/DELETE | /api/users/:id | Detail / Update / Delete |
| POST | /api/users/:id/change-password | Change password |

### Other
| GET | /api/stats | Dashboard summary |
| GET | /api/permissions/modules | All HR modules |
| GET | /api/permissions/my-permissions | Current user's permission map |

## RBAC & Permission System

Every API route is protected by two decorators:

```python
@bp.get("/")
@require_auth                          # Verifies JWT, sets g.user
@require_permission("EMPLOYEES", "view")  # Checks role_permissions table
def list_employees():
    ...
```

Permission matrix is editable per-role via **Roles & Permissions** page.
The frontend reads the `permissions` object from the login response and
hides navigation items and action buttons the user cannot access.

## HR Modules
DASHBOARD · EMPLOYEES · DEPARTMENTS · PAYROLL · ATTENDANCE · LEAVES · PERFORMANCE · RECRUITMENT · REPORTS · USER_MANAGEMENT · ROLE_MANAGEMENT
