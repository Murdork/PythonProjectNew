---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# COM4018 — Introduction to Programming — Assignment Brief (Markdown Port)

## Overview

* **Assessment type:** Coursework (100% of module grade).
* **Structure:** Three tasks to be completed **in sequence**.
* **Deliverables inside the report:** screenshots, flowcharts, and **code in text** (functional code included in an appendix so it can be verified).

### Learning Outcomes

1. Understand data structures and programming techniques in the context of a programming language.
2. Understand how programs are developed (from concept to development and testing).
3. Write programs using appropriate structure and language rules.

### Graduate Attribute (relevant)

* **Discipline Expertise:** Knowledge and understanding of the chosen field; skills to operate in the sector; awareness of current developments and ability to respond to change.

---

## Guidance (report format and word count)

* Include a **title page** with: student number, module name, submission deadline, **exact word count**; include appendices (if relevant) and a **reference list** using **AU Harvard**.
* **Anonymous marking:** do **not** include your name; do include your **STU number**.
* **Maximum word count:** **3,000 words**.

  * Word count **includes** everything in the main body (including in‑text citations and references).
  * Word count **excludes** numerical data in tables, figures, diagrams, footnotes, reference list, and appendices.
  * Up to **+10%** over the limit incurs **no penalty**, but **no marks** are awarded past the maximum size limit.

---

## Scenario

* **Scenario and pricing**
You are required to create and test a new software system for a small shop loaning fishing and camping equipment for hire to customers.
The fishing and camping equipment available for hire and the cost is listed below. Customers can rent it from 9am to 6pm each day.
The equipment can be hired from 9am of day 1 but should be returned by 2pm the next day irrespective of the time of collection on day 1.
For each additional night a 50% discount is applied for each piece of equipment hired.
If the equipment is returned after 2pm, it will still be counted as an additional night and extra 50% payment for each piece of equipment hired will need to be paid.


You will create and test a new software system for a **small shop** that loans **fishing and camping equipment**.

* **Opening hours for hire:** 9:00–18:00 daily.
* **Standard hire window:** From **09:00 Day 1** to **14:00 Day 2** regardless of pickup time on Day 1.
* **Additional nights:** Each extra night is charged at **50% of the per‑item cost**.
* **Late returns:** If returned **after 14:00**, it counts as an **additional night** and incurs an **extra 50% per item**.

The system must:

* Record **customer and hire details** (see *Customer and Equipment Details* below).
* Produce an **operator report** (see *Earnings Report* below).
* **Start with a menu** (include options to capture *Customer and hire details* and *Earnings report*, plus *Exit*).

### Equipment and Hire Costs (per item)

* Day chairs — **£15.00**
* Bed chairs — **£25.00**
* Bite Alarm (set of 3) — **£20.00**
* Bite Alarm (single) — **£5.00**
* Bait Boat — **£60.00**
* Camping tent — **£20.00**
* Sleeping bag — **£20.00**
* Rods (3lb TC) — **£10.00**
* Rods (Bait runners) — **£5.00**
* Reels (Bait runners) — **£10.00**
* Camping Gas stove (Double burner) — **£10.00**

### Customer and Equipment Details (data to store)

* Customer ID
* Customer Name
* Phone Number
* House Number
* Postcode
* Credit/Debit Card (reference)
* **Equipment type(s) with quantity** (e.g., *Bed chairs — 2; Camping tent — 1*)

### Earnings Report (required columns)

* Customer ID
* Equipment (summary)
* Number of nights
* Total cost
* Returned on time (y/n)
* Extra charge for delayed return

---

## Assignment Requirements (files and implementation constraints)

* **Submit three separate files:**

  1. **One** MS Word **.docx** document (contains all tasks and the appendix with code in text).
  2. **Two** Python **.py** files: one for **Task 1 only** and one for **Tasks 2 & 3**.
* **File naming:**

  * Word document: `<student_number>.docx`.
  * Python files: `<student_number>_T1.py` (Task 1) and `<student_number>.py` (Tasks 2 & 3).
