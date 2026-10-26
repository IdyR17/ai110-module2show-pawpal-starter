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

Yes. After reviewing my first skeleton with AI, I made these suggested changes:

- **Added a `ScheduledTask` class.** It links a task to its pet, a start time, and a reason. Before, the plan was just a list of tasks, so it lost which pet each task was for and had nowhere to store times.
- **Added `day_start` to Owner.** The scheduler needs to know when the day begins to give tasks real start times.
- **Added a priority ranking (low = 1, medium = 2, high = 3).** Priorities are text, and sorting text puts "high" before "low" before "medium", which is wrong. Numbers sort correctly.
- **Made `generate_plan()` rebuild the plan from scratch each time.** Streamlit reruns the code on every click, so without this the plan would fill up with duplicate tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler looks at the owner's available minutes, each task's priority, fixed start times, and due dates (so only tasks due today are planned). Time and priority matter most: a busy owner can't go over their time, and things like meds and feeding can't be skipped for a less important task. Preferences are stored but not used yet.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler picks tasks greedily: it sorts by priority (shortest first when priorities tie) and adds each task if it still fits, without trying every combination to find the "best" one. This means a long high-priority task can use up time that could have fit two or three medium-priority tasks. For example, with 40 minutes left, a 40-minute high-priority bath beats two 20-minute medium tasks, even if the owner would have rather done both.

I think this is reasonable because the most important care (meds, feeding, walks) should always come first, even if that means fewer tasks get done. It's also easy to explain to the owner ("this was skipped because only 5 minutes were left"), and it's fast and predictable. Finding the perfect combination would be slower, harder to explain, and not worth it for a handful of tasks a day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI (Claude Code) for many steps: Brainstorming classes, drawing the Mermaid UML, writing the class skeleton, filling in the logic, and writing `main.py` and the first tests. The most helpful prompt was asking it to review its own skeleton for missing relationships and logic bottlenecks. That found real problems, like the plan losing track of which pet a task was for and priorities sorting alphabetically ("high" < "low" < "medium").

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**Accepted:** the review fixes (the `ScheduledTask` class, `day_start`, number-based priority, and rebuilding the plan from scratch each time), since each one solved a problem I could see in the code.

**Rejected or changed:**

- When writing tests, the AI also tried to add a `pytest.ini` config file and run the tests right away. I stopped that so I could set up and run the tests myself.

**How I verified:** I ran `main.py` to see the schedule in the terminal and checked that the order, start times, and skipped tasks made sense (for example, the 45-minute bath was skipped when only 10 minutes were left). I also checked that the UML matched the code after each change.

**c. AI strategy**

- **Most effective features:** Asking the AI to review its own code found real design problems early. Running `main.py` and the tests right in the editor let me check each step quickly. Having it keep the UML in sync with the code saved a lot of time.
- **A suggestion I modified:** When I asked how to simplify `generate_plan()`, the AI offered a shorter version using `itertools.accumulate`. It was more "Pythonic" but harder to read and broke the "skip a big task, keep trying smaller ones" behavior. I kept the plain `for` loop and only took the smaller fix (reusing `filter_tasks()`).
- **Separate chat sessions:** Splitting the work by phase (design, logic, testing, UI) kept each chat focused, so the AI wasn't mixing up old ideas with new ones.
- **Being the lead architect:** The AI is fast, but I have to set the direction. I decided what to build, said no when answers were too long or did more than I asked, and checked the results myself. AI made a great teammate but I was still the lead.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I have 23 tests covering sorting by time, filtering by pet or status, daily/weekly recurrence, building the plan, and conflict detection. They include edge cases like a pet with no tasks, two tasks at the same time, and back-to-back tasks (which should not count as a conflict). These matter because they're the parts most likely to break, like a time sorting wrong or a daily task not coming back.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Fairly confident (4/5). All tests pass. Next I'd test tasks that run past midnight, fixed time tasks that start before the owner's day begins, and the Streamlit UI.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The scheduler. Fixed-time tasks keep their slot, flexible ones fill the gaps, and every choice comes with a clear reason.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd use owner preferences (like "walks in the morning"), let the app suggest fixes for conflicts instead of just warning, and save data so it isn't lost when the app closes.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Design first, then build. Having a clear UML made it easy to guide the AI and to notice when its suggestions didn't fit the plan.
