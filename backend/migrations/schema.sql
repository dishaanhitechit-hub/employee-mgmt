-- HR Portal SaaS — PostgreSQL Schema
-- Run this once against your database before seeding.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Organizations ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS organizations (
    id         UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    domain     VARCHAR(200) UNIQUE NOT NULL,
    plan       VARCHAR(50)  NOT NULL DEFAULT 'starter',
    is_active  BOOLEAN      NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Modules (system-global, not per-org) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS modules (
    id          SERIAL       PRIMARY KEY,
    code        VARCHAR(50)  UNIQUE NOT NULL,
    label       VARCHAR(100) NOT NULL,
    description TEXT,
    icon        VARCHAR(50),
    sort_order  INT          NOT NULL DEFAULT 0
);

-- ── Roles (per org) ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL       PRIMARY KEY,
    org_id      UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(50)  NOT NULL,
    description TEXT,
    is_system   BOOLEAN      NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, code)
);

-- ── Role Permissions ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS role_permissions (
    id         SERIAL  PRIMARY KEY,
    role_id    INT     NOT NULL REFERENCES roles(id)   ON DELETE CASCADE,
    module_id  INT     NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    can_view   BOOLEAN NOT NULL DEFAULT false,
    can_create BOOLEAN NOT NULL DEFAULT false,
    can_edit   BOOLEAN NOT NULL DEFAULT false,
    can_delete BOOLEAN NOT NULL DEFAULT false,
    UNIQUE(role_id, module_id)
);

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    org_id        UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role_id       INT          NOT NULL REFERENCES roles(id),
    email         VARCHAR(200) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    is_active     BOOLEAN      NOT NULL DEFAULT true,
    last_login    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, email)
);

-- ── Departments ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id          SERIAL       PRIMARY KEY,
    org_id      UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    head_id     INT,          -- FK set after employees exist
    UNIQUE(org_id, name)
);

-- ── Employees ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employees (
    id                SERIAL       PRIMARY KEY,
    org_id            UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    employee_id       VARCHAR(20)  NOT NULL,
    full_name         VARCHAR(200) NOT NULL,
    email             VARCHAR(200) NOT NULL,
    phone             VARCHAR(20),
    date_of_birth     DATE,
    department_id     INT          REFERENCES departments(id) ON DELETE SET NULL,
    designation       VARCHAR(150),
    employment_type   VARCHAR(50)  CHECK (employment_type IN ('Full-Time','Part-Time','Contract','Intern')),
    joining_date      DATE,
    employment_status VARCHAR(50)  CHECK (employment_status IN ('Active','Inactive','On Leave')),
    manager_id        INT          REFERENCES employees(id) ON DELETE SET NULL,
    work_location     VARCHAR(100),
    annual_ctc        NUMERIC(14,2),
    user_id           UUID         REFERENCES users(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, employee_id),
    UNIQUE(org_id, email)
);

-- Add FK after employees table exists
ALTER TABLE departments
    ADD CONSTRAINT fk_dept_head
    FOREIGN KEY (head_id) REFERENCES employees(id) ON DELETE SET NULL
    NOT VALID;    -- NOT VALID allows adding without scanning existing rows

-- ── Skills ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skills (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS employee_skills (
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    skill_id    INT NOT NULL REFERENCES skills(id)    ON DELETE CASCADE,
    PRIMARY KEY (employee_id, skill_id)
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_emp_org       ON employees(org_id);
CREATE INDEX IF NOT EXISTS idx_emp_dept      ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_emp_mgr       ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_emp_status    ON employees(employment_status);
CREATE INDEX IF NOT EXISTS idx_users_org     ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_roles_org     ON roles(org_id);
CREATE INDEX IF NOT EXISTS idx_dept_org      ON departments(org_id);
