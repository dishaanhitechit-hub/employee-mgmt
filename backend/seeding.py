import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models.organization import Organization
from models.module       import Module
from models.role         import Role
from models.permission   import RolePermission
from models.user         import User
from models.department   import Department
from models.employee     import Employee
from models.skill        import Skill


MODULES = [
    ("DASHBOARD",       "Dashboard",          "Overview and key metrics",              "grid",        1),
    ("EMPLOYEES",       "Employees",          "Employee directory and profiles",        "users",       2),
    ("DEPARTMENTS",     "Departments",        "Department structure",                   "building",    3),
    ("PAYROLL",         "Payroll",            "Salary and compensation management",     "dollar-sign", 4),
    ("ATTENDANCE",      "Attendance",         "Attendance tracking",                    "clock",       5),
    ("LEAVES",          "Leaves",             "Leave requests and approvals",           "calendar",    6),
    ("PERFORMANCE",     "Performance",        "Reviews and KPIs",                       "bar-chart-2", 7),
    ("RECRUITMENT",     "Recruitment",        "Job postings and candidate pipeline",    "briefcase",   8),
    ("REPORTS",         "Reports",            "Analytics and exports",                  "pie-chart",   9),
    ("USER_MANAGEMENT", "User Management",    "Manage portal user accounts",           "user-check", 10),
    ("ROLE_MANAGEMENT", "Role Management",    "Roles and permission matrix",           "shield",     11),
]

PERM_MATRIX = {
    "super_admin": {m[0]: (True, True, True, True) for m in MODULES},
    "hr_manager": {
        "DASHBOARD":       (True,  False, False, False),
        "EMPLOYEES":       (True,  True,  True,  False),
        "DEPARTMENTS":     (True,  True,  True,  False),
        "PAYROLL":         (True,  True,  True,  False),
        "ATTENDANCE":      (True,  True,  True,  False),
        "LEAVES":          (True,  True,  True,  True),
        "PERFORMANCE":     (True,  True,  True,  False),
        "RECRUITMENT":     (True,  True,  True,  True),
        "REPORTS":         (True,  False, False, False),
        "USER_MANAGEMENT": (True,  True,  True,  False),
        "ROLE_MANAGEMENT": (True,  False, False, False),
    },
    "hr_executive": {
        "DASHBOARD":   (True,  False, False, False),
        "EMPLOYEES":   (True,  True,  True,  False),
        "DEPARTMENTS": (True,  False, False, False),
        "ATTENDANCE":  (True,  True,  False, False),
        "LEAVES":      (True,  True,  True,  False),
        "RECRUITMENT": (True,  True,  False, False),
        "REPORTS":     (True,  False, False, False),
    },
    "manager": {
        "DASHBOARD":   (True,  False, False, False),
        "EMPLOYEES":   (True,  False, False, False),
        "DEPARTMENTS": (True,  False, False, False),
        "ATTENDANCE":  (True,  True,  False, False),
        "LEAVES":      (True,  False, True,  False),
        "PERFORMANCE": (True,  True,  True,  False),
        "REPORTS":     (True,  False, False, False),
    },
    "employee": {
        "DASHBOARD":  (True, False, False, False),
        "EMPLOYEES":  (True, False, False, False),
        "ATTENDANCE": (True, True,  False, False),
        "LEAVES":     (True, True,  False, False),
    },
}

ROLES = [
    ("super_admin",  "Super Admin",  "Full access to all modules", True),
    ("hr_manager",   "HR Manager",   "Manages HR operations",      True),
    ("hr_executive", "HR Executive", "Day-to-day HR tasks",        True),
    ("manager",      "Manager",      "Team lead access",           True),
    ("employee",     "Employee",     "Self-service access",        True),
]

DEPARTMENTS = [
    ("Engineering",        "Designs, builds, and maintains software systems."),
    ("Marketing",          "Brand, campaigns, and market growth."),
    ("Human Resources",    "Talent acquisition, culture, and people operations."),
    ("Finance",            "Budgeting, accounting, and financial reporting."),
    ("Sales",              "Revenue growth and client relationships."),
    ("Product Management", "Product strategy, roadmap, and execution."),
    ("Design",             "User experience and visual design."),
]

SKILLS = [
    "Python","Flask","Django","JavaScript","React","Node.js",
    "PostgreSQL","MySQL","MongoDB","Docker","Kubernetes","AWS",
    "Linux","Git","CI/CD","REST API","GraphQL",
    "Figma","Adobe XD","Illustrator","Photoshop",
    "SEO","Google Ads","Content Marketing","Social Media",
    "Excel","Power BI","Tableau","Financial Modelling",
    "Salesforce","CRM","Negotiation","B2B Sales",
    "JIRA","Agile","Scrum","Product Analytics",
    "Recruitment","Onboarding","Payroll","Labor Law",
    "Java","Go","Terraform","Ansible",
]

