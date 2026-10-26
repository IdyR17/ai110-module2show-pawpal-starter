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

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([{"pet": pet.name, "title": t.title, "time": t.time or "flexible",
               "duration_minutes": t.duration_minutes, "priority": t.priority,
               "repeats": t.frequency, "due": str(t.due_date)}
              for pet, t in all_tasks])
elif pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.table([{"time": f"{item.start_time:%H:%M}", "task": item.task.title,
                   "pet": item.pet.name, "minutes": item.task.duration_minutes,
                   "priority": item.task.priority}
                  for item in plan])
    else:
        st.warning("No tasks fit in today's plan.")
    for conflict in scheduler.detect_conflicts():
        st.warning(f"Conflict: {conflict}")
    st.markdown("**Why this plan**")
    st.text(scheduler.explain_plan())
