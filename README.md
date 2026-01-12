Based on your current volume structure, it is clear that **Fundwarden** has matured into a sophisticated, multi-layered application. You’ve successfully separated your Python environment, Node.js assets (for Tailwind CSS), and a modular Flask core.

Here is the updated `README.md` that accurately reflects this architecture.

---

# Fundwarden: A Full-Stack Financial Management Solution

## Project Overview

**Fundwarden** is a professional-grade web application developed as the final project for Harvard University's CS50x 2025. It provides a secure, modular platform for financial tracking, emphasizing data integrity, modern UI/UX via Tailwind CSS, and a robust backend built on Flask and PostgreSQL.

The project structure reflects a "Production-First" mindset, utilizing an **Application Factory** pattern, isolated virtual environments, and automated asset compilation to ensure the software remains maintainable and scalable.

---

## Technical Architecture & Design Choices

### 1. The Application Factory & Modular Blueprints

The core of Fundwarden resides in the `app/` directory. Rather than a monolithic file, I implemented a modular architecture:

- **`app.py`**: Acts as the central hub containing the `create_app()` factory function. It initializes extensions (SQLAlchemy, Mail, Migrate) and dynamically registers blueprints.
- **Blueprints (`app/blueprints/`)**: The logic is split into `auth` (for identity management) and `core` (for financial logic). This separation ensures that as the project grows, developers can work on the dashboard without affecting the authentication flow.

### 2. Frontend Modernization: Tailwind CSS & Node.js

Unlike standard Flask projects that use raw CSS, Fundwarden integrates **Tailwind CSS** for a highly responsive and modern interface.

- **Asset Pipeline**: I utilized a `node_modules` ecosystem to handle Tailwind's compilation.
- **Source vs. Dist**: The directory structure separates `static/src` (raw Tailwind classes) from `static/dist` (minified, production-ready CSS), significantly improving the application's load times.

### 3. Database & Infrastructure Evolution

A significant portion of the development was dedicated to mastering the **Flask-Migrate (Alembic)** workflow for PostgreSQL.

- **Migration Integrity**: By moving the `migrations/` folder to the root directory, I ensured it exists outside the application logic, serving as a standalone version history of the database schema.
- **DevOps Automation**: I authored an `entrypoint.sh` script to automate `flask db upgrade` during deployment. This ensures that the production environment on Render is always synchronized with the local schema defined in `models.py`.

---

## File Structure & Descriptions

- **`app.py`**: The application's core factory. It configures the Flask instance and sets up the database and mail extensions.
- **`run.py`**: The entry point for the server; it calls the factory from `app.py`.
- **`app/blueprints/`**: Contains sub-packages for `auth` and `core` logic, keeping the codebase organized.
- **`app/templates/` & `app/static/**`: Houses the Jinja2 templates and compiled CSS.
- **`migrations/`**: The root-level directory for database versioning and schema history.
- **`node_modules/`**: Contains the dependencies for the Tailwind CSS build process.
- **`.fundwarden_venv/`**: An isolated virtual environment containing Python 3.14 and all necessary libraries (Flask, SQLAlchemy, Brevo SDK).
- **`Dockerfile` & `entrypoint.sh**`: The configuration for containerizing the app for reliable cloud deployment.

---

## Features & Implementation Details

### Security & Validation

- **Regex Refinement**: Re-engineered name validation to support multi-part names and initials while stripping all non-alphabetic symbols.
- **Authentication**: Implemented session-based authentication with password hashing via **Bcrypt** and protected routes to ensure user data privacy.

### Email Integration

- **Brevo Mail API**: After navigating port restrictions and provider limitations (SMTP/SendGrid), I implemented the **Brevo (formerly Sendinblue)** API for reliable transactional emails, ensuring "Forgot Password" functionality works consistently in a production environment.

---

## Lessons Learned & Future Roadmap

This project was a journey of technical resilience. Recovering from surgery while building a complex system taught me that:

1. **Architecture is Foundation**: Using the Factory Pattern early saved me from countless circular import bugs.
2. **Environment Isolation is Key**: Maintaining a clean `.fundwarden_venv` allowed me to experiment with the latest Python 3.14 features without breaking system-wide configurations.

**Future Goals**:
I plan to evolve Fundwarden into a full React/Django stack and eventually bridge this logic into **Robotics and Computer Vision** projects, applying the same rigorous architectural standards to hardware-software integration.

---

## How to Run Locally

1. **Clone**: `git clone https://github.com/Sonu64/Fundwarden`
2. **Activate Env**: `.\.fundwarden_venv\Scripts\activate`
3. **Install JS Deps**: `npm install` (for Tailwind compilation)
4. **Database**: `flask db upgrade`
5. **Run**: `python run.py`

---

**Next Step:** Your folder structure shows you are using **Python 3.14**. Since this is a very new/experimental version, would you like me to help you double-check your `Dockerfile` to ensure it uses the correct base image for this specific version on Render?
