# 🏗️ Predictive Analytics and Forecasting for Construction Projects

A Flask-based web application for managing construction projects, tasks, and progress. It includes role-based authentication, admin controls, and AI-powered predictions for project analytics such as estimated completion time, required workers, and material needs.

---

## 🚀 Features

### ✅ Core Features

- **User Authentication**
  - Register, Login, Logout
- **Role-Based Access**
  - Admin and Core User roles
- **Project Management**
  - Add, view, and delete projects
  - Inline task management for each project
- **Task Progress Tracking**
  - Add progress with percentage, delays, and notes
  - Automatic status updates
- **Admin Panel**
  - Promote/Demote admins
  - Block/Unblock users
  - Delete users
- **File Upload Support**
  - Import project tasks via `.xlsx` or `.csv` files
- **Analytics & Reporting**
  - View task progress in structured tables
  - (Optional) Downloadable reports

### 🤖 AI-Powered Predictions

Powered by pre-trained ML models:
- ⏳ Estimated days to completion
- 👷 Required additional workers
- 🧱 Required additional materials

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ManojReyya/Predictive-Analytics-and-Forecasting-for-Construction-Projects-.git
cd Predictive-Analytics-and-Forecasting-for-Construction-Projects-
```
### 2. Set Up Virtual Environment
```bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
Copy
Edit
pip install -r requirements.txt
```
5. Run the Application
```bash
Copy
Edit
python app.py
```
6. Open in Browser
Visit:
```bash
http://127.0.0.1:5000

```
cpp
Copy
Edit
http://127.0.0.1:5000
