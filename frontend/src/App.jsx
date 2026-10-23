import { useEffect, useState } from "react";
import { FileText, Settings } from "lucide-react";

import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  BarChart3,
  LogIn,
  UserPlus,
  User,
  ArrowLeft,
  TrendingUp,
  Package,
  ShoppingCart,
  Users,
  LogOut,
} from "lucide-react";

import "./app.css";

function PowerBIStyleCharts({ sales = [], money }) {
  const rows = sales.map((sale, index) => ({
    label: sale.date || `Sale ${index + 1}`,
    value: Number(sale.amount) || 0,
  })).slice(-8);
  const history = rows.length ? rows : [
    { label: "Jan", value: 42000 }, { label: "Feb", value: 51000 },
    { label: "Mar", value: 47000 }, { label: "Apr", value: 63000 },
    { label: "May", value: 59000 }, { label: "Jun", value: 74000 },
  ];
  const maxValue = Math.max(...history.map((x) => x.value), 1);
  const total = history.reduce((sum, x) => sum + x.value, 0);
  const average = total / history.length;
  const forecast = Array.from({ length: 4 }, (_, i) => ({
    label: `P${i + 1}`, value: Math.round(average * (1 + (i + 1) * 0.08)),
  }));
  const points = history.map((x, i) => `${24 + i * (252 / Math.max(history.length - 1, 1))},${128 - (x.value / maxValue) * 100}`).join(" ");
  return <div className="pbi-dashboard">
    <div className="pbi-heading"><div><span className="pbi-kicker">POWER BI-STYLE INSIGHTS</span><h3>Sales performance overview</h3><p>Interactive-ready visual summary based on available sales records</p></div><span className="pbi-live-dot">● Live workspace data</span></div>
    <div className="pbi-kpis"><article><span>Revenue in chart</span><strong>{money(total)}</strong><small>Across {history.length} periods</small></article><article><span>Average sale</span><strong>{money(average)}</strong><small>Average value</small></article><article><span>Forecast next period</span><strong>{money(forecast[0].value)}</strong><small>Illustrative +8% trend</small></article></div>
    <div className="pbi-chart-grid"><section className="salespro-card pbi-chart-card"><div className="pbi-chart-title"><div><h4>Sales by period</h4><p>Revenue comparison</p></div><span className="pbi-chart-tag">BAR CHART</span></div><div className="pbi-bars">{history.map((x, i) => <div className="pbi-bar-column" key={`${x.label}-${i}`} title={`${x.label}: ${money(x.value)}`}><strong>{money(x.value)}</strong><div className="pbi-bar-track"><div className="pbi-bar" style={{ height: `${Math.max(5, x.value / maxValue * 100)}%` }} /></div><span>{x.label}</span></div>)}</div></section>
    <section className="salespro-card pbi-chart-card"><div className="pbi-chart-title"><div><h4>Sales trend</h4><p>Historical trend line</p></div><span className="pbi-chart-tag">LINE CHART</span></div><svg className="pbi-line-chart" viewBox="0 0 300 155" role="img" aria-label="Sales trend line chart"><line x1="20" y1="28" x2="280" y2="28"/><line x1="20" y1="70" x2="280" y2="70"/><line x1="20" y1="112" x2="280" y2="112"/><polyline points={points}/>{history.map((x, i) => <circle key={i} cx={24 + i * (252 / Math.max(history.length - 1, 1))} cy={128 - (x.value / maxValue) * 100} r="3.5"/> )}</svg><div className="pbi-chart-foot"><span>Lowest: {money(Math.min(...history.map(x => x.value)))}</span><span>Peak: {money(maxValue)}</span></div></section>
    <section className="salespro-card pbi-chart-card pbi-forecast-chart"><div className="pbi-chart-title"><div><h4>Forecast projection</h4><p>Illustrative trend based on average sales</p></div><span className="pbi-chart-tag">FORECAST</span></div><div className="pbi-forecast-row">{forecast.map((x) => <div key={x.label}><span>{x.label}</span><div className="pbi-forecast-track"><div style={{ width: `${Math.min(100, x.value / Math.max(...forecast.map(y => y.value)) * 100)}%` }} /></div><strong>{money(x.value)}</strong></div>)}</div><p className="muted pbi-disclaimer">Forecast is a simple illustrative projection, not an external Power BI connection or a trained predictive model.</p></section></div>
  </div>;
}

