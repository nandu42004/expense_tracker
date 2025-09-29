# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal, InvalidOperation
from typing import Optional, List
import sqlite3
from pathlib import Path
from datetime import date

HERE = Path(__file__).parent
DB_PATH = str(HERE / "db.sqlite")

app = FastAPI(title="Smart Expense Tracker (PoC)")

# allow your frontend dev server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ---- Pydantic models for request/response validation ----
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1)

class CategoryOut(BaseModel):
    id: int
    name: str

class ExpenseCreate(BaseModel):
    user_id: int
    category_id: int
    amount: str    # accept as string so decimals are precise
    date: Optional[str] = None  # 'YYYY-MM-DD'
    note: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: str
    date: str
    note: Optional[str]

# ---- Users ----
@app.post("/api/users", response_model=UserOut)
def create_user(payload: UserCreate):
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (payload.name.strip(), payload.email)
            )
            uid = cur.lastrowid
            row = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (uid,)).fetchone()
            return dict(row)
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail="User with that email already exists")

@app.get("/api/users", response_model=List[UserOut])
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, email FROM users ORDER BY id").fetchall()
        return [dict(r) for r in rows]

# ---- Categories ----
@app.post("/api/categories", response_model=CategoryOut)
def create_category(payload: CategoryCreate):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO categories (name) VALUES (?)", (payload.name.strip(),))
        cid = cur.lastrowid
        row = conn.execute("SELECT id, name FROM categories WHERE id = ?", (cid,)).fetchone()
        return dict(row)

@app.get("/api/categories", response_model=List[CategoryOut])
def list_categories():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return [dict(r) for r in rows]

# ---- Expenses ----
@app.post("/api/expenses", response_model=ExpenseOut)
def create_expense(payload: ExpenseCreate):
    # validate amount using Decimal
    try:
        amt = Decimal(payload.amount)
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=400, detail="Invalid amount format")
    if amt <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    expense_date = payload.date or date.today().isoformat()
    with get_conn() as conn:
        # ensure user exists
        user = conn.execute("SELECT id FROM users WHERE id = ?", (payload.user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # ensure category exists
        cat = conn.execute("SELECT id FROM categories WHERE id = ?", (payload.category_id,)).fetchone()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        cur = conn.execute(
            "INSERT INTO expenses (user_id, category_id, amount, date, note) VALUES (?, ?, ?, ?, ?)",
            (payload.user_id, payload.category_id, str(amt), expense_date, payload.note)
        )
        eid = cur.lastrowid
        row = conn.execute("SELECT id, user_id, category_id, amount, date, note FROM expenses WHERE id = ?", (eid,)).fetchone()
        result = dict(row)
        result["amount"] = format(Decimal(result["amount"]), ".2f")
        return result

@app.get("/api/expenses", response_model=List[ExpenseOut])
def get_expenses(user_id: int = Query(..., description="id of the user")):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, user_id, category_id, amount, date, note FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
            (user_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["amount"] = format(Decimal(d["amount"]), ".2f")
            out.append(d)
        return out

# ---- Monthly summary report (Tier 2) ----
@app.get("/api/reports/monthly_summary")
def monthly_summary(year: str = Query(..., min_length=4, max_length=4), month: str = Query(..., min_length=1, max_length=2), user_id: int = Query(...)):
    # normalize month to 2 digits
    month = month.zfill(2)
    with get_conn() as conn:
        # single aggregated query for total
        total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?",
            (user_id, year, month)
        ).fetchone()
        total = Decimal(total_row["total"]) if total_row and total_row["total"] is not None else Decimal("0.00")

        # expenses by category in one query
        rows = conn.execute(
            """
            SELECT c.name AS category_name, COALESCE(SUM(e.amount),0) AS total_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ? AND strftime('%Y', e.date) = ? AND strftime('%m', e.date) = ?
            GROUP BY c.name
            ORDER BY total_amount DESC
            """,
            (user_id, year, month)
        ).fetchall()

        by_cat = []
        for r in rows:
            amt = Decimal(r["total_amount"]) if r["total_amount"] is not None else Decimal("0.00")
            by_cat.append({"category_name": r["category_name"], "total_amount": format(amt, ".2f")})

        return {
            "total_expenses": format(total, ".2f"),
            "expenses_by_category": by_cat
        }