* **Do not** zip/compress; **incorrect formats** will result in **zero (0) marks**.
* **Clarity:** All flowcharts and screenshots must be **legible without zooming**; annotate screenshots or add concise explanations where helpful.
* **Code quality:** Comment code appropriately.
* **Input validation:** Include wherever applicable.
* **Restrictions:** **Do not import any Python modules.**

---

## Task 1 — Main User Menu (900 words eq., 30 marks)

**A. Flowchart:**

* Display the **main menu** (as per brief) and accept a user option.
* After executing the selected option, **redisplay** the menu.
* The algorithm ends **only when Exit is selected**.
* **Detailed requirements:**

  1. Include **input validation** for the valid menu inputs.
  2. Follow common **notations and conventions**.
  3. At this stage, selecting options **only prints messages**:

     * Option 1 → `Customer and hire details selected`
     * Option 2 → `Earnings report selected`

**B. Python program:** Implement the flowchart.

**C. Evidence:** Provide **sufficient screenshots** showing the program works as expected.

---

## Task 2 — Hiring Equipment (1200 words eq., 40 marks)

Design the algorithm for **menu option 1** (hiring), implement it in Python, and integrate it with Task 1.

* Use **suitable data structures** to store all data needed (see *Customer and Equipment Details*).
* Demonstrate at least **10 hires**, covering:

  * Each **equipment type** at least once.
  * **Different numbers of days**.
  * **Late returns**.
* Ensure the data structures are **accessible to both Task 2 and Task 3**.
* To modularise the program, put this functionality in a **subroutine** invoked from the main menu.

**A. Pseudocode (for the subroutine):**

1. Accept user inputs for equipment types and quantities as per the task summary.
2. Ignore table formatting in pseudocode; **output the required data**.
3. Enter data via **keyboard input**, storing it in **mutable data structure(s)** separate from any **read‑only reference data**.
4. **No input validation** is required in the pseudocode.
5. Follow standard conventions: **indentation**, descriptive **names** for variables/subroutines, control structures, operators, and pseudo‑keywords.

**B. Python program:** Start from the menu; when **Option 1** is chosen, call the hiring subroutine. Implement according to the pseudocode, **adding input validation** and formatting output as specified.

> *Note:* Copy the Task 1 program and alter it for Option 1 in the new file; **do not** modify the Task 1 `.py` file.

**C. Evidence:** Provide **sufficient screenshots** of sample runs demonstrating expected behaviour.

---

## Task 3 — Earnings Report (900 words eq., 30 marks)

Design the algorithm for **menu option 2** (earnings report), implement it in Python, and integrate it with Task 2.

* Use the **data stored in Task 2**.
* Display a report **similar to the specified columns** (*Earnings Report* above). You may ignore columnar formatting in the flowchart.
* The displayed data should **reflect all hires recorded so far**. If more orders are placed, subsequent reports should show **increased earnings** accordingly.

**A. Flowchart (for the subroutine):**

1. Use data captured in Task 2.
2. Produce the required columns (formatting details not enforced in the flowchart).
3. Ensure the output reflects **cumulative state** (orders added over time appear in later reports).
4. Follow standard notations and conventions.

**B. Python program:** Modify the Task 2 code so that when **Option 2** is selected, the **report subroutine** is called. Implement it per the flowchart and **match the output format**.

**C. Evidence:** Provide **sufficient screenshots** of sample runs.

---

## Referencing and Feedback

* **Referencing:** Underpin your analysis/evaluation with appropriate, wide‑ranging academic research, referenced using **AU Harvard** (see Arden Library *Referencing & Avoiding Plagiarism* guide).
* **Formative feedback:** You may submit **up to 30%** of your work for **one** round of feedback. **Week 8 Friday** is the last day for hand‑in for feedback. Distance learners should email their tutor **no later than two weeks** before the final submission week. No formative feedback will be given **after** the specified time.
* **Tutor updates:** Technology/platform details may change; tutors will provide up‑to‑date details.

---

## Assessment Criteria (Generic — Level 4)

