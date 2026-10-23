SalesPro Sales Forecasting System - Updated Project

Included updates:
- Modern professional blue-and-white dashboard styling.
- Separate Admin and User navigation/management views.
- Admin user-management controls and role-based API protections from the existing project.
- Forecasting charts, reports/analytics, products, sales, customers, and settings pages preserved from the existing project.
- Forgot Password page now has an Admin/User account-type dropdown above the reset form.
- Password reset checks that the email belongs to the selected account type.

Run backend (Windows PowerShell):
1. Open a terminal in the project folder.
2. cd backend
3. python -m pip install -r requirements.txt
4. python create_admin.py   (creates/resets the local admin account)
5. python app.py

The included create_admin.py currently sets the local administrator credentials to:
Email: admin@gmail.com
Password: admin123
Change these values in backend/create_admin.py before running it if you prefer different credentials.

Run frontend in a second terminal:
1. cd frontend
2. npm install
3. npm run dev
4. Open the localhost URL printed by Vite in your browser.

The frontend defaults to the Flask API at http://127.0.0.1:5000/api. If you use a different API address, set VITE_API_URL in the frontend environment.

Important:
- This is a development project. Change the Flask secret key and admin credentials before deployment.
- Password reset is a direct reset form for this local project, not an email verification flow. Do not expose it publicly without adding secure identity verification.
- The frontend dependency installation/build could not be completed in this environment because npm installation timed out. Backend Python files passed syntax compilation.

Customer ID form update: Customer Management now accepts an optional Customer ID/code (for example CUS001). Existing records without a custom code continue to display their database ID as C{id}. The backend database initialization adds the customer_code column without deleting existing customer records.