function App() {
  // ==========================================
  // SPLASH SCREEN
  // ==========================================

  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  // ==========================================
  // PAGE STATE
  // ==========================================

  const [page, setPage] = useState("login");

  // ==========================================
  // LOGIN STATE
  // ==========================================

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");

  // ==========================================
  // REGISTER STATE
  // ==========================================

  const [fullName, setFullName] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // ==========================================
  // FORGOT PASSWORD STATE
  // ==========================================

  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotRole, setForgotRole] = useState("user");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");

  // ==========================================
  // UI STATE
  // ==========================================

  const [showPassword, setShowPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // ==========================================
  // USER STATE
  // ==========================================

  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [workspacePage, setWorkspacePage] = useState("dashboard");
  const [theme, setTheme] = useState(() => localStorage.getItem("salesProTheme") || "light");
  const changeTheme = (nextTheme) => { setTheme(nextTheme); localStorage.setItem("salesProTheme", nextTheme); };
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [managedUsers, setManagedUsers] = useState([]);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("");
  const [newUserRole, setNewUserRole] = useState("user");
  const [sales, setSales] = useState([]);
  const [productName, setProductName] = useState("");
  const [productCode, setProductCode] = useState("");
  const [productPrice, setProductPrice] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerCode, setCustomerCode] = useState("");
  const [customerEmail, setCustomerEmail] = useState("");
  const [saleAmount, setSaleAmount] = useState("");
  const [saleProductId, setSaleProductId] = useState("");
  const [saleCustomerId, setSaleCustomerId] = useState("");
  const [currentSales, setCurrentSales] = useState("100000");
  const [growth, setGrowth] = useState("10");
  const [workspaceNotice, setWorkspaceNotice] = useState("");

  // Load persistent data from the Flask API for the signed-in account.
  useEffect(() => {
    if (!loggedIn || !user) return;
    const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";
    const headers = { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` };
    fetch(`${api}/customers`, { headers }).then(async r => { const d = await r.json(); if (r.ok) setCustomers((d.customers || []).map(c => ({ ...c, name: c.customer_name, email: c.email || "" }))); }).catch(() => {});
    if (user.role === "admin") fetch(`${api}/admin/users`, { headers }).then(async r => { const d = await r.json(); if (r.ok) setManagedUsers(d.users || []); }).catch(() => {});
  }, [loggedIn, user]);

  // ==========================================
  // GO TO LOGIN
  // ==========================================

  const goToLogin = () => {
    setPage("login");
    setError("");
    setSuccess("");
  };

  // ==========================================
  // GO TO REGISTER
  // ==========================================

  const goToRegister = () => {
    setPage("register");
    setError("");
    setSuccess("");
  };

  // ==========================================
  // GO TO FORGOT PASSWORD
  // ==========================================

  const goToForgotPassword = () => {
    setPage("forgot-password");
    setError("");
    setSuccess("");
  };

  // ==========================================
  // RESET PASSWORD
  // ==========================================

  const handleResetPassword = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!forgotEmail.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!newPassword) {
      setError("Please enter a new password.");
      return;
    }

    if (newPassword.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const API_URL =
        import.meta.env.VITE_API_URL ||
        "http://127.0.0.1:5000/api";

      const response = await fetch(
        `${API_URL}/reset-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: forgotEmail.trim(),
            role: forgotRole,
            new_password: newPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setSuccess(
          data.message ||
            "Password reset successfully. Please login."
        );

        setForgotEmail("");
        setNewPassword("");
        setConfirmNewPassword("");

        setTimeout(() => {
          goToLogin();
        }, 1500);
      } else {
        setError(
          data.message ||
            "Unable to reset password."
        );
      }
    } catch (error) {
      console.error("Reset password error:", error);
      setError(
        "Cannot connect to backend. Make sure Flask is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // LOGIN
  // ==========================================

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    if (!role) {
      setError("Please select Admin or User.");
      return;
    }

    try {
      setLoading(true);

      const API_URL =
        import.meta.env.VITE_API_URL ||
        "http://127.0.0.1:5000/api";

      const response = await fetch(
        `${API_URL}/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            password,
            role,
          }),
        }
      );

      const data = await response.json();

      if (response.ok && data.user) {
        if (data.user.role !== role) {
          setError(`This account is registered as ${data.user.role}. Please select ${data.user.role}.`);
          return;
        }

        setUser(data.user);
        setLoggedIn(true);
        setPage("dashboard");

        localStorage.setItem(
          "salesProUser",
          JSON.stringify(data.user)
        );

        if (data.token) {
          localStorage.setItem("salesProToken", data.token);
        }
      } else {
        setError(
          data.message || "Invalid email or password."
        );
      }
    } catch (error) {
      console.error("Login error:", error);

      setError(
        "Cannot connect to backend. Make sure Flask is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // REGISTER
  // ==========================================

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!fullName.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (!registerEmail.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!registerPassword) {
      setError("Please enter a password.");
      return;
    }

    if (!confirmPassword) {
      setError("Please confirm your password.");
      return;
    }

    if (registerPassword.length < 6) {
      setError(
        "Password must contain at least 6 characters."
      );
      return;
    }

    if (registerPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const API_URL =
        import.meta.env.VITE_API_URL ||
        "http://127.0.0.1:5000/api";

      const response = await fetch(
        `${API_URL}/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: fullName.trim(),
            email: registerEmail.trim(),
            password: registerPassword,
          }),
        }
      );

      const data = await response.json();

      if (response.ok && data.message) {
        setSuccess(
          "Registration successful! Redirecting to login..."
        );

        setFullName("");
        setRegisterEmail("");
        setRegisterPassword("");
        setConfirmPassword("");

        setTimeout(() => {
          setPage("login");
          setSuccess("");
        }, 1500);
      } else {
        setError(
          data.message || "Registration failed."
        );
      }
    } catch (error) {
      console.error("Registration error:", error);

      setError(
        "Cannot connect to backend. Make sure Flask is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = () => {
    localStorage.removeItem("salesProUser");
    localStorage.removeItem("salesProToken");

    setUser(null);
    setLoggedIn(false);

    setEmail("");
    setPassword("");
    setRole("");

    goToLogin();
  };

  // ==========================================
  // SPLASH SCREEN
  // ==========================================

  if (showSplash) {
    return (
      <div className="splash-screen">

        <div className="splash-content">

          {/* LOGO */}

          <div className="splash-logo">
            <div className="splash-logo-box">
              <BarChart3 size={42} />
            </div>
          </div>

          {/* PROJECT NAME */}

          <h1 className="splash-title">
            SalesPro
          </h1>

          <p className="splash-subtitle">
            Sales Forecasting & Management System
          </p>

          {/* LOADING */}

          <div className="splash-loader">

            <div className="splash-loader-track">
              <div className="splash-loader-progress"></div>
            </div>

            <p>
              Loading SalesPro...
            </p>

          </div>

          {/* FEATURES */}

          <div className="splash-features">

            <div className="splash-feature">

              <div className="splash-feature-icon">
                <BarChart3 size={22} />
              </div>

              <div>
                <h3>Sales Analytics</h3>
                <p>
                  Analyze your business performance
                </p>
              </div>

            </div>

            <div className="splash-feature">

              <div className="splash-feature-icon">
                <TrendingUp size={22} />
              </div>

              <div>
                <h3>Sales Forecasting</h3>
                <p>
                  Predict future sales trends
                </p>
              </div>

            </div>

            <div className="splash-feature">

              <div className="splash-feature-icon">
                <Package size={22} />
              </div>

              <div>
                <h3>Business Reports</h3>
                <p>
                  Generate detailed reports
                </p>
              </div>

            </div>

          </div>

          <div className="splash-footer">
            © 2026 SalesPro. All rights reserved.
          </div>

        </div>

      </div>
    );
  }

  // ==========================================
  // SALESPRO WORKSPACE
  // ==========================================
  if (loggedIn) {
    const isAdmin = user?.role === "admin";
    const userPages = [
      { id: "dashboard", label: "Dashboard", icon: <BarChart3 size={19} /> },
      { id: "sales", label: "My Sales", icon: <ShoppingCart size={19} /> },
      { id: "customers", label: "Customers", icon: <Users size={19} /> },
      { id: "forecast", label: "Forecast", icon: <TrendingUp size={19} /> },
      { id: "products", label: "Products", icon: <Package size={19} /> },
      { id: "analytics", label: "My Analytics", icon: <BarChart3 size={19} /> },
      { id: "reports", label: "Reports", icon: <FileText size={19} /> },
      { id: "settings", label: "Settings", icon: <Settings size={19} /> },
      { id: "datacenter", label: "Data Center", icon: <Lock size={19} /> },
    ];
    const adminPages = [
      { id: "dashboard", label: "Admin Dashboard", icon: <BarChart3 size={19} /> },
      { id: "users", label: "User Management", icon: <Users size={19} /> },
      { id: "sales", label: "All Sales", icon: <ShoppingCart size={19} /> },
      { id: "customers", label: "Customers", icon: <Users size={19} /> },
      { id: "products", label: "Products", icon: <Package size={19} /> },
      { id: "analytics", label: "Reports & Analytics", icon: <TrendingUp size={19} /> },
      { id: "reports", label: "Reports", icon: <FileText size={19} /> },
      { id: "settings", label: "Settings", icon: <Settings size={19} /> },
      { id: "datacenter", label: "Data Center", icon: <Lock size={19} /> },
    ];
    const workspacePages = isAdmin ? adminPages : userPages;
    if (!workspacePages.some((item) => item.id === workspacePage)) setWorkspacePage("dashboard");
    const money = (value) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value) || 0);
    const addLocalItem = (setter, item, message) => { setter((items) => [...items, item]); setWorkspaceNotice(message); };
    const title = workspacePages.find((item) => item.id === workspacePage)?.label || "Dashboard";
    const totalSales = sales.reduce((sum, item) => sum + Number(item.amount || 0), 0);
    const forecastTotal = (Number(currentSales) || 0) * (1 + (Number(growth) || 0) / 100);

    return (
      <div className={`salespro-layout ${theme === "dark" ? "salespro-dark-theme" : "salespro-light-theme"}`}>
        <aside className="salespro-sidebar">
          <div className="salespro-brand"><h2>SalesPro</h2><span>{isAdmin ? "Administrator Portal" : "User Workspace"}</span></div>
          <nav className="salespro-nav">
            {workspacePages.map((item) => <button key={item.id} className={`salespro-nav-item ${workspacePage === item.id ? "active" : ""}`} onClick={() => { setWorkspacePage(item.id); setWorkspaceNotice(""); }}>{item.icon}<span>{item.label}</span></button>)}
          </nav>
          <button className="salespro-nav-item salespro-logout" onClick={handleLogout}><LogOut size={19}/><span>Log out</span></button>
        </aside>
        <main className="salespro-main">
          <header className="salespro-header"><div><h1>{title}</h1><p>{isAdmin ? "System administration and business overview" : "Manage your sales and forecasts"}</p></div><div className="salespro-user"><span>♟</span>{user?.full_name || user?.name || "User"}<small className={`role-pill ${isAdmin ? "admin-pill" : "user-pill"}`}>{isAdmin ? "ADMIN" : "USER"}</small></div></header>
          {workspaceNotice && <div className="salespro-notice">{workspaceNotice}</div>}
          {workspacePage === "users" && isAdmin && <><h2 className="salespro-section-title">User Management</h2><form className="salespro-card salespro-form" onSubmit={async (e) => { e.preventDefault(); const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/admin/users`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` }, body: JSON.stringify({ name: newUserName, email: newUserEmail, password: newUserPassword, role: newUserRole }) }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Could not create user"); setWorkspaceNotice("User account created successfully."); setNewUserName(""); setNewUserEmail(""); setNewUserPassword(""); const rr = await fetch(`${api}/admin/users`, { headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const rd = await rr.json(); if (rr.ok) setManagedUsers(rd.users || []); } catch (err) { setWorkspaceNotice(err.message || "Could not connect to backend."); } }}><input placeholder="Full name" value={newUserName} onChange={e => setNewUserName(e.target.value)} required/><input type="email" placeholder="User email" value={newUserEmail} onChange={e => setNewUserEmail(e.target.value)} required/><input type="password" placeholder="Temporary password" value={newUserPassword} onChange={e => setNewUserPassword(e.target.value)} required/><select value={newUserRole} onChange={e => setNewUserRole(e.target.value)}><option value="user">User</option><option value="admin">Admin</option></select><button className="salespro-button">Create User</button></form><section className="salespro-card salespro-list"><h3>Registered users ({managedUsers.length})</h3>{managedUsers.length === 0 ? <p className="muted">No users loaded. Check backend connection and admin login.</p> : <table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead><tbody>{managedUsers.map(u => <tr key={u.id}><td>{u.name}</td><td>{u.email}</td><td>{u.role}</td><td>{Number(u.active) ? "Active" : "Inactive"}</td><td><button type="button" className="salespro-button" onClick={async () => { const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/admin/users/${u.id}/toggle`, { method: "PUT", headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Action failed"); const rr = await fetch(`${api}/admin/users`, { headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const rd = await rr.json(); if (rr.ok) setManagedUsers(rd.users || []); setWorkspaceNotice(d.message || "User status updated."); } catch (err) { setWorkspaceNotice(err.message); } }}> {Number(u.active) ? "Deactivate" : "Activate"} </button> <button type="button" className="salespro-button" onClick={async () => { if (!window.confirm(`Delete user ${u.email}?`)) return; const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/admin/users/${u.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Delete failed"); setManagedUsers(items => items.filter(item => item.id !== u.id)); setWorkspaceNotice("User deleted."); } catch (err) { setWorkspaceNotice(err.message); } }}>Delete</button></td></tr>)}</tbody></table>}</section></>}
          {workspacePage === "dashboard" && <>
            <h2 className="salespro-section-title">{isAdmin ? "System Overview" : "Business Overview"}</h2>
            <section className="salespro-stat-grid">
              <article className="salespro-card"><p>Total Sales</p><h2>{money(totalSales || 125000)}</h2><span className="positive">+12.5% this month</span></article>
              <article className="salespro-card"><p>Customers</p><h2>{customers.length || 850}</h2><span className="positive">+8.2% this month</span></article>
              <article className="salespro-card"><p>Orders</p><h2>{sales.length || 320}</h2><span className="positive">+10.4% this month</span></article>
              <article className="salespro-card"><p>Growth</p><h2>18.6%</h2><span className="positive">+4.1% this month</span></article>
            </section>
            <section className="salespro-card salespro-welcome"><h3>{isAdmin ? "Welcome to the Admin Portal" : "Welcome to SalesPro"}</h3><p>{isAdmin ? "Monitor the platform, manage users, review sales, and access business reports." : "Manage your sales, customers, products, forecasts and analytics from your own workspace."}</p></section>
          </>}
          {workspacePage === "sales" && <><h2 className="salespro-section-title">Sales Management</h2><form className="salespro-card salespro-form salespro-sale-form" onSubmit={(e) => { e.preventDefault(); if (Number(saleAmount) <= 0) return setWorkspaceNotice("Enter a sale amount greater than zero."); const selectedProduct = products.find((p) => String(p.id) === String(saleProductId)); const selectedCustomer = customers.find((c) => String(c.id) === String(saleCustomerId)); addLocalItem(setSales, { id: Date.now(), productId: selectedProduct?.id || "", productName: selectedProduct?.name || selectedProduct?.product_name || "—", customerId: selectedCustomer?.id || "", customerName: selectedCustomer?.name || selectedCustomer?.customer_name || "—", amount: Number(saleAmount), date: new Date().toLocaleDateString("en-IN") }, "Sale recorded successfully."); setSaleAmount(""); setSaleProductId(""); setSaleCustomerId(""); }}><select value={saleProductId} onChange={(e) => setSaleProductId(e.target.value)} required><option value="">Select product</option>{products.map((p) => <option key={p.id} value={p.id}>{`${p.productCode || p.code || `P${p.id}`} — ${p.name || p.product_name}`}</option>)}</select><select value={saleCustomerId} onChange={(e) => setSaleCustomerId(e.target.value)} required><option value="">Select customer</option>{customers.map((c) => <option key={c.id} value={c.id}>{`${c.customer_code || `C${c.id}`} — ${c.name || c.customer_name}`}</option>)}</select><input type="number" min="1" step="0.01" placeholder="Sale amount (₹)" value={saleAmount} onChange={(e) => setSaleAmount(e.target.value)} required/><button className="salespro-button">Add Sale</button></form><section className="salespro-card salespro-list"><h3>Recorded Sales</h3>{sales.length === 0 ? <p className="muted">No sales added yet.</p> : <div className="salespro-table-wrap"><table><thead><tr><th>Date</th><th>Product ID</th><th>Product Name</th><th>Sales ID</th><th>Sales Name</th><th>Customer ID</th><th>Customer Name</th><th>Sale Amount</th></tr></thead><tbody>{sales.map((s) => <tr key={s.id}><td>{s.date}</td><td>{s.productId ? (products.find((p) => String(p.id) === String(s.productId))?.productCode || `P${s.productId}`) : "—"}</td><td>{s.productName || "—"}</td><td>{`S${s.id}`}</td><td>{user?.full_name || user?.name || "Current user"}</td><td>{s.customerId ? `C${s.customerId}` : "—"}</td><td>{s.customerName || "—"}</td><td>{money(s.amount)}</td></tr>)}</tbody></table></div>}</section></>}
          {workspacePage === "customers" && <><h2 className="salespro-section-title">{isAdmin ? "All Customer Records" : "My Customer Management"}</h2><form className="salespro-card salespro-form" onSubmit={async (e) => { e.preventDefault(); const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/customers`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` }, body: JSON.stringify({ customer_code: customerCode.trim(), customer_name: customerName.trim(), email: customerEmail.trim() }) }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Could not save customer"); const rr = await fetch(`${api}/customers`, { headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const rd = await rr.json(); if (rr.ok) setCustomers((rd.customers || []).map(c => ({ ...c, name: c.customer_name, email: c.email || "" }))); setCustomerName(""); setCustomerCode(""); setCustomerEmail(""); setWorkspaceNotice("Customer saved to database successfully."); } catch (err) { setWorkspaceNotice(err.message || "Could not connect to backend."); } }}><input placeholder="Customer ID (e.g. CUS001)" value={customerCode} onChange={(e) => setCustomerCode(e.target.value)} aria-label="Customer ID"/><input placeholder="Customer name" value={customerName} onChange={(e) => setCustomerName(e.target.value)} required/><input type="email" placeholder="Email address" value={customerEmail} onChange={(e) => setCustomerEmail(e.target.value)}/><button className="salespro-button">Add Customer</button></form><section className="salespro-card salespro-list"><h3>Customers ({customers.length})</h3>{customers.length === 0 ? <p className="muted">No customers found for this account.</p> : <table><thead><tr><th>Customer ID</th><th>Name</th><th>Email</th><th>{isAdmin ? "Owner" : "Actions"}</th><th>Manage</th></tr></thead><tbody>{customers.map((c) => <tr key={c.id}><td>{c.customer_code || `C${c.id}`}</td><td>{c.name}</td><td>{c.email}</td><td>{isAdmin ? (c.owner_name || "Admin") : "My record"}</td><td><button type="button" className="salespro-button" onClick={async () => { const code = window.prompt("Customer ID", c.customer_code || `C${c.id}`); if (code === null) return; const name = window.prompt("Customer name", c.name); if (name === null) return; const email = window.prompt("Customer email", c.email || ""); if (email === null) return; const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/customers/${c.id}`, { method: "PUT", headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` }, body: JSON.stringify({ customer_code: code, customer_name: name, email }) }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Update failed"); setCustomers(items => items.map(x => x.id === c.id ? { ...x, customer_code: code, name, customer_name: name, email } : x)); setWorkspaceNotice("Customer updated."); } catch (err) { setWorkspaceNotice(err.message); } }}>Edit</button> <button type="button" className="salespro-button" onClick={async () => { if (!window.confirm(`Delete customer ${c.name}?`)) return; const api = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api"; try { const r = await fetch(`${api}/customers/${c.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${localStorage.getItem("salesProToken") || ""}` } }); const d = await r.json(); if (!r.ok) throw new Error(d.message || "Delete failed"); setCustomers(items => items.filter(x => x.id !== c.id)); setWorkspaceNotice("Customer deleted."); } catch (err) { setWorkspaceNotice(err.message); } }}>Delete</button></td></tr>)}</tbody></table>}</section></>}
          {workspacePage === "products" && <><h2 className="salespro-section-title">Products</h2><form className="salespro-card salespro-form" onSubmit={(e) => { e.preventDefault(); const code = productCode.trim() || `P${Date.now().toString().slice(-6)}`; if (products.some((p) => String(p.productCode || p.code || "").toLowerCase() === code.toLowerCase())) return setWorkspaceNotice("That Product ID already exists. Please use a unique ID."); addLocalItem(setProducts, { id: Date.now(), productCode: code, name: productName.trim(), price: Number(productPrice) }, "Product added successfully."); setProductCode(""); setProductName(""); setProductPrice(""); }}><input placeholder="Product ID (e.g. PROD001)" value={productCode} onChange={(e) => setProductCode(e.target.value)} aria-label="Product ID"/><input placeholder="Product name" value={productName} onChange={(e) => setProductName(e.target.value)} required/><input type="number" min="0" step="0.01" placeholder="Price (₹)" value={productPrice} onChange={(e) => setProductPrice(e.target.value)} required/><button className="salespro-button">Add Product</button></form><section className="salespro-card salespro-list">{products.length === 0 ? <p className="muted">No products added yet.</p> : <><h3>Product List</h3><table><thead><tr><th>Product ID</th><th>Product</th><th>Price</th></tr></thead><tbody>{products.map((p) => <tr key={p.id}><td>{p.productCode || p.code || `P${p.id}`}</td><td>{p.name || p.product_name}</td><td>{money(p.price)}</td></tr>)}</tbody></table></>}</section></>}
          {workspacePage === "forecast" && <><h2 className="salespro-section-title">Sales Forecast & BI Charts</h2><section className="salespro-card salespro-forecast"><label>Current sales (₹)<input type="number" min="0" value={currentSales} onChange={(e) => setCurrentSales(e.target.value)}/></label><label>Expected growth (%)<input type="number" value={growth} onChange={(e) => setGrowth(e.target.value)}/></label><h3>Forecasted sales: {money(forecastTotal)}</h3><p className="muted">Calculated using current sales and expected growth.</p></section><PowerBIStyleCharts sales={sales} money={money}/></>}
          {workspacePage === "analytics" && <><h2 className="salespro-section-title">Sales Analytics</h2><PowerBIStyleCharts sales={sales} money={money}/><section className="salespro-stat-grid"><article className="salespro-card"><p>Recorded Revenue</p><h2>{money(totalSales)}</h2></article><article className="salespro-card"><p>Sales Entries</p><h2>{sales.length}</h2></article><article className="salespro-card"><p>Products</p><h2>{products.length}</h2></article><article className="salespro-card"><p>Customers</p><h2>{customers.length}</h2></article></section><section className="salespro-card salespro-list"><h3>Recent sales activity</h3>{sales.length ? sales.slice().reverse().map((s) => <p key={s.id}>{s.date} <strong>{money(s.amount)}</strong></p>) : <p className="muted">Add sales to start viewing your business analytics.</p>}</section></>}
          {workspacePage === "reports" && <><h2 className="salespro-section-title">Reports</h2><section className="salespro-stat-grid"><article className="salespro-card"><p>Total Revenue</p><h2>{money(totalSales)}</h2></article><article className="salespro-card"><p>Sales Records</p><h2>{sales.length}</h2></article><article className="salespro-card"><p>Customers</p><h2>{customers.length}</h2></article><article className="salespro-card"><p>Products</p><h2>{products.length}</h2></article></section><section className="salespro-card salespro-list"><div className="salespro-report-actions"><h3>Sales report</h3><button className="salespro-button" type="button" onClick={() => window.print()}>Print / Save PDF</button><button className="salespro-button" type="button" onClick={() => { const rows = [["Date","Amount (INR)"], ...sales.map(x => [x.date, x.amount])]; const csv = rows.map(row => row.map(v => `"${String(v ?? "").replace(/"/g, '""')}"`).join(",")).join("\n"); const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" }); const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = "salespro-report.csv"; a.click(); URL.revokeObjectURL(url); }}>Export CSV</button></div>{sales.length ? <div className="salespro-table-wrap"><table><thead><tr><th>Date</th><th>Product ID</th><th>Customer ID</th><th>Sales ID</th><th>Sales amount</th></tr></thead><tbody>{sales.map(s => <tr key={s.id}><td>{s.date}</td><td>{s.productId ? (products.find((p) => String(p.id) === String(s.productId))?.productCode || `P${s.productId}`) : "—"}</td><td>{s.customerId ? `C${s.customerId}` : "—"}</td><td>{`S${s.id}`}</td><td>{money(s.amount)}</td></tr>)}</tbody></table></div> : <p className="muted">No sales recorded yet. Add sales to populate this report.</p>}</section></>}
          {workspacePage === "settings" && <><h2 className="salespro-section-title">Settings</h2><section className="salespro-card salespro-profile-card"><div className="salespro-settings-card-heading"><div><span className="salespro-settings-eyebrow">ACCOUNT SETTINGS</span><h3>Profile</h3></div><span className={`salespro-settings-role ${isAdmin ? "is-admin" : "is-user"}`}>{isAdmin ? "ADMINISTRATOR" : "USER"}</span></div><div className="salespro-profile-grid"><div className="salespro-profile-field"><label htmlFor="profile-display-name">Display name</label><input id="profile-display-name" value={user?.full_name || user?.name || "User"} readOnly aria-readonly="true"/><small>Managed by your account</small></div><div className="salespro-profile-field"><label htmlFor="profile-email">Email address</label><input id="profile-email" type="email" value={user?.email || ""} readOnly aria-readonly="true"/><small>Your registered email</small></div><div className="salespro-profile-field"><label htmlFor="profile-role">Account role</label><input id="profile-role" value={isAdmin ? "Administrator" : "User"} readOnly aria-readonly="true"/><small>Role permissions are protected</small></div></div><p className="salespro-profile-help">Profile details are managed by your account. Contact an administrator if you need account changes.</p><div className="salespro-settings-actions"><button className="salespro-button" type="button" onClick={() => { const ok = window.confirm("Log out of SalesPro now?"); if (ok) handleLogout(); }}>Log out</button></div></section><section className="salespro-card salespro-list salespro-preferences"><h3>Workspace preferences</h3><p>Interface: Modern Professional Dashboard</p><div className="salespro-theme-setting"><label htmlFor="salespro-theme-select">Color theme</label><select id="salespro-theme-select" value={theme} onChange={(e) => changeTheme(e.target.value)}><option value="light">Light theme</option><option value="dark">Dark theme</option></select><span className="salespro-theme-preview">{theme === "dark" ? "Dark mode is active" : "Light mode is active"}</span></div><p>Data access: {isAdmin ? "Administrator access" : "Your own workspace data"}</p></section></>}
          {workspacePage === "datacenter" && <><h2 className="salespro-section-title">Data Center</h2><section className="salespro-stat-grid"><article className="salespro-card"><p>Sales records</p><h2>{sales.length}</h2></article><article className="salespro-card"><p>Customer records</p><h2>{customers.length}</h2></article><article className="salespro-card"><p>Product records</p><h2>{products.length}</h2></article></section><section className="salespro-card salespro-list"><h3>Stored data overview</h3><p>Sales: {sales.length} records</p><p>Customers: {customers.length} records</p><p>Products: {products.length} records</p><p className="muted">This page summarizes records created in this current workspace session.</p></section></>}
        </main>
      </div>
    );
  }

  // ==========================================
  // FORGOT PASSWORD PAGE
  // ==========================================

  if (page === "forgot-password") {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <button
            type="button"
            className="back-button"
            onClick={goToLogin}
          >
            <ArrowLeft size={18} />
            Back to Login
          </button>

          <div className="auth-icon">
            <Lock size={28} />
          </div>

          <h1>Forgot Password?</h1>

          <p className="auth-description">
            Reset your SalesPro account password.
          </p>

          <div className="form-group forgot-role-group">
            <label htmlFor="forgot-account-role">Account Type</label>
            <select
              id="forgot-account-role"
              className="role-select"
              value={forgotRole}
              onChange={(e) => setForgotRole(e.target.value)}
            >
              <option value="admin">Admin</option>
              <option value="user">User</option>
            </select>
            <small className="forgot-role-hint">Choose the account type before resetting your password.</small>
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          <form onSubmit={handleResetPassword}>
            <div className="form-group">
              <label>Email Address</label>

              <div className="input-wrapper">
                <User size={21} className="input-icon" />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={forgotEmail}
                  onChange={(e) =>
                    setForgotEmail(e.target.value)
                  }
                />
              </div>
            </div>

            <div className="form-group">
              <label>New Password</label>

              <div className="input-wrapper">
                <Lock size={21} className="input-icon" />

                <input
                  type="password"
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) =>
                    setNewPassword(e.target.value)
                  }
                />
              </div>
            </div>

            <div className="form-group">
              <label>Confirm New Password</label>

              <div className="input-wrapper">
                <Lock size={21} className="input-icon" />

                <input
                  type="password"
                  placeholder="Confirm new password"
                  value={confirmNewPassword}
                  onChange={(e) =>
                    setConfirmNewPassword(e.target.value)
                  }
                />
              </div>
            </div>

            <button
              type="submit"
              className="sign-in-button"
              disabled={loading}
            >
              <Lock size={21} />
              <span>
                {loading
                  ? "Resetting..."
                  : "Reset Password"}
              </span>
            </button>
          </form>
        </div>
      </div>
    );
  }

  // ==========================================
  // REGISTER PAGE
  // ==========================================

  if (page === "register") {
    return (
      <div className="auth-page">

        <div className="register-card">

          <div className="auth-logo">
            <BarChart3 size={30} />
          </div>

          <h1>
            Create Account
          </h1>

          <p className="auth-description">
            Create your Sales Forecasting System account.
          </p>

          <form onSubmit={handleRegister}>

            {/* FULL NAME */}

            <div className="form-group">

              <label>
                Full Name
              </label>

              <div className="input-wrapper">

                <User size={19} />

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(e) =>
                    setFullName(e.target.value)
                  }
                />

              </div>

            </div>

            {/* EMAIL */}

            <div className="form-group">

              <label>
                Email Address
              </label>

              <div className="input-wrapper">

                <Mail size={19} />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={registerEmail}
                  onChange={(e) =>
                    setRegisterEmail(e.target.value)
                  }
                />

              </div>

            </div>

            {/* PASSWORD */}

            <div className="form-group">

              <label>
                Password
              </label>

              <div className="input-wrapper">

                <Lock size={19} />

                <input
                  type={
                    showRegisterPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Create a password"
                  value={registerPassword}
                  onChange={(e) =>
                    setRegisterPassword(e.target.value)
                  }
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowRegisterPassword(
                      !showRegisterPassword
                    )
                  }
                >
                  {showRegisterPassword ? (
                    <EyeOff size={19} />
                  ) : (
                    <Eye size={19} />
                  )}
                </button>

              </div>

            </div>

            {/* CONFIRM PASSWORD */}

            <div className="form-group">

              <label>
                Confirm Password
              </label>

              <div className="input-wrapper">

                <Lock size={19} />

                <input
                  type="password"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) =>
                    setConfirmPassword(e.target.value)
                  }
                />

              </div>

            </div>

            {/* ERROR */}

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            {/* SUCCESS */}

            {success && (
              <div className="success-message">
                {success}
              </div>
            )}

            {/* BUTTON */}

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >

              <UserPlus size={19} />

              {loading
                ? "Creating Account..."
                : "Create Account"}

            </button>

          </form>

          {/* BACK */}

          <div className="register-section">

            <span>
              Already have an account?
            </span>

            <button
              type="button"
              onClick={goToLogin}
            >
              <ArrowLeft size={16} />
              Sign In
            </button>

          </div>

        </div>

      </div>
    );
  }

  // ==========================================
  // LOGIN PAGE
  // ==========================================

  return (
    <div className="login-page">

      {/* LEFT SIDE */}
      <div className="login-left">

        <div className="brand">
          <div className="brand-icon">
            <TrendingUp size={30} />
          </div>

          <div className="brand-text">
            <h2>SalesPro</h2>
            <span>Sales Forecasting System</span>
          </div>
        </div>

        <div className="welcome-content">
          <h1>
            Manage Your Sales
            <br />
            <span>Smarter.</span>
          </h1>

          <p>
            Track products, customers, sales and business performance in one powerful platform.
          </p>
        </div>

      </div>

      {/* RIGHT SIDE */}
      <div className="login-right">

        <div className="login-card">

          <h1>Welcome Back</h1>

          <p className="login-description">
            Sign in to access your dashboard.
          </p>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin}>

            {/* EMAIL */}
            <div className="form-group">
              <label>Email Address</label>

              <div className="input-wrapper">
                <User size={21} className="input-icon" />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            {/* PASSWORD */}
            <div className="form-group">
              <label>Password</label>

              <div className="input-wrapper">
                <Lock size={21} className="input-icon" />

                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />

                <button
                  type="button"
                  className="password-eye"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={21} /> : <Eye size={21} />}
                </button>
              </div>
            </div>

            {/* LOGIN AS */}
            <div className="form-group">
              <label>Login As</label>
              <select
                className="role-select"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
              </select>
            </div>

            {/* SIGN IN */}
            <button
              type="submit"
              className="sign-in-button"
              disabled={loading}
            >
              <LogIn size={21} />
              <span>{loading ? "Signing In..." : "Sign In"}</span>
            </button>

          </form>

          {/* FORGOT PASSWORD */}
          <div className="forgot-password-link">
            <button
              type="button"
              onClick={goToForgotPassword}
            >
              Forgot Password?
            </button>
          </div>

          {/* CREATE ACCOUNT */}
          <div className="create-account">
            <span>Don't have an account?</span>

            <button type="button" onClick={goToRegister}>
              Create Account
              <UserPlus size={17} />
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}

export default App;