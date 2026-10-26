"""Temporary testing ground: build a sample owner and print today's schedule."""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Sam", available_minutes=90, day_start=time(7, 30))

    biscuit = Pet("Biscuit", "dog", age=3)
    mochi = Pet("Mochi", "cat", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 30, "high", "walk"))
    biscuit.add_task(Task("Brushing", 15, "low", "grooming"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding"))
    mochi.add_task(Task("Allergy meds", 5, "high", "meds"))
    mochi.add_task(Task("Laser pointer play", 20, "medium", "enrichment"))
    biscuit.add_task(Task("Bath", 45, "low", "grooming"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print("=== Today's Schedule ===")
    print(scheduler.display_plan())
    print()
    print("=== Why this plan ===")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
