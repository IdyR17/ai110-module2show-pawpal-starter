# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Core user actions:

1. Enter owner and pet info (name, pet type, time available today).
2. Add or edit care tasks, each with a duration and priority.
3. Generate today's plan and see why each task was chosen.

My UML has four classes. An Owner has pets, each Pet has tasks, and the Scheduler uses all of that to build the daily plan.

- **Owner**: holds the owner's name, how much time they have today, their preferences, and their pets. It can add pets and update the available time.
- **Pet**: holds the pet's name, species, age, and its list of care tasks. It can add, remove, and list tasks.
- **Task**: one care activity, like a walk or feeding. It holds the title, how long it takes, priority, category, how often it happens, and whether it's done. It can be edited or marked complete.
- **Scheduler**: does the planning. It looks at the owner's pets and tasks, picks the most important ones that fit in the available time, and explains why it chose or skipped each task.

I kept the planning in its own Scheduler class so the other three classes just hold data. That makes the scheduling easier to change and test.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. After reviewing my first skeleton, I made these changes:

- **Added a `ScheduledTask` class.** It links a task to its pet, a start time, and a reason. Before, the plan was just a list of tasks, so it lost which pet each task was for and had nowhere to store times.
- **Added `day_start` to Owner.** The scheduler needs to know when the day begins to give tasks real start times.
- **Added a priority ranking (low = 1, medium = 2, high = 3).** Priorities are text, and sorting text puts "high" before "low" before "medium", which is wrong. Numbers sort correctly.
- **Made `generate_plan()` rebuild the plan from scratch each time.** Streamlit reruns the code on every click, so without this the plan would fill up with duplicate tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
