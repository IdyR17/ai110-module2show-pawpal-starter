# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The logic lives in `pawpal_system.py` and is made of four main classes:

- **Task**: one care activity (walk, feeding, meds...) with a duration, priority, category, frequency, and done/not done status. It rejects bad input like an unknown priority or a zero-minute duration.
- **Pet**: a pet's details plus its list of tasks. You can add, remove, and list tasks.
- **Owner**: the owner's name, how many minutes they have today, when their day starts, and their pets. `get_all_tasks()` returns every pet's tasks together, each paired with its pet.
- **Scheduler**: the "brain". It reads all tasks from `Owner.get_all_tasks()`, sets aside completed ones, sorts the rest by priority (shorter first on ties), and fits them into the owner's time starting at `day_start`. Tasks that don't fit are skipped with a reason.

A small helper class, **ScheduledTask**, holds one entry in the plan: the pet, the task, its start time, and why it was scheduled or skipped. `display_plan()` prints the timed schedule and `explain_plan()` prints the reasons.

`main.py` builds a sample owner with two pets and prints the plan, as shown below.

## 🖥️ Sample Output

Output from running `python main.py`:

```
=== Today's Schedule ===
Daily plan for Sam:
  07:30 - Allergy meds for Mochi (5 min) [priority: high]
  07:35 - Breakfast for Mochi (10 min) [priority: high]
  07:45 - Morning walk for Biscuit (30 min) [priority: high]
  08:15 - Laser pointer play for Mochi (20 min) [priority: medium]
  08:35 - Brushing for Biscuit (15 min) [priority: low]

=== Why this plan ===
Scheduled Allergy meds for Mochi: high priority, fits in the 90 min left.
Scheduled Breakfast for Mochi: high priority, fits in the 85 min left.
Scheduled Morning walk for Biscuit: high priority, fits in the 75 min left.
Scheduled Laser pointer play for Mochi: medium priority, fits in the 45 min left.
Scheduled Brushing for Biscuit: low priority, fits in the 25 min left.
Skipped Bath for Biscuit: needs 45 min but only 10 min left.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests\test_pawpal.py ..                                                             [100%]

=================================== 2 passed in 0.02s ====================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by their `"HH:MM"` time. Tasks with no fixed time go last. |
| Sort for planning | `Scheduler.generate_plan()`, `Task.priority_rank()` | Highest priority first; shorter tasks first when priorities tie. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Filter by pet, by done/not done, or both. |
| Fit to available time | `Scheduler.generate_plan()`, `Scheduler._first_free_slot()` | Fixed-time tasks keep their slot; flexible tasks go in the earliest free gap. Anything that doesn't fit is skipped with a reason. |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when two planned tasks overlap (start + duration), across all pets. Shown under "Conflicts" in `display_plan()`. |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()`, `Task.is_due()` | Completing a daily/weekly task creates the next one (+1 or +7 days). Only tasks due today are planned. |

**Sorting.** `sort_by_time()` uses `sorted()` with a `lambda` key. Zero-padded `"HH:MM"` strings already sort in clock order, so no time parsing is needed. Task times are checked when a task is created so a value like `"8:30"` can't break the order.

**Filtering.** `filter_tasks()` reads every pet's tasks from `Owner.get_all_tasks()` and keeps the ones that match. Leaving a filter as `None` means "any". `generate_plan()` uses it to set aside completed tasks.

**Planning.** `generate_plan()` takes the unfinished tasks that are due today and sorts them by priority. Tasks with a fixed `time` are placed first, at that time. Flexible tasks then go into the earliest gap starting at `day_start`. Every task counts against the owner's available minutes. It's greedy: it doesn't search for the best combination, but it keeps trying smaller tasks after a big one doesn't fit.

**Conflict detection.** `detect_conflicts()` sorts the planned tasks by start time and checks each one against the tasks after it. If the next task starts before the current one ends, that's a conflict. Because the list is sorted, it can stop checking as soon as a later task starts after the current one ends. Conflicts are warnings only: the plan isn't changed, and the owner decides what to move.

**Recurring tasks.** Each task has a `frequency` (`"once"`, `"daily"`, `"weekly"`) and a `due_date`. `mark_complete()` marks the task done and returns a copy due 1 or 7 days later (counted from today if the task was done late). `Pet.complete_task()` adds that copy to the pet. `generate_plan()` only includes tasks where `is_due(today)` is true, so next week's bath doesn't show up today.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
