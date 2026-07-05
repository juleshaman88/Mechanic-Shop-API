from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_ticket_mechanics = db.Table(
    "service_ticket_mechanics",
    db.metadata,
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True),
)


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(30), nullable=False)

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        secondary=service_ticket_mechanics,
        back_populates="mechanics",
    )


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    description: Mapped[str] = mapped_column(db.String(500), nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), nullable=False, default="open")

    mechanics: Mapped[list[Mechanic]] = relationship(
        secondary=service_ticket_mechanics,
        back_populates="service_tickets",
    )
