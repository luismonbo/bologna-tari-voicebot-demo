#!/usr/bin/env python
"""Delete appointments from the database.

Usage:
  uv run scripts/delete_appointment.py --all                                  # Delete all appointments
  uv run scripts/delete_appointment.py --name "Luigi Rossi"                  # Delete all by citizen name
  uv run scripts/delete_appointment.py --date 2026-06-30                     # Delete all on date
  uv run scripts/delete_appointment.py --name "Luigi Rossi" --date 2026-06-30 # Delete specific appointment
"""

import asyncio
import os
import sys
from argparse import ArgumentParser

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from app.database import AppointmentModel, SessionLocal
from sqlalchemy import delete, select


async def delete_appointments(all: bool = False, name: str = None, date: str = None):
    """Delete appointments based on criteria."""
    async with SessionLocal() as session:
        query = delete(AppointmentModel)

        if all:
            print("🗑️  Deleting ALL appointments...")
        elif name and date:
            query = query.where(AppointmentModel.citizen_name == name).where(
                AppointmentModel.date == date
            )
            print(f"🗑️  Deleting appointment for {name} on {date}")
        elif name:
            query = query.where(AppointmentModel.citizen_name == name)
            print(f"🗑️  Deleting all appointments for: {name}")
        elif date:
            query = query.where(AppointmentModel.date == date)
            print(f"🗑️  Deleting all appointments on date: {date}")
        else:
            print("❌ Please specify --all, --name, --date, or both --name and --date")
            return

        # Show what will be deleted first
        select_query = select(AppointmentModel)
        if name:
            select_query = select_query.where(AppointmentModel.citizen_name == name)
        if date:
            select_query = select_query.where(AppointmentModel.date == date)

        result = await session.execute(select_query)
        appointments = result.scalars().all()

        if not appointments and not all:
            print("⚠️  No matching appointments found")
            return

        if not all:
            print(f"\nFound {len(appointments)} appointment(s):")
            for apt in appointments:
                print(f"  • {apt.office} on {apt.date} at {apt.time} ({apt.citizen_name})")

            confirm = input("\nConfirm deletion (y/N)? ").lower()
            if confirm != "y":
                print("Cancelled")
                return

        # Delete
        result = await session.execute(query)
        await session.commit()

        deleted_count = result.rowcount
        print(f"✅ Deleted {deleted_count} appointment(s)")


def main():
    parser = ArgumentParser(description="Delete appointments from the database")
    parser.add_argument("--all", action="store_true", help="Delete all appointments")
    parser.add_argument("--name", type=str, help="Citizen name")
    parser.add_argument("--date", type=str, help="Date (YYYY-MM-DD)")

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.name and not args.date:
        parser.print_help()
        sys.exit(1)

    asyncio.run(delete_appointments(all=args.all, name=args.name, date=args.date))


if __name__ == "__main__":
    main()
