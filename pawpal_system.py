"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta

# Higher number = more important. Used for sorting, since "high"/"medium"/"low"
# sort alphabetically in the wrong order.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# Days until a recurring task comes back after it's completed. None = never.
FREQUENCY_DAYS = {"once": None, "daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care activity, like a walk or feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "once", "daily", or "weekly"
    completed: bool = False
    time: str | None = None  # fixed start time as "HH:MM", or None if flexible
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Check that priority, duration, frequency, and time are valid."""
        _check_priority(self.priority)
        _check_duration(self.duration_minutes)
        if self.frequency not in FREQUENCY_DAYS:
            raise ValueError(f"frequency must be one of {list(FREQUENCY_DAYS)}, got {self.frequency!r}")
        if self.time is not None:
            _check_time(self.time)

    def edit(self, duration_minutes: int | None = None, priority: str | None = None) -> None:
        """Update the task's duration and/or priority."""
        if duration_minutes is not None:
            _check_duration(duration_minutes)
            self.duration_minutes = duration_minutes
        if priority is not None:
            _check_priority(priority)
            self.priority = priority

    def mark_complete(self) -> "Task | None":
        """Mark this task as done; for a daily/weekly task, return its next occurrence."""
        self.completed = True
        days = FREQUENCY_DAYS[self.frequency]
        if days is None:
            return None
        # Count from today if the task was done late, so the next one isn't already overdue.
        next_due = max(self.due_date, date.today()) + timedelta(days=days)
        return replace(self, completed=False, due_date=next_due)

    def is_due(self, today: date) -> bool:
        """Return True if this task isn't done and is due on or before today."""
        return not self.completed and self.due_date <= today

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def priority_rank(self) -> int:
        """Return the task's priority as a number from PRIORITY_RANK."""
        return PRIORITY_RANK[self.priority]


def _check_priority(priority: str) -> None:
    """Raise ValueError if priority isn't low, medium, or high."""
    if priority not in PRIORITY_RANK:
        raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}, got {priority!r}")


def _check_duration(minutes: int) -> None:
    """Raise ValueError if minutes isn't a positive number."""
    if minutes <= 0:
        raise ValueError(f"duration_minutes must be positive, got {minutes}")


def _check_time(value: str) -> None:
    """Raise ValueError if value isn't a zero-padded "HH:MM" time like "08:30"."""
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError:
        raise ValueError(f'time must look like "HH:MM", got {value!r}') from None
    # strptime accepts "8:30", but that sorts wrong as a string ("8:30" > "10:00").
    if len(value) != 5:
        raise ValueError(f'time must be zero-padded like "08:30", got {value!r}')


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove this exact task object (not just one with the same fields)."""
        self.tasks = [t for t in self.tasks if t is not task]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done and, if it repeats, add its next occurrence to this pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    """A pet owner, their pets, and how much time they have today."""

    name: str
    available_minutes: int = 60
    day_start: time = time(8, 0)  # when the first task can begin
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, each paired with its pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has for pet care today."""
        if minutes < 0:
            raise ValueError(f"available minutes can't be negative, got {minutes}")
        self.available_minutes = minutes


@dataclass
class ScheduledTask:
    """A task placed in the plan, linked to its pet and a start time."""

    pet: Pet
    task: Task
    start_time: time | None = None  # None for skipped tasks
    reason: str = ""  # why it was scheduled or skipped


