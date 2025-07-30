Smart Inventory & Sales Management System
A full-stack, multi-user web application designed to help small businesses or individuals manage their product inventory and track sales efficiently. The system is built with a Python and Flask backend, a PostgreSQL database, and is deployed live on the cloud with Render.
https://smart-inventory-system-kmve.onrender.com
Key Features
Secure Multi-User Accounts: A robust registration and login system ensures that each user's data is completely private and accessible only to them.
Full CRUD Inventory Management: Users can easily Create, Read, Update, and Delete items from their inventory.
Automated Sales Tracking: Recording a sale automatically deducts the quantity from the available stock, ensuring data is always accurate.
Smart Low-Stock Alerts: The UI provides immediate visual feedback for items running low on stock, both in the navigation bar and highlighted directly in the inventory list.
Live Search & Filtering: The inventory page features a responsive search bar that filters results in real-time without needing a page reload.
Business Intelligence Dashboard: The main dashboard provides at-a-glance insights, including total inventory value, item counts, and a dynamic sales revenue chart for the last 7 days.
CSV Data Export: Users can export both their inventory and sales records to CSV files for offline analysis or record-keeping.
Production-Ready Deployment: The application is configured with a Gunicorn WSGI server and Flask-Migrate for seamless database schema management in a production environment.
Technology Stack
Category	Technology
Backend	Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Gunicorn
Frontend	HTML, CSS, JavaScript, Bootstrap 5, Chart.js
Database	PostgreSQL (Production), SQLite (Development)
Deployment	Render, Git, GitHub
## Screenshots

**Main Dashboard:**
![Dashboard Screenshot](./images/Screenshot%202025-07-30%20123301.png)

**Inventory Page (with Low-Stock Alert):**
![Inventory Screenshot](./images/Screenshot%202025-07-30%20123551.png)