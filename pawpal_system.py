"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# Higher number = more important. Used for sorting, since "high"/"medium"/"low"
# sort alphabetically in the wrong order.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet care activity, like a walk or feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "daily" or "weekly"
    completed: bool = False

    def __post_init__(self) -> None:
        """Check that priority is one of PRIORITY_RANK's keys and duration is positive."""
        _check_priority(self.priority)
        _check_duration(self.duration_minutes)

    def edit(self, duration_minutes: int | None = None, priority: str | None = None) -> None:
        """Update the task's duration and/or priority."""
        if duration_minutes is not None:
            _check_duration(duration_minutes)
            self.duration_minutes = duration_minutes
        if priority is not None:
            _check_priority(priority)
            self.priority = priority

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

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

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for this owner with an empty plan."""
        self.owner = owner
        self.plan: list[ScheduledTask] = []
        self.skipped: list[ScheduledTask] = []

    def generate_plan(self) -> list[ScheduledTask]:
        """Rebuild the plan from scratch: clear plan/skipped, then fit tasks into the owner's time."""
        self.plan = []
        self.skipped = []

        pending = []
        for pet, task in self.owner.get_all_tasks():
            if task.completed:
                self.skipped.append(ScheduledTask(pet, task, reason="already completed"))
            else:
                pending.append((pet, task))

        # Most important first; among equal priority, shorter tasks first so more fit.
        pending.sort(key=lambda pair: (-pair[1].priority_rank(), pair[1].duration_minutes))

        minutes_left = self.owner.available_minutes
        current = datetime.combine(date.today(), self.owner.day_start)
        for pet, task in pending:
            if task.duration_minutes <= minutes_left:
                reason = f"{task.priority} priority, fits in the {minutes_left} min left"
                self.plan.append(ScheduledTask(pet, task, current.time(), reason))
                current += timedelta(minutes=task.duration_minutes)
                minutes_left -= task.duration_minutes
            else:
                reason = f"needs {task.duration_minutes} min but only {minutes_left} min left"
                self.skipped.append(ScheduledTask(pet, task, reason=reason))

        return self.plan

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
        return "\n".join(lines)
