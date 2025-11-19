# 🛒 ByteCart
### A Robust, Database-Driven E-Commerce Backend

> A modular, database-driven e-commerce backend demonstrating **ACID compliance** and **transactional integrity** using Django REST Framework and PostgreSQL.

---

## 📖 Overview
**ByteCart** is a backend-focused e-commerce platform developed as part of a Database Management Systems course project.  
It applies **core DBMS concepts** such as **ACID properties**, **normalization**, and **transactional consistency** in a practical setting.  
The platform handles **users**, **products**, and **orders** through modular Django applications, exposing a clean RESTful API.

---

## 🧩 Key Features
- 🔐 User authentication (JWT-ready)  
- 🛍️ Product and category management  
- 🧾 Order placement with ACID transactions  
- 💾 PostgreSQL database integration  
- 🧱 Normalized schema derived from an ERD  
- ⚙️ Modular Django apps: users, products, orders  
- 🧪 API testing using Postman  
- 🚀 CI-ready with GitHub Actions  

---

## 🛠️ Tech Stack
| Category | Tools/Frameworks |
|-----------|------------------|
| **Language** | Python 3.x |
| **Framework** | Django, Django REST Framework |
| **Database** | PostgreSQL |
| **Testing** | Postman |
| **Version Control** | Git + GitHub |
| **Workflow** | GitHub Actions (CI/CD) |

---

## 📁 Project Structure
```
bytecart/
  ├─ backend/
  │   ├─ manage.py
  │   ├─ bytecart/            # Django project settings
  │   ├─ apps/
  │   │   ├─ users/           # Authentication and profiles
  │   │   ├─ products/        # Product and category management
  │   │   └─ orders/          # Cart and transactional order handling
  │   └─ requirements.txt
  │
  ├─ .env.example              # Example environment variables
  ├─ .gitignore                # Ignore sensitive/unnecessary files
  ├─ README.md                 # Project overview and setup guide
  ├─ LICENSE                   # Open-source license file
  ├─ docs/                     # ERD diagrams and API documentation
  └─ .github/workflows/ci.yml  # Continuous integration workflow
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ACIDSynthesizers/ByteCart.git
cd ByteCart/backend
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Copy `.env.example` to `.env` and update it with your PostgreSQL credentials and Django secret key.

### 5️⃣ Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Start the Development Server
```bash
python manage.py runserver
```
Now visit 🌐 **http://127.0.0.1:8000/** to access the API.

---

## 🧪 Testing
API endpoints are tested via **Postman**.  
Collections will be added under `docs/api_tests/`.

---

## 📊 Database Design
The database schema follows a **normalized ERD** focusing on referential integrity and transactional safety.  
Diagrams and schema docs are included in the `/docs` directory.

---

## 👥 Team
**Team:** ACID Synthesizers  
**Course:** Database Management System (TCS – 503)

| Name | Role | Student ID |
|------|------|-------------|
| 👨‍💻 Pratyush Semwal | Team Lead | 23021760 |
| 👨‍💻 Ashmit Bisht | Developer | 230213633 |
| 👨‍💻 Harshit Negi | Developer | 23021720 |

---

## 📈 Project Phases
| Phase | Focus | Status |
|--------|--------|---------|
| ✅ Phase 1 | Proposal & ER Diagram | Completed |
| 🏗️ Phase 2 | Core Backend Setup & DB Integration | Completed |
| 🔜 Phase 3 | API Testing, Transaction Logic & Deployment | Completed |

---

## 🌐 Repository Links
- **GitHub Repo:** [https://github.com/lucifer-070/ByteCart/](#)  
- **Documentation:** `/docs`  
- **Postman Collection:** *(Coming Soon)*  

---

⭐ *Developed with passion by Team ACID Synthesizers — bridging theory and real-world DBMS applications.*
