# Warehouse Management System
## Introduction
This Warehouse Management System is a Python Flask application designed to streamline inventory management processes for businesses. It offers comprehensive functionalities tailored to different user roles, including admins, managers, and employees.

## Features
- User Roles: Three distinct roles are available: Admin, Manager, and Employee.
- Admin: Manages user accounts, including adding, modifying, and deleting users. No access to warehouse functionalities.
- Manager: Manages warehouses, including adding, modifying, and deleting them. Can view warehouse details, inventory, and stock levels. Can order or deliver products for warehouses and add new products to the database for ordering.
- Employee: Similar functionalities as the manager but without the ability to manage warehouses. Can view the current inventory of a warehouse, order or deliver products, and view warehouse details. Cannot add, modify, or delete warehouses or products.  <br>
Additional Features <br>
- Flash Messages: Confirmation messages are displayed after each action.
- Confirmation Modals: Modal dialogs prompt for confirmation before deleting records.
- Data Management: Tables support data search, column sorting, pagination, and data export to PDF, CSV, Excel formats, and copying to the clipboard.
## Technologies Used
- Python Flask/Jinja: Backend web framework for developing the application.
- HTML/CSS/JavaScript: Frontend technologies for user interface development.
- MySQL: Supported database options for data storage.
