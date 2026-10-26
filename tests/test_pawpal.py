"""Tests for the PawPal+ logic layer."""

from datetime import date, time

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

# A fixed "today" so tests don't depend on the day they're run.
TODAY = date(2026, 1, 15)


def make_owner(*pets: Pet, minutes: int = 240) -> Owner:
    """Build an owner whose day starts at 07:00 with the given pets."""
    owner = Owner("Sam", available_minutes=minutes, day_start=time(7, 0))
    for pet in pets:
        owner.add_pet(pet)
    return owner


def titles(pairs) -> list[str]:
    """Pull just the task titles out of a list of (pet, task) pairs."""
    return [task.title for _, task in pairs]


# --- Basics ---------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.get_tasks()) == 1


# --- Sorting --------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Dinner", 10, time="18:00"))
    pet.add_task(Task("Walk", 30, time="07:30"))
    pet.add_task(Task("Lunch", 10, time="12:00"))
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    assert titles(scheduler.sort_by_time()) == ["Walk", "Lunch", "Dinner"]


def test_sort_by_time_handles_hours_before_and_after_ten():
    # "09:30" < "10:00" only works because times are zero-padded.
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Late", 10, time="10:00"))
    pet.add_task(Task("Early", 10, time="09:30"))
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    assert titles(scheduler.sort_by_time()) == ["Early", "Late"]


def test_sort_by_time_puts_untimed_tasks_last():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Brushing", 15))  # no time
    pet.add_task(Task("Walk", 30, time="07:30"))
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    assert titles(scheduler.sort_by_time()) == ["Walk", "Brushing"]


def test_sort_by_time_keeps_tasks_at_the_same_time():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    dog.add_task(Task("Dog breakfast", 10, time="08:00"))
    cat.add_task(Task("Cat breakfast", 10, time="08:00"))
    scheduler = Scheduler(make_owner(dog, cat), today=TODAY)

    result = scheduler.sort_by_time()

    assert len(result) == 2
    assert {t.time for _, t in result} == {"08:00"}


def test_sort_by_time_with_pet_that_has_no_tasks():
    scheduler = Scheduler(make_owner(Pet("Biscuit", "dog")), today=TODAY)

    assert scheduler.sort_by_time() == []


def test_time_must_be_zero_padded():
    with pytest.raises(ValueError):
        Task("Walk", 30, time="9:30")


# --- Filtering ------------------------------------------------------------

def test_filter_tasks_by_pet_and_status():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    walk = Task("Walk", 30)
    dog.add_task(walk)
    dog.add_task(Task("Brushing", 15))
    cat.add_task(Task("Breakfast", 10))
    walk.mark_complete(TODAY)
    scheduler = Scheduler(make_owner(dog, cat), today=TODAY)

    assert titles(scheduler.filter_tasks(pet_name="Mochi")) == ["Breakfast"]
    assert titles(scheduler.filter_tasks(completed=True)) == ["Walk"]
    assert titles(scheduler.filter_tasks(pet_name="Biscuit", completed=False)) == ["Brushing"]
    assert scheduler.filter_tasks(pet_name="Nobody") == []


# --- Recurring tasks ------------------------------------------------------

def test_completing_daily_task_creates_one_for_tomorrow():
    pet = Pet("Mochi", "cat")
    meds = Task("Allergy meds", 5, "high", frequency="daily", time="08:00", due_date=TODAY)
    pet.add_task(meds)

    next_meds = pet.complete_task(meds, today=TODAY)

    assert meds.completed is True
    assert next_meds is not None
    assert next_meds.completed is False
    assert next_meds.due_date == date(2026, 1, 16)
    assert (next_meds.title, next_meds.time) == ("Allergy meds", "08:00")
    assert len(pet.get_tasks()) == 2


def test_completing_weekly_task_creates_one_for_next_week():
    bath = Task("Bath", 45, frequency="weekly", due_date=TODAY)

    next_bath = bath.mark_complete(TODAY)

    assert next_bath.due_date == date(2026, 1, 22)


