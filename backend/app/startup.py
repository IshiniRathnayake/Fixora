"""Database bootstrap: tables, roles, demo users, sample enterprise data."""

from sqlalchemy.orm import Session

from app.api.deps import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.entities import Inventory, Order, Role, User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_roles(db)
        _seed_users(db)
        _seed_enterprise(db)
        db.commit()
    finally:
        db.close()


def _seed_roles(db: Session) -> None:
    defaults = [
        (1, "administrator", "Full access: agents, alerts, users, configuration"),
        (2, "viewer", "Read-only: dashboard, alerts, diagnostics"),
    ]
    for rid, name, desc in defaults:
        if not db.query(Role).filter(Role.id == rid).first():
            db.add(Role(id=rid, name=name, description=desc))


def _seed_users(db: Session) -> None:
    users = [
        ("admin@fixora.local", "admin123", "System Administrator", 1),
        ("viewer@fixora.local", "viewer123", "Business Viewer", 2),
    ]
    for email, password, name, role_id in users:
        user = db.query(User).filter(User.email == email).first()
        hashed = hash_password(password)
        if user:
            user.password_hash = hashed
            user.full_name = name
            user.role_id = role_id
            user.is_active = True
        else:
            db.add(
                User(
                    email=email,
                    password_hash=hashed,
                    full_name=name,
                    role_id=role_id,
                )
            )


def _seed_enterprise(db: Session) -> None:
    if db.query(Order).count() == 0:
        db.add_all(
            [
                Order(order_ref="ORD-1001", customer_name="Acme Corp", status="completed", total_amount=1250.00),
                Order(order_ref="ORD-1002", customer_name="Beta Ltd", status="processing", total_amount=890.50),
                Order(order_ref="ORD-1003", customer_name="Gamma Inc", status="failed", total_amount=320.00),
            ]
        )
    if db.query(Inventory).count() == 0:
        db.add_all(
            [
                Inventory(sku="SKU-A01", product_name="Widget Alpha", quantity=150),
                Inventory(sku="SKU-B02", product_name="Component Beta", quantity=42),
                Inventory(sku="SKU-C03", product_name="Module Gamma", quantity=0),
            ]
        )
