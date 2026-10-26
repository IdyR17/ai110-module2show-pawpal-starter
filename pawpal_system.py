"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity, like a walk or feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "daily" or "weekly"
    completed: bool = False

    def edit(self, duration_minutes: int | None = None, priority: str | None = None) -> None:
        """Update the task's duration and/or priority."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        pass


@dataclass
class Owner:
    """A pet owner, their pets, and how much time they have today."""

    name: str
    available_minutes: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has for pet care today."""
        pass


class Scheduler:
    """Builds a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped: list[Task] = []

    def generate_plan(self) -> list[Task]:
        """Pick and order tasks that fit in the owner's available time."""
        pass

    def explain_plan(self) -> str:
        """Explain why each task was scheduled or skipped."""
        pass

    def display_plan(self) -> str:
        """Return the plan formatted for display."""
        pass