def test_completing_one_time_task_creates_nothing():
    pet = Pet("Biscuit", "dog")
    vet = Task("Vet visit", 60, frequency="once", due_date=TODAY)
    pet.add_task(vet)

    assert pet.complete_task(vet, today=TODAY) is None
    assert len(pet.get_tasks()) == 1


def test_late_daily_task_comes_back_tomorrow_not_in_the_past():
    overdue = Task("Feeding", 10, frequency="daily", due_date=date(2026, 1, 12))

    next_task = overdue.mark_complete(TODAY)

    assert next_task.due_date == date(2026, 1, 16)


def test_tomorrows_copy_is_not_in_todays_plan():
    pet = Pet("Mochi", "cat")
    meds = Task("Allergy meds", 5, frequency="daily", due_date=TODAY)
    pet.add_task(meds)
    pet.complete_task(meds, today=TODAY)
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    assert scheduler.generate_plan() == []


# --- Planning -------------------------------------------------------------

def test_fixed_time_task_keeps_its_time():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Evening walk", 30, "high", time="18:00", due_date=TODAY))
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    plan = scheduler.generate_plan()

    assert plan[0].start_time == time(18, 0)


def test_flexible_task_goes_in_first_free_gap():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Walk", 30, time="07:00", due_date=TODAY))
    pet.add_task(Task("Brushing", 15, due_date=TODAY))  # flexible
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    plan = scheduler.generate_plan()

    brushing = next(item for item in plan if item.task.title == "Brushing")
    assert brushing.start_time == time(7, 30)


def test_owner_with_pet_but_no_tasks_gets_empty_plan():
    scheduler = Scheduler(make_owner(Pet("Biscuit", "dog")), today=TODAY)

    assert scheduler.generate_plan() == []
    assert scheduler.detect_conflicts() == []


def test_generate_plan_twice_does_not_duplicate():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Walk", 30, due_date=TODAY))
    scheduler = Scheduler(make_owner(pet), today=TODAY)

    scheduler.generate_plan()
    scheduler.generate_plan()

    assert len(scheduler.plan) == 1


def test_task_that_does_not_fit_is_skipped():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Bath", 45, due_date=TODAY))
    scheduler = Scheduler(make_owner(pet, minutes=30), today=TODAY)

    assert scheduler.generate_plan() == []
    assert "only 30 min left" in scheduler.skipped[0].reason


# --- Conflict detection ---------------------------------------------------

def test_two_tasks_at_the_same_time_are_flagged():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    dog.add_task(Task("Dog breakfast", 10, time="08:00", due_date=TODAY))
    cat.add_task(Task("Cat breakfast", 10, time="08:00", due_date=TODAY))
    scheduler = Scheduler(make_owner(dog, cat), today=TODAY)
    scheduler.generate_plan()

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Dog breakfast" in conflicts[0] and "Cat breakfast" in conflicts[0]


def test_overlapping_tasks_are_flagged():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    dog.add_task(Task("Walk", 30, time="07:30", due_date=TODAY))  # 07:30-08:00
    cat.add_task(Task("Breakfast", 10, time="07:45", due_date=TODAY))
    scheduler = Scheduler(make_owner(dog, cat), today=TODAY)
    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 1


def test_back_to_back_tasks_are_not_a_conflict():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Walk", 30, time="07:30", due_date=TODAY))  # ends 08:00
    pet.add_task(Task("Breakfast", 10, time="08:00", due_date=TODAY))
    scheduler = Scheduler(make_owner(pet), today=TODAY)
    scheduler.generate_plan()

    assert scheduler.detect_conflicts() == []


def test_long_task_overlapping_two_others_gives_two_warnings():
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Hike", 60, time="07:00", due_date=TODAY))  # 07:00-08:00
    pet.add_task(Task("Meds", 5, time="07:15", due_date=TODAY))
    pet.add_task(Task("Breakfast", 10, time="07:30", due_date=TODAY))
    scheduler = Scheduler(make_owner(pet), today=TODAY)
    scheduler.generate_plan()

    assert len(scheduler.detect_conflicts()) == 2