class Scheduler:
    """Builds a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner, today: date | None = None) -> None:
        """Create a scheduler for this owner with an empty plan; today defaults to the real date."""
        self.owner = owner
        self.today = today or date.today()
        self.plan: list[ScheduledTask] = []
        self.skipped: list[ScheduledTask] = []

    def _at(self, t: time) -> datetime:
        """Turn a clock time into a datetime on self.today, so minutes can be added to it."""
        return datetime.combine(self.today, t)

    def sort_by_time(self, items: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs ordered by task time; tasks with no time go last."""
        if items is None:
            items = self.owner.get_all_tasks()
        # Zero-padded "HH:MM" strings sort in clock order, so no parsing is needed.
        # The key is a tuple: False sorts before True, so timed tasks come first.
        return sorted(items, key=lambda pair: (pair[1].time is None, pair[1].time or ""))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching a pet name and/or completion status; None means any."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def generate_plan(self) -> list[ScheduledTask]:
        """Rebuild today's plan: fixed-time tasks keep their slot, flexible ones fill the gaps."""
        self.plan = []
        self.skipped = [ScheduledTask(pet, task, reason="already completed")
                        for pet, task in self.filter_tasks(completed=True)]
        # Tasks not due yet (e.g. next week's bath) are left out entirely.
        due = [(pet, task) for pet, task in self.filter_tasks(completed=False)
               if task.is_due(self.today)]

        # Most important first; among equal priority, shorter tasks first so more fit.
        due.sort(key=lambda pair: (-pair[1].priority_rank(), pair[1].duration_minutes))
        # Place fixed-time tasks before flexible ones so a flexible task can't take their slot.
        timed = [pair for pair in due if pair[1].time is not None]
        flexible = [pair for pair in due if pair[1].time is None]

        minutes_left = self.owner.available_minutes
        for pet, task in timed + flexible:
            if task.duration_minutes > minutes_left:
                reason = f"needs {task.duration_minutes} min but only {minutes_left} min left"
                self.skipped.append(ScheduledTask(pet, task, reason=reason))
                continue
            if task.time is not None:
                start = time.fromisoformat(task.time)
                reason = f"fixed time, {task.priority} priority, fits in the {minutes_left} min left"
            else:
                start = self._first_free_slot(task.duration_minutes)
                reason = f"{task.priority} priority, first free slot, fits in the {minutes_left} min left"
            self.plan.append(ScheduledTask(pet, task, start, reason))
            minutes_left -= task.duration_minutes

        self.plan.sort(key=lambda item: item.start_time)
        return self.plan

    def _first_free_slot(self, duration_minutes: int) -> time:
        """Return the earliest start from day_start where a task this long fits between planned tasks."""
        start = self._at(self.owner.day_start)
        for item in sorted(self.plan, key=lambda i: i.start_time):
            item_start = self._at(item.start_time)
            if start + timedelta(minutes=duration_minutes) <= item_start:
                break  # fits in the gap before this task
            item_end = item_start + timedelta(minutes=item.task.duration_minutes)
            start = max(start, item_end)
        return start.time()

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each pair of planned tasks whose times overlap. Call generate_plan() first."""
        warnings = []
        items = sorted(self.plan, key=lambda item: item.start_time)
        for i, a in enumerate(items):
            a_end = self._at(a.start_time) + timedelta(minutes=a.task.duration_minutes)
            for b in items[i + 1:]:
                if self._at(b.start_time) >= a_end:
                    break  # sorted by start, so no later task can overlap a either
                warnings.append(
                    f"{a.task.title} ({a.pet.name}) {a.start_time:%H:%M}-{a_end:%H:%M} "
                    f"overlaps {b.task.title} ({b.pet.name}) at {b.start_time:%H:%M}"
                )
        return warnings

    def explain_plan(self) -> str:
        """Explain why each task was scheduled or skipped. Call generate_plan() first."""
        lines = []
        for item in self.plan:
            lines.append(f"Scheduled {item.task.title} for {item.pet.name}: {item.reason}.")
        for item in self.skipped:
            lines.append(f"Skipped {item.task.title} for {item.pet.name}: {item.reason}.")
        return "\n".join(lines) if lines else "No tasks to plan."

    def display_plan(self) -> str:
        """Return the plan formatted for display. Call generate_plan() first."""
        if not self.plan:
            return f"No tasks scheduled for {self.owner.name} today."
        lines = [f"Daily plan for {self.owner.name}:"]
        for item in self.plan:
            lines.append(
                f"  {item.start_time:%H:%M} - {item.task.title} for {item.pet.name} "
                f"({item.task.duration_minutes} min) [priority: {item.task.priority}]"
            )
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("Conflicts:")
            lines.extend(f"  ! {warning}" for warning in conflicts)
        return "\n".join(lines)
