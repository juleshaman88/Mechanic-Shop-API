from datetime import date
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanic = db.Table(
    "service_mechanic",
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True),
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
)

service_inventory = db.Table(
    "service_inventory",
    db.Column("inventory_id", db.ForeignKey("inventory.id"), primary_key=True),
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
)

class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    password: Mapped[str | None] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(30), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)
    service_ticket_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("service_tickets.id"),
        nullable=True,
    )

    primary_service_ticket: Mapped["ServiceTicket | None"] = relationship(
        foreign_keys=[service_ticket_id]
    )

    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=service_mechanic,
        back_populates="mechanics",
    )


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = relationship(back_populates="customer")


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    description: Mapped[str] = mapped_column(db.String(500), nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), nullable=False, default="open")
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = relationship(
        secondary=service_mechanic,
        back_populates="service_tickets",
    )
    inventory: Mapped[List["Inventory"]] = relationship(
        secondary=service_inventory,
        back_populates="service_tickets",
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=service_inventory,
        back_populates="inventory",
    )
