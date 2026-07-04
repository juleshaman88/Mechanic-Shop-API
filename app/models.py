from datetime import date

from sqlalchemy import Date, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import Base


service_ticket_mechanics = Table(
    "service_ticket_mechanics",
    Base.metadata,
    Column("service_ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
    Column("mechanic_id", ForeignKey("mechanics.id"), primary_key=True),
)


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        secondary=service_ticket_mechanics,
        back_populates="mechanics",
    )


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")

    mechanics: Mapped[list[Mechanic]] = relationship(
        secondary=service_ticket_mechanics,
        back_populates="service_tickets",
    )
