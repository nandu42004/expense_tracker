import { useState, useEffect } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000/api";

function App() {
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({ category_id: "", amount: "", date: "", note: "" });
  const [report, setReport] = useState(null);
  const [yearMonth, setYearMonth] = useState({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
  });

  useEffect(() => {
    fetch(`${API}/users`).then(r => r.json()).then(setUsers).catch(console.error);
    fetch(`${API}/categories`).then(r => r.json()).then(setCategories).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedUser) {
      fetch(`${API}/expenses?user_id=${selectedUser}`)
        .then(r => r.json())
        .then(setExpenses)
        .catch(console.error);
    } else {
      setExpenses([]);
    }
  }, [selectedUser]);

  const createExpense = async (e) => {
    e.preventDefault();
    if (!selectedUser) {
      alert("Select a user");
      return;
    }
    const payload = {
      user_id: Number(selectedUser),
      category_id: Number(form.category_id),
      amount: form.amount,
      date: form.date,
      note: form.note,
    };
    const res = await fetch(`${API}/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      setForm({ category_id: "", amount: "", date: "", note: "" });
      fetch(`${API}/expenses?user_id=${selectedUser}`)
        .then(r => r.json())
        .then(setExpenses);
    } else {
      const err = await res.json();
      alert("Error: " + (err.detail || JSON.stringify(err)));
    }
  };

  const fetchReport = async () => {
    if (!selectedUser) {
      alert("Select a user");
      return;
    }
    const r = await fetch(
      `${API}/reports/monthly_summary?year=${yearMonth.year}&month=${yearMonth.month}&user_id=${selectedUser}`
    );
    if (r.ok) {
      const data = await r.json();
      setReport(data);
    } else {
      alert("Failed to fetch report");
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", fontFamily: "Arial, sans-serif" }}>
      <h1>Smart Expense Tracker (PoC)</h1>

      <div style={{ marginBottom: 20 }}>
        <label>Current user: </label>
        <select value={selectedUser || ""} onChange={(e) => setSelectedUser(e.target.value)}>
          <option value="">-- select user --</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name} ({u.email})
            </option>
          ))}
        </select>
      </div>

      <section style={{ border: "1px solid #ddd", padding: 12, marginBottom: 20 }}>
        <h3>Add Expense</h3>
        <form onSubmit={createExpense}>
          <div>
            <label>Category: </label>
            <select
              required
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            >
              <option value="">--choose--</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Amount: </label>
            <input
              required
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              placeholder="e.g., 99.50"
            />
          </div>
          <div>
            <label>Date: </label>
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
            />
          </div>
          <div>
            <label>Note: </label>
            <input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
          </div>
          <button type="submit">Add</button>
        </form>
      </section>

      <section style={{ border: "1px solid #eee", padding: 12, marginBottom: 20 }}>
        <h3>Expenses for selected user</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((exp) => (
              <tr key={exp.id}>
                <td>{exp.date}</td>
                <td>{categories.find((c) => c.id === exp.category_id)?.name || exp.category_id}</td>
                <td>{exp.amount}</td>
                <td>{exp.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h3>Monthly Report</h3>
        <div>
          <label>Year: </label>
          <input
            type="number"
            value={yearMonth.year}
            onChange={(e) => setYearMonth({ ...yearMonth, year: e.target.value })}
          />
          <label> Month: </label>
          <input
            type="number"
            value={yearMonth.month}
            onChange={(e) => setYearMonth({ ...yearMonth, month: e.target.value })}
          />
          <button onClick={fetchReport}>Get Report</button>
        </div>

        {report && (
          <div style={{ marginTop: 12 }}>
            <p>
              <strong>Total:</strong> {report.total_expenses}
            </p>
            <ul>
              {report.expenses_by_category.map((c, i) => (
                <li key={i}>
                  {c.category_name}: {c.total_amount}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