DEMO_USERS = [
    ("admin@acmecorp.io",     "Admin@123", "super_admin",  "Admin User"),
    ("hrmanager@acmecorp.io", "Admin@123", "hr_manager",   "Priya Sharma"),
    ("manager@acmecorp.io",   "Admin@123", "manager",      "Arjun Mehta"),
    ("employee@acmecorp.io",  "Admin@123", "employee",     "Demo Employee"),
]

EMPLOYEES = [
    ("EMP001","Arjun Mehta","arjun.mehta@acmecorp.io","+91-9810001001","1978-04-15","Engineering","Chief Technology Officer","Full-Time","2015-03-01","Active",None,"Bangalore",5200000,["Python","AWS","Docker","Kubernetes","Agile","Git"]),
    ("EMP002","Priya Sharma","priya.sharma@acmecorp.io","+91-9810002002","1980-07-22","Human Resources","HR Director","Full-Time","2014-06-15","Active",None,"Mumbai",4800000,["Recruitment","Onboarding","Payroll","Labor Law"]),
    ("EMP003","Rahul Kapoor","rahul.kapoor@acmecorp.io","+91-9810003003","1977-11-30","Finance","Finance Director","Full-Time","2013-01-10","Active",None,"Delhi",4900000,["Financial Modelling","Excel","Power BI","Tableau"]),
    ("EMP004","Sneha Patel","sneha.patel@acmecorp.io","+91-9810004004","1982-02-14","Sales","Sales Director","Full-Time","2016-05-20","Active",None,"Hyderabad",4700000,["Salesforce","B2B Sales","Negotiation","CRM"]),
    ("EMP005","Vikram Singh","vikram.singh@acmecorp.io","+91-9810005005","1979-09-05","Marketing","Marketing Director","Full-Time","2015-08-01","Active",None,"Pune",4600000,["SEO","Google Ads","Content Marketing","Social Media"]),
    ("EMP006","Ananya Nair","ananya.nair@acmecorp.io","+91-9810006006","1985-12-03","Product Management","VP of Product","Full-Time","2017-02-15","Active","EMP001","Bangalore",3800000,["JIRA","Agile","Scrum","Product Analytics","REST API"]),
    ("EMP007","Rohan Joshi","rohan.joshi@acmecorp.io","+91-9810007007","1988-06-18","Engineering","Senior Software Engineer","Full-Time","2018-07-01","Active","EMP001","Bangalore",2600000,["Python","Flask","PostgreSQL","Docker","Git","REST API"]),
    ("EMP008","Deepika Reddy","deepika.reddy@acmecorp.io","+91-9810008008","1991-03-25","Engineering","Software Engineer","Full-Time","2020-01-06","Active","EMP007","Bangalore",1800000,["JavaScript","React","Node.js","MongoDB","Git"]),
    ("EMP009","Amit Kumar","amit.kumar@acmecorp.io","+91-9810009009","1989-08-11","Engineering","DevOps Engineer","Full-Time","2019-04-15","Active","EMP001","Bangalore",2200000,["Docker","Kubernetes","Terraform","Ansible","AWS","Linux","CI/CD"]),
    ("EMP010","Kavitha Iyer","kavitha.iyer@acmecorp.io","+91-9810010010","1992-01-07","Engineering","QA Engineer","Full-Time","2021-03-22","Active","EMP007","Chennai",1600000,["Python","Agile","JIRA","Git"]),
    ("EMP011","Sanjay Malhotra","sanjay.malhotra@acmecorp.io","+91-9810011011","1987-10-19","Design","UI/UX Designer","Full-Time","2018-11-05","Active","EMP006","Bangalore",2100000,["Figma","Adobe XD","Scrum","Product Analytics"]),
    ("EMP012","Meera Agarwal","meera.agarwal@acmecorp.io","+91-9810012012","1994-05-30","Design","Graphic Designer","Part-Time","2022-06-01","Active","EMP006","Remote",900000,["Illustrator","Photoshop","Figma"]),
    ("EMP013","Nikhil Bose","nikhil.bose@acmecorp.io","+91-9810013013","1986-04-02","Marketing","Digital Marketing Manager","Full-Time","2017-09-10","Active","EMP005","Pune",2000000,["SEO","Google Ads","Social Media","Content Marketing"]),
    ("EMP014","Pooja Verma","pooja.verma@acmecorp.io","+91-9810014014","1995-08-17","Marketing","Content Strategist","Full-Time","2022-01-10","On Leave","EMP013","Pune",1200000,["Content Marketing","SEO"]),
    ("EMP015","Rajesh Nair","rajesh.nair@acmecorp.io","+91-9810015015","1984-12-28","Sales","Senior Sales Executive","Full-Time","2016-11-14","Active","EMP004","Hyderabad",1900000,["Salesforce","CRM","Negotiation","B2B Sales"]),
    ("EMP016","Sunita Gupta","sunita.gupta@acmecorp.io","+91-9810016016","1993-07-09","Sales","Sales Executive","Full-Time","2021-08-23","Active","EMP015","Hyderabad",1100000,["CRM","B2B Sales","Salesforce"]),
    ("EMP017","Kiran Desai","kiran.desai@acmecorp.io","+91-9810017017","1990-02-21","Sales","Sales Executive","Contract","2023-03-01","Active","EMP015","Remote",960000,["Negotiation","CRM"]),
    ("EMP018","Aditya Choudhary","aditya.choudhary@acmecorp.io","+91-9810018018","1985-11-13","Finance","Senior Accountant","Full-Time","2015-07-07","Active","EMP003","Delhi",1700000,["Financial Modelling","Excel","Power BI"]),
    ("EMP019","Lakshmi Menon","lakshmi.menon@acmecorp.io","+91-9810019019","1993-03-16","Finance","Financial Analyst","Full-Time","2020-09-14","Active","EMP018","Delhi",1400000,["Tableau","Excel","Financial Modelling"]),
    ("EMP020","Manish Sharma","manish.sharma@acmecorp.io","+91-9810020020","1987-06-24","Human Resources","HR Manager","Full-Time","2017-04-03","Active","EMP002","Mumbai",1800000,["Recruitment","Onboarding","Labor Law","Payroll"]),
]


