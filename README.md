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

## ✨ Features

- **Multiple pets:** one owner can have many pets, and the schedule covers all of them.
- **Sorting by time:** tasks are listed in clock order. Tasks without a set time go last.
- **Filtering:** show tasks for one pet, or only tasks that are done or still to do.
- **Priority planning:** high-priority tasks are scheduled first. If priorities tie, shorter tasks go first so more fit.
- **Fixed and flexible times:** tasks with a set time keep it. Tasks without one fill the first free gap in the day.
- **Time limit:** the plan never uses more minutes than the owner has. Tasks that don't fit are skipped with a reason.
- **Conflict warnings:** if two tasks overlap (even for different pets), the app shows a warning.
- **Daily and weekly recurrence:** finishing a daily task creates tomorrow's copy; a weekly task comes back in 7 days. Tasks not due yet stay out of today's plan.
- **Plan explanations:** every task in the plan says why it was scheduled or skipped.

## 🛠️ Implementation Summary

The logic lives in `pawpal_system.py` and is made of four main classes:

- **Task**: one care activity (walk, feeding, meds...) with a duration, priority, category, how often it repeats, an optional fixed time, a due date, and done/not done status. It rejects bad input like an unknown priority or a zero-minute duration. Completing a daily or weekly task creates its next copy.
- **Pet**: a pet's details plus its list of tasks. You can add, remove, list, and complete tasks.
- **Owner**: the owner's name, how many minutes they have today, when their day starts, and their pets. `get_all_tasks()` returns every pet's tasks together, each paired with its pet.
- **Scheduler**: the "brain". It reads all tasks from `Owner.get_all_tasks()`, keeps the ones due today, and sorts them by priority. Fixed-time tasks keep their time, and flexible tasks fill the first free gap after `day_start`. Tasks that don't fit are skipped with a reason. It can also sort and filter tasks, and warn about overlapping tasks.

A small helper class, **ScheduledTask**, holds one entry in the plan: the pet, the task, its start time, and why it was scheduled or skipped. `display_plan()` prints the timed schedule and any conflicts, and `explain_plan()` prints the reasons.

`main.py` builds a sample owner with two pets and prints the plan, as shown below.

## 🖥️ Sample Output

The schedule part of `python main.py` (the full output is in the Demo Walkthrough below):

```
=== Today's Schedule ===
Daily plan for Sam:
  07:30 - Morning walk for Biscuit (30 min) [priority: high]
  07:45 - Breakfast for Mochi (10 min) [priority: high]
  08:00 - Brushing for Biscuit (15 min) [priority: low]
  12:30 - Laser pointer play for Mochi (20 min) [priority: medium]
  18:00 - Evening walk for Biscuit (30 min) [priority: high]
Conflicts:
  ! Morning walk (Biscuit) 07:30-08:00 overlaps Breakfast (Mochi) at 07:45
```

## 🧪 Testing PawPal+

Run the tests with:

```bash
python -m pytest
```

The tests cover sorting tasks by time, filtering by pet or status, recurring daily/weekly tasks, building the daily plan, and conflict detection. They include edge cases like a pet with no tasks, two tasks at the same time, and back-to-back tasks.

```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Projects\codepath\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 23 items

tests\test_pawpal.py .......................                             [100%]

============================= 23 passed in 0.03s ==============================
```

**Confidence level: ⭐⭐⭐⭐☆ (4/5)**. All tests pass, but the Streamlit UI isn't tested automatically, and tasks that run past midnight aren't handled yet.

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

Start the app with `streamlit run app.py`.

**What you can do in the app**

- **Owner:** set your name, how many minutes you have today, and when your day starts.
- **Pets:** add pets with a name, species, and age.
- **Tasks:** add a task to a pet with a duration, priority, category, how often it repeats, and (optionally) a fixed start time.
- **Task list:** see all tasks sorted by time, filter by pet or by done/to do, and mark a task complete.
- **Build Schedule:** generate today's plan and see the times, any conflicts, skipped tasks, and why each task was chosen.

**Example workflow**

1. Set the owner to "Sam" with 120 minutes, starting at 07:30.
2. Add two pets: Biscuit (dog) and Mochi (cat).
3. Give Biscuit a "Morning walk" (30 min, high, fixed at 07:30) and Mochi a "Breakfast" (10 min, high, fixed at 07:45).
4. Add a flexible "Brushing" task for Biscuit (15 min, low).
5. Check the task list: tasks appear in time order, with Brushing last because it has no fixed time.
6. Click **Generate schedule**. The walk and breakfast keep their times, Brushing goes into the first free gap (08:00), and a warning appears because the walk (07:30–08:00) overlaps breakfast.
7. Mark Mochi's breakfast complete. Because it's a daily task, a new copy appears in the list, due tomorrow.

**Scheduler behaviors shown**

- Sorting by time in the task list.
- Filtering by pet and status.
- Fixed-time tasks keeping their slot, with flexible tasks filling the gaps.
- Conflict warnings for overlapping tasks.
- Daily recurrence when a task is marked complete.

**Sample CLI output from `python main.py`** (shortened):

```
Completed Allergy meds; next one due 2026-10-27

=== Sorted by time ===
  07:30  Morning walk for Biscuit [todo, due 2026-10-26]
  07:45  Breakfast for Mochi [todo, due 2026-10-26]
  08:00  Allergy meds for Mochi [done, due 2026-10-26]
  08:00  Allergy meds for Mochi [todo, due 2026-10-27]
  12:30  Laser pointer play for Mochi [todo, due 2026-10-26]
  18:00  Evening walk for Biscuit [todo, due 2026-10-26]
  --:--  Brushing for Biscuit [todo, due 2026-10-26]
  --:--  Bath for Biscuit [todo, due 2026-10-29]

=== Today's Schedule ===
Daily plan for Sam:
  07:30 - Morning walk for Biscuit (30 min) [priority: high]
  07:45 - Breakfast for Mochi (10 min) [priority: high]
  08:00 - Brushing for Biscuit (15 min) [priority: low]
  12:30 - Laser pointer play for Mochi (20 min) [priority: medium]
  18:00 - Evening walk for Biscuit (30 min) [priority: high]
Conflicts:
  ! Morning walk (Biscuit) 07:30-08:00 overlaps Breakfast (Mochi) at 07:45

=== Why this plan ===
Scheduled Morning walk for Biscuit: fixed time, high priority, fits in the 80 min left.
Scheduled Breakfast for Mochi: fixed time, high priority, fits in the 120 min left.
Scheduled Brushing for Biscuit: low priority, first free slot, fits in the 30 min left.
Scheduled Laser pointer play for Mochi: fixed time, medium priority, fits in the 50 min left.
Scheduled Evening walk for Biscuit: fixed time, high priority, fits in the 110 min left.
Skipped Allergy meds for Mochi: already completed.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
