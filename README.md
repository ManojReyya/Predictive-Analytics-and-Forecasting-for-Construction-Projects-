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
# 🤖 Machine Learning in This Project

This project uses machine learning models to enhance construction project forecasting and analytics. The goal is to predict:

- 🕒 Estimated days to project completion
- 👷 Additional workers required
- 🧱 Additional materials needed

## 🧠 ML Workflow

### 1. Dataset
The model is trained on historical construction project data with the following features:

- `work_progress`
- `worker_availability`
- `material_availability`
- `equipment_availability`
- `delays`
- `resource_shortage`
- `budget_overrun`

### 2. Models
We use **Random Forest Regressors** from `scikit-learn` to predict:

- `predicted_completion_days_left`
- `additional_workers_needed`
- `additional_materials_needed`

Each target is trained using a separate model for better accuracy.

### 3. Model Evaluation
We evaluate each model using:

- **MAE** (Mean Absolute Error)
- **MSE** (Mean Squared Error)

Example evaluation output:
```text
Completion Prediction - MAE: 42.93, MSE: 2419.52  
Workers Prediction - MAE: 4.97, MSE: 33.42  
Materials Prediction - MAE: 12.46, MSE: 212.12  
```
## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ManojReyya/Predictive-Analytics-and-Forecasting-for-Construction-Projects-.git
cd Predictive-Analytics-and-Forecasting-for-Construction-Projects-
```
### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
5. Run the Application
```bash
python app.py
```
6. Open in Browser
Visit:
```bash
http://127.0.0.1:5000
```

