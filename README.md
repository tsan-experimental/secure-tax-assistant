# Secure Tax Assistant

A full-stack, secure web application designed to help users organize, validate, and process tax information safely. This project is structured with a decoupled client-server architecture, utilizing a **FastAPI** backend for high-performance data processing and a **React (Vite)** frontend for an interactive user interface.

---

## 🏗️ Architecture & System Legs Explained

To understand how this application operates, it is divided into three primary functional layers ("legs"):

### 1. The System/Environment Layer (Host Machine / WSL2)
- **Purpose:** Provides the underlying operating system environment and core binaries required to execute code.
- **Components:**
  - **Ubuntu (WSL2):** Linux environment running on Windows for consistent Unix-based development.
  - **Python 3.12:** The programming language interpreter running the backend logic.
  - **Build Essentials & Python Dev:** Native C compilers (`build-essential`, `python3-dev`) required to compile performance-critical Python packages (like `pydantic-core`).
  - **Node.js & npm:** JavaScript runtime and package manager used to build and execute the frontend development environment.

### 2. The Backend Layer (FastAPI API Server)
- **Purpose:** Handles business logic, secure data validation, and API routing.
- **Components:**
  - **FastAPI:** A modern, high-speed Python web framework used to build RESTful endpoints.
  - **Uvicorn:** A lightning-fast ASGI server that hosts and runs the FastAPI application.
  - **Pydantic & Pydantic-Core:** Enforces strict data validation and type checking on all incoming and outgoing data models.
  - **Python-Dotenv:** Manages secure environment variables (like API keys or database URIs) via a local `.env` file.

### 3. The Frontend Layer (React & Vite Client)
- **Purpose:** Provides the visual user interface where users interact with the app.
- **Components:**
  - **Vite:** A next-generation, ultra-fast frontend build tool and development server.
  - **React:** A JavaScript library for building component-based user interfaces.
  - **npm (Node Package Manager):** Manages JavaScript libraries and UI packages.

---

## 📋 Comprehensive Dependency List

### System Prerequisites (OS Level)
Before running the app, your environment must have:
- Python 3.12 (`python3.12-venv`, `python3.12-dev`)
- Build Tools (`build-essential`, `python3-dev`)
- Node.js (v18+) & npm

### Backend Dependencies (`backend/requirements.txt`)
- `fastapi==0.115.0` - Web framework for building APIs
- `uvicorn==0.31.0` - ASGI server to run FastAPI
- `pydantic==2.9.2` - Data validation library
- `pydantic-core==2.23.4` - Compiled core validator for Pydantic
- `python-dotenv==1.0.1` - Environment variable loader
- `anyio`, `click`, `h11`, `idna`, `starlette`, `typing_extensions` - Underlying routing and utility packages

### Frontend Dependencies (`frontend/package.json`)
- `react` & `react-dom` - Core UI rendering engine
- `vite` - Development bundler and local server

---

## 🚀 Step-by-Step Installation Guide

### Step 1: Install System Prerequisites (WSL / Ubuntu)
```bash
sudo apt update
sudo apt install -y build-essential python3-dev software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev nodejs npm