from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, users, invoices, settings as company_settings, dashboard, reports, ai

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(company_settings.router, prefix="/settings", tags=["settings"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.on_event("startup")
def on_startup():
    from app.db.database import Base, engine, SessionLocal
    # Auto-create tables for deployed databases
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed admin user
    try:
        from seed_admin import seed_admin_user
        db = SessionLocal()
        seed_admin_user(db)
        db.close()
    except Exception as e:
        print(f"Failed to seed admin: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to NexAura Invoice Management System API"}