* **Outstanding (80%+)** — Confident analysis and application of theory; excellent use of sources; excellent academic/professional skills; originality.
* **Excellent (70–79%)** — Strong analysis and theory application; high competence with sources; excellent skills; originality.
* **Very Good (60–69%)** — Clear analysis; some theory; very good use of sources; accurate expression; some originality.
* **Good (50–59%)** — Begins to analyse/apply theory; sound use of basic sources; generally accurate but may lack structure; limited originality.
* **Satisfactory (40–49%)** — Some omissions in understanding/theory/ethics; limited use of sources; errors in expression; may lack structure; difficulties with professional skills; largely imitative.
* **Marginal Fail (30–39%)** — Limited performance; omissions in understanding/theory/ethics; weak academic writing; structural issues; limited originality.
* **Clear Fail (≤29%)** — Substantial gaps in knowledge/theory/ethics; very weak writing; numerous errors; lacks structure; professional skills not developed; imitative.

---

## Marking Rubric (By Component)

> **Weighting per task:** Algorithm — **40%**; Code in text — **30%**; Sample output/screenshots — **30%**.

### A. Algorithm (flowchart or pseudocode)

* **Task 1 & Task 3 (30‑mark tasks)** — **Max marks 12** for this component.
* **Task 2 (40‑mark task)** — **Max marks 16** for this component.

**Descriptors across bands (all tasks):**

* *Outstanding/Excellent/Very Good/Good:* Functional, justified, adheres to standard conventions; error‑proofing; no logical errors; meets **all** requirements (Outstanding adds efficiency and value beyond requirements).
* *Pass:* Functional; most conventions; meets **most** minimum requirements.
* *Poor:* Functional and/or reverse‑engineered; some conventions; meets **some** minimum requirements.
* *Fail:* Non‑functional; little/no conventions; significant omissions or logical errors; meets few/none of requirements.

### B. Code in text (Python implementation excerpts)

* **Task 1 & Task 3** — **Max marks 9**.
* **Task 2** — **Max marks 12**.

**Descriptors across bands (all tasks):**

* *Outstanding/Excellent:* Effectively commented, succinct, efficient; uses language features productively; fully error‑proofed; no logical errors; implements algorithm exactly; meets all requirements.
* *Very Good:* Fully commented; algorithm implemented exactly; no logical errors; minimal redundancy.
* *Good:* Mostly commented; closely implements algorithm; meets most minimum requirements; may have some redundancy.
* *Pass:* Functional with some comments; partial implementation; meets some minimum requirements; significant redundancy possible.
* *Fail:* Non‑functional; missing comments or code not provided in text; syntax/logic errors; does not implement algorithm; meets few/none of requirements.

### C. Sample output / screenshots

* **Task 1 & Task 3** — **Max marks 9**.
* **Task 2** — **Max marks 12**.

**Descriptors across bands (all tasks):**

* *Outstanding:* Continuous, comprehensive samples; demonstrate interactivity; include fool‑proof input testing; meet all requirements; demonstrate testing/QA.
* *Excellent:* Comprehensive; includes invalid input tests and error messages; meets all requirements; no logical errors indicated via prompts.
* *Very Good:* Demonstrates interactivity; tests **all relevant values**; meets all requirements; prompts are appropriate, clear, and unambiguous.
* *Good:* Demonstrates interactivity; tests **most** relevant values; meets **most** minimum requirements; most prompts clear/unambiguous.
* *Pass:* Limited interactivity evidence; tests few inputs; meets **some** minimum requirements; some prompts unclear/ambiguous.
* *Fail:* Insufficient samples; interactivity/functionality not evidenced; few/no prompts shown.

---

## Submission Checklist

* [ ] Title page with required details and exact word count.
* [ ] Main body within 3,000 words (+10% allowed).
* [ ] Flowcharts and screenshots are clear without zooming.
* [ ] Code (Task 1 and Tasks 2–3) provided **in text** in the appendix.
* [ ] Python files named correctly and submitted as **separate** files.
* [ ] No Python modules imported; input validation present where applicable.
* [ ] AU Harvard referencing used; reference list included.
* [ ] Screenshots annotated/briefly explained as needed.
