from datetime import date, datetime, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this whole script on every click, so keep the Owner in
# session_state. Only create it the first time; after that, reuse the same one.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
col1, col2, col3 = st.columns(3)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    minutes = st.number_input(
        "Time available (minutes)", min_value=0, max_value=1440, value=owner.available_minutes
    )
    owner.set_available_time(int(minutes))
with col3:
    owner.day_start = st.time_input("Day starts at", value=owner.day_start)

st.markdown("### Pets")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    elif any(p.name == pet_name for p in owner.get_pets()):
        st.error(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name, species, int(age)))
        st.success(f"Added {pet_name}.")

if owner.get_pets():
    st.table([{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.get_tasks())}
              for p in owner.get_pets()])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
pets = owner.get_pets()
if not pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pet_choice = st.selectbox("For pet", [p.name for p in pets])
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col3:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "enrichment", "grooming", "general"]
        )
    col1, col2 = st.columns(2)
    with col1:
        frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])
    with col2:
        fixed = st.checkbox("Fixed start time")
        task_time = st.time_input("Start time", value=owner.day_start, disabled=not fixed)

    if st.button("Add task"):
        pet = next(p for p in pets if p.name == pet_choice)
        try:
            when = f"{task_time:%H:%M}" if fixed else None
            pet.add_task(Task(task_title, int(duration), priority, category, frequency, time=when))
            st.success(f"Added {task_title} for {pet.name}.")
        except ValueError as e:
            st.error(str(e))

scheduler = Scheduler(owner)

if owner.get_all_tasks():
    st.markdown("#### Task list")
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in pets])
    with col2:
        status_filter = st.radio("Status", ["To do", "Done", "All"], horizontal=True)

    # Filter first, then sort the result by time.
    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"To do": False, "Done": True, "All": None}[status_filter],
    )
    shown = scheduler.sort_by_time(filtered)
    if shown:
        st.table([{"time": t.time or "flexible", "pet": pet.name, "task": t.title,
                   "minutes": t.duration_minutes, "priority": t.priority,
                   "repeats": t.frequency, "due": str(t.due_date),
                   "status": "✅ done" if t.completed else "⏳ to do"}
                  for pet, t in shown])
        st.caption("Sorted by time; tasks without a fixed time are listed last.")
    else:
        st.info("No tasks match these filters.")

    to_do = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if to_do:
        labels = [f"{t.time or 'flexible'} · {t.title} ({pet.name}, due {t.due_date})"
                  for pet, t in to_do]
        choice = st.selectbox("Mark a task complete", labels)
        if st.button("Mark complete"):
            pet, task = to_do[labels.index(choice)]
            next_task = pet.complete_task(task)
            message = f"Done: {task.title} for {pet.name}."
            if next_task:
                message += f" Next one due {next_task.due_date}."
            # Rerun so the table above shows the change; keep the message for the next run.
            st.session_state.flash = message
            st.rerun()
elif pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()
    used = sum(item.task.duration_minutes for item in plan)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks scheduled", len(plan))
    col2.metric("Time used", f"{used} / {owner.available_minutes} min")
    col3.metric("Conflicts", len(conflicts))

    if plan:
        rows = []
        for item in plan:
            start = datetime.combine(date.today(), item.start_time)
            end = start + timedelta(minutes=item.task.duration_minutes)
            rows.append({"time": f"{start:%H:%M}–{end:%H:%M}", "task": item.task.title,
                         "pet": item.pet.name, "priority": item.task.priority,
                         "type": "fixed" if item.task.time else "flexible"})
        st.table(rows)
    else:
        st.warning("No tasks fit in today's plan.")

    if conflicts:
        for conflict in conflicts:
            st.warning(f"⚠️ Conflict: {conflict}. Consider moving one of these tasks.")
    elif plan:
        st.success("No time conflicts. This plan works!")

    not_fit = [item for item in scheduler.skipped if item.reason != "already completed"]
    if not_fit:
        st.markdown("**Skipped today**")
        st.table([{"task": item.task.title, "pet": item.pet.name, "reason": item.reason}
                  for item in not_fit])

    with st.expander("Why this plan"):
        st.text(scheduler.explain_plan())