def seed():
    app = create_app()
    with app.app_context():

        print("▶  Dropping and recreating tables …")
        db.drop_all()
        db.create_all()

        print("▶  Seeding modules …")
        mod_map = {}
        for code, label, desc, icon, order in MODULES:
            m = Module(code=code, label=label, description=desc, icon=icon, sort_order=order)
            db.session.add(m)
            db.session.flush()
            mod_map[code] = m

        print("▶  Creating organisation: Acme Corp …")
        org = Organization(name="Acme Corp", domain="acmecorp.io", plan="enterprise")
        db.session.add(org)
        db.session.flush()

        print("▶  Creating roles and permission matrix …")
        role_map = {}
        for code, name, desc, is_sys in ROLES:
            role = Role(org_id=org.id, name=name, code=code, description=desc, is_system=is_sys)
            db.session.add(role)
            db.session.flush()
            role_map[code] = role
            for mcode, (v, cr, ed, dl) in (PERM_MATRIX.get(code) or {}).items():
                rp = RolePermission(
                    role_id=role.id, module_id=mod_map[mcode].id,
                    can_view=v, can_create=cr, can_edit=ed, can_delete=dl,
                )
                db.session.add(rp)

        print("▶  Creating demo users …")
        for email, pwd, rcode, fname in DEMO_USERS:
            u = User(org_id=org.id, role_id=role_map[rcode].id, email=email, full_name=fname)
            u.set_password(pwd)
            db.session.add(u)

        print("▶  Creating departments …")
        dept_map = {}
        for name, desc in DEPARTMENTS:
            dept = Department(org_id=org.id, name=name, description=desc)
            db.session.add(dept)
            db.session.flush()
            dept_map[name] = dept

        print("▶  Creating skills …")
        skill_map = {}
        for sk in SKILLS:
            s = Skill(name=sk)
            db.session.add(s)
            db.session.flush()
            skill_map[sk] = s

        print("▶  Inserting employees (pass 1 — no manager) …")
        emp_map = {}
        for row in EMPLOYEES:
            eid, name, email, phone, dob, dept, desig, etype, joining, status, _, loc, ctc, skill_names = row
            from datetime import date
            emp = Employee(
                org_id=org.id, employee_id=eid, full_name=name, email=email,
                phone=phone, date_of_birth=date.fromisoformat(dob),
                department_id=dept_map[dept].id, designation=desig,
                employment_type=etype, joining_date=date.fromisoformat(joining),
                employment_status=status, work_location=loc, annual_ctc=ctc,
            )
            emp.skills = [skill_map[sk] for sk in skill_names if sk in skill_map]
            db.session.add(emp)
            db.session.flush()
            emp_map[eid] = emp

        print("▶  Linking managers (pass 2) …")
        for row in EMPLOYEES:
            eid, mgr_eid = row[0], row[10]
            if mgr_eid:
                emp_map[eid].manager_id = emp_map[mgr_eid].id

        db.session.commit()

        print(f"\n✔  Seeding complete!")
        print(f"   Org      : Acme Corp  (id = {org.id})")
        print(f"   Modules  : {len(MODULES)}")
        print(f"   Roles    : {len(ROLES)}")
        print(f"   Employees: {len(EMPLOYEES)}")
        print()
        print("   Demo logins:")
        for email, pwd, rcode, _ in DEMO_USERS:
            print(f"     {email:<35} password: {pwd}  role: {rcode}")


if __name__ == "__main__":
    seed()
