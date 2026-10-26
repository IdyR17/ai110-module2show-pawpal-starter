"""Temporary testing ground: build a sample owner and print today's schedule."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(heading: str, items: list[tuple[Pet, Task]]) -> None:
    """Print a heading and one line per (pet, task) pair."""
    print(f"=== {heading} ===")
    for pet, task in items:
        when = task.time or "--:--"
        status = "done" if task.completed else "todo"
        print(f"  {when}  {task.title} for {pet.name} [{status}, due {task.due_date}]")
    print()


def main() -> None:
    owner = Owner("Sam", available_minutes=120, day_start=time(7, 30))

    biscuit = Pet("Biscuit", "dog", age=3)
    mochi = Pet("Mochi", "cat", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added out of time order on purpose, to show sort_by_time() fixing it.
    biscuit.add_task(Task("Evening walk", 30, "high", "walk", time="18:00"))
    mochi.add_task(Task("Laser pointer play", 20, "medium", "enrichment", time="12:30"))
    biscuit.add_task(Task("Morning walk", 30, "high", "walk", time="07:30"))
    mochi.add_task(Task("Allergy meds", 5, "high", "meds", time="08:00"))
    biscuit.add_task(Task("Brushing", 15, "low", "grooming"))  # no fixed time
    # Overlaps the 07:30-08:00 morning walk, to show conflict detection.
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", time="07:45"))
    # Weekly task not due for a few days, so today's plan leaves it out.
    biscuit.add_task(Task("Bath", 45, "low", "grooming", frequency="weekly",
                          due_date=date.today() + timedelta(days=3)))

    # Allergy meds already given today. It's daily, so tomorrow's copy is created.
    meds = mochi.get_tasks()[1]
    next_meds = mochi.complete_task(meds)
    print(f"Completed {meds.title}; next one due {next_meds.due_date}\n")

    scheduler = Scheduler(owner)

    print_tasks("All tasks (as added)", owner.get_all_tasks())
    print_tasks("Sorted by time", scheduler.sort_by_time())
    print_tasks("Mochi's tasks", scheduler.filter_tasks(pet_name="Mochi"))
    print_tasks("Still to do", scheduler.filter_tasks(completed=False))
    print_tasks(
        "Biscuit's tasks to do, sorted by time",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit", completed=False)),
    )

    scheduler.generate_plan()
    print("=== Today's Schedule ===")
    print(scheduler.display_plan())
    print()
    print("=== Why this plan ===")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
