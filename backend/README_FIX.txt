SalesPro repair

What was fixed:
- Kept frontend/src/App.jsx and frontend/src/app.css unchanged.
- Fixed backend database.py so it provides get_db(), which app.py imports.
- Migrates the existing sales_forecasting.db without deleting old data.
- Preserves incompatible old products/customers/sales tables as *_legacy and copies their data into the schema expected by app.py.
- Adds the missing users.name and users.active columns.
- Added backend/requirements.txt.

Run backend:
  cd backend
  py -m pip install -r requirements.txt
  py app.py

Test backend:
  http://127.0.0.1:5000/api/health

Run frontend:
  cd frontend
  npm install
  npm run dev

Important:
- Do not delete sales_forecasting.db.
- The repair does not intentionally change the frontend design.
- The old database tables are preserved as products_legacy, customers_legacy and sales_legacy after migration.
