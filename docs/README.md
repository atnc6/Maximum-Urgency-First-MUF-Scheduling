# Maximum Urgency First (MUF) Real-Time Scheduler & Comparative Study (MUF vs. RM & EDF)
### الگوریتم زمان‌بندی بیشترین فوریت اول MUF و پژوهش مقایسه‌ای جامع با الگوریتم‌های RM و EDF

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Dependencies](https://img.shields.io/badge/Dependencies-None%20(Pure%20Python)-brightgreen.svg)
![Course](https://img.shields.io/badge/Course-Embedded%20%26%20Real--Time%20Systems-orange.svg)
![Documentation](https://img.shields.io/badge/Docs-Bilingual%20(EN%20%7C%20FA)%20%2B%20DOCX-purple.svg)

**[🇬🇧 English Documentation](#english-documentation) | [🇮🇷 مستندات فارسی](#مستندات-فارسی)**

---

## 📄 Full Academic Research Monographs (Word Documents) / دانلود فایل‌های کامل مقاله پژوهشی
The complete 11-chapter comparative research monographs (including high-resolution charts, architectural flowcharts, mathematical proofs, pseudocode, starvation/deadlock analysis, and multiprocessor evaluations) are available in the [`docs/`](./docs/) directory:
* 📘 **[Download English Monograph (PDF)](./docs/Comparative_Analysis_of_MUF_RM_and_EDF_Real_Time_Scheduling_Algorithms_EN.pdf)** — *Comprehensive Comparative Analysis of MUF vs. RM and EDF*
* 📗 **[دانلود گزارش جامع پژوهشی به زبان فارسی (DOCX)](./docs/MUF_vs_RM_EDF_Comparative_Study_FA.docx)** — *تحلیل و مقایسه جامع الگوریتم‌های زمان‌بندی MUF، RM و EDF*

---

<a name="english-documentation"></a>
## 🇬🇧 English Documentation

### 1. Introduction & Overview
In **Hard Real-Time Operating Systems (RTOS)**, system correctness depends not only on the logical result of computation but also on the physical instant at which results are produced. Traditional real-time scheduling algorithms face a fundamental dilemma between **CPU utilization efficiency** and **overload predictability**:
* **Rate Monotonic (RM)** *(Liu & Layland, 1973)* assigns fixed priorities inversely proportional to task periods ($P_i \propto 1/T_i$). While predictable during overload, its worst-case schedulable utilization bound drops to $U_{LUB} = n(2^{1/n} - 1) \to \ln(2) \approx 69.31\%$.
* **Earliest Deadline First (EDF)** *(Horn, 1974)* dynamically schedules the task with the closest absolute deadline ($D_i$). While EDF achieves $100\%$ CPU utilization under normal loads, it suffers from the catastrophic **Domino Effect** during transient CPU overloads ($U > 100\%$), where non-critical tasks with early deadlines preempt critical tasks and cause cascading deadline failures.
* **Maximum Urgency First (MUF)** *(Stewart & Khosla, 1991)* resolves this trade-off via a **two-tier hybrid priority architecture** that combines static **Criticality Isolation** with dynamic **Laxity/Urgency** scheduling—guaranteeing $100\%$ CPU utilization for the Critical Set while completely preventing the Domino Effect.

---

### 2. Mathematical Principles & How MUF Works
At any discrete time tick $t$, for each ready process $P_i$ with Arrival Time $A_i$, CPU Burst $C_i$, Remaining Burst $R_i(t)$, Absolute Deadline $D_i$, and Static Criticality Level $K_i \in \{1 \text{ (Critical)}, 0 \text{ (Non-Critical)}\}$:

$$\text{Laxity}_i(t) = D_i - t - R_i(t)$$

$$\text{Urgency}_i(t) = -\text{Laxity}_i(t) = t + R_i(t) - D_i$$

#### Hierarchical Two-Tier Selection Policy:
1. **Tier 1 (Static Criticality Filter):** Tasks in the **Critical Set ($K_i = 1$)** strictly take precedence over tasks in the **Non-Critical Set ($K_i = 0$)**.
2. **Tier 2 (Dynamic Urgency / Minimum Laxity):** Within the same criticality tier, the scheduler dispatches the task with the **highest Urgency (minimum Laxity)**.
3. **Preemption:** If a newly arrived task has a higher `(Criticality, Urgency)` tuple than the running task, the running task is immediately preempted.

---

### 3. Architectural Features & Critical Evaluation (Critique)

#### 3.1. Key Features
* **RM:** $O(1)$ hardware bitmap scheduling overhead; deterministic fixed-priority isolation; optimal among static-priority policies.
* **EDF:** $100\%$ uniprocessor schedulable utilization; minimal context switches under feasible loads ($U \le 100\%$).
* **MUF:** Guarantees $100\%$ utilization for critical tasks; provides **Early Deadline Failure Detection** the exact instant $\text{Laxity}_i(t) < 0$ (at $t = D_i - R_i(t)$, well before the deadline $D_i$ expires!).

#### 3.2. Critical Limitations (Critique)
* **Critique of RM (Period-Importance Fallacy):** RM blindly equates importance with execution frequency ($1/T_i$). A trivial high-frequency task ($T_1 = 5\text{ms}$) preempts a life-critical safety monitor with a longer period ($T_2 = 50\text{ms}$).
* **Critique of EDF (Domino Effect Collapse):** During transient overload, EDF prioritizes tasks whose deadlines are closest (or already missed), stealing CPU cycles from subsequent tasks and causing a cascading failure across all tasks.
* **Critique of MUF/LLF (Laxity Tie Thrashing):** When two tasks in the same criticality tier reach equal laxity ($L_1(t) = L_2(t)$), running $P_1$ for 1 tick keeps $L_1$ constant while $L_2$ decreases by 1, causing alternating preemptions at every clock tick unless non-preemptive tie-breaking is enforced.

---

### 4. Formal Kernel Pseudocode & Decision Flowchart

#### 4.1. MUF Preemptive Kernel Pseudocode
```text
PROCEDURE MUF_Schedule_Tick(Ready_Queue, Running_Task, current_time):
    IF Ready_Queue IS EMPTY THEN RETURN IDLE
    FOR EACH task IN Ready_Queue DO
        task.Laxity  <- task.Deadline - current_time - task.Remaining_Burst
        task.Urgency <- -task.Laxity
        IF task.Laxity < 0 AND task.Criticality == 0 THEN
            Raise_Early_Overload_Alert(task)   // Early failure detection before D_i
        END IF
    END FOR
    // Two-Tier Selection: 1. Max Criticality, 2. Max Urgency (-Laxity), 3. Min Arrival
    Selected <- ARGMAX_{task IN Ready_Queue} (task.Criticality, task.Urgency, -task.Arrival, -task.PID)
    IF Running_Task != NULL AND Selected != Running_Task THEN
        Preempt_And_Context_Switch(Running_Task, Selected)
    END IF
    Execute_One_Tick(Selected)
    RETURN Selected
END PROCEDURE
```

#### 4.2. Comparative Decision Flowchart
```text
                   ┌──────────────────────────────────────────────┐
                   │ RTOS Timer Tick (t) / Update Ready Queue (Q) │
                   └──────────────────────┬───────────────────────┘
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                               ▼                               ▼
┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
│  Rate Monotonic   │           │     EDF Policy    │           │    MUF Policy     │
│ Prio = 1/Period_i │           │ Prio = 1/Deadln_i │           │ Tier 1: Max Crit  │
└─────────┬─────────┘           └─────────┬─────────┘           └─────────┬─────────┘
          │                               │                               ▼
          │                               │                     ┌───────────────────┐
          │                               │                     │ Tier 2: In Q_crit │
          │                               │                     │ L_i = D_i - t - R │
          │                               │                     │ Pick min(L_i)     │
          └───────────────────────────────┼───────────────────────────────┘
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │ If Selected != Running -> Preempt & Dispatch │
                   └──────────────────────────────────────────────┘
```

---

### 5. Starvation, Deadlock & Multiprocessing Analysis

* **Starvation (Indefinite Postponement):**
  * **RM:** High-period tasks starve indefinitely if short-period tasks consume $100\%$ CPU.
  * **EDF:** Free of permanent starvation because $(D_i - t)$ decreases monotonically for waiting tasks, but this exact aging causes the Domino Effect in overload.
  * **MUF:** **Zero starvation within the same criticality tier**—because a running task's laxity remains constant ($\Delta L_{run} = 0$) while a waiting task's laxity shrinks by $1$ per tick ($\Delta L_{wait} = -1$). During severe overload, Non-Critical tasks ($K=0$) are intentionally deferred to save Critical tasks; starvation is mitigated via **Priority Aging** or a **Constant Bandwidth Server (CBS)**.
* **Deadlock & Synchronization (PIP / PCP / SRP):**
  * When tasks share mutexes (`R1`, `R2`), circular wait and unbounded **Priority Inversion** can occur.
  * MUF integrates with **Two-Tier Priority Inheritance Protocol (PIP)** (where a low-criticality lock holder inherits both $K_H$ and $\text{Urgency}_H$ of a blocked critical task) and **Baker's Stack Resource Policy (SRP)** (using dynamic preemption ceilings to guarantee **complete deadlock freedom** and at most 1 blocking period per job).
* **Multiprocessing (Multicore SMP):**
  * Under **Global Scheduling (G-RM / G-EDF / G-MUF)** on $m$ cores, **Dhall's Effect (1978)** causes deadline misses even at total utilization $U \approx 1.01$, alongside severe cache migration penalties during laxity ties.
  * **Criticality-Partitioned MUF (CP-MUF)** pins Critical Set tasks onto dedicated cores (achieving $100\%$ utilization per critical core with zero migration overhead) while scheduling Non-Critical tasks across global slack cycles.

---

### 6. Master Comparative Synthesis Table (RM vs. EDF vs. LLF vs. MUF)

| Evaluation Dimension | Rate Monotonic (RM) | Earliest Deadline First (EDF) | Least Laxity First (LLF) | Maximum Urgency First (MUF) |
| :--- | :---: | :---: | :---: | :---: |
| **Priority Assignment** | Static ($1 / T_i$) | Dynamic ($\min D_i$) | Dynamic ($\min \text{Laxity}_i$) | **Hybrid (Static Crit + Dynamic Laxity)** |
| **Uniprocessor Util. Bound** | $n(2^{1/n}-1) \approx 69.31\%$ | $100\%$ | $100\%$ | **$100\%$ (for Critical Set)** |
| **Overload Behavior** | Predictable (Long $T_i$ fails) | Catastrophic (Domino Effect) | Catastrophic (Domino + Thrashing) | **Predictable (100% Critical Protected)** |
| **Early Failure Detection** | No (at $t = D_i$) | No (at $t = D_i$) | Yes ($\text{Laxity}_i < 0$) | **Yes ($\text{Laxity}_i < 0$ before $D_i$)** |
| **Intra-Tier Starvation** | High for large $T_i$ | None (causes Domino) | None | **None ($\Delta L_{wait} = -1$ per tick)** |
| **Deadlock Prevention** | PCP / PIP | SRP / Dynamic PIP | SRP / Dynamic PIP | **Hybrid SRP / Two-Tier PIP** |
| **Kernel Dispatch Overhead** | $O(1)$ | $O(\log n)$ | $O(n)$ | **$O(n)$** |
| **Multicore (SMP) Paradigm** | Partitioned RM (P-RM) | Global/Part. EDF | Global/Part. LLF | **Criticality-Partitioned MUF (CP-MUF)** |

---

### 7. Comparative Overload Gantt Chart (RM & EDF vs. MUF)
Consider the Overload Benchmark (`Scenario 2` in `maximum_urgency_first.py`):
* `P1 (T1)`: Arrival=0, Burst=3, Deadline=6, **Critical (K=1)**
* `P2 (T2)`: Arrival=1, Burst=3, Deadline=8, **Critical (K=1)**
* `P3 (T3)`: Arrival=0, Burst=4, Deadline=5, **Non-Critical (K=0)** *(Early Deadline Trap!)*
* `P4 (T4)`: Arrival=2, Burst=2, Deadline=7, **Critical (K=1)**

```text
  [RM & EDF Schedule] -> Non-Critical P3 runs first (D=5), causing ALL 3 CRITICAL TASKS to MISS deadlines!
  Time (t) │ 0..1 │ 1..2 │ 2..3 │ 3..4 │ 4..5 │ 5..6 │ 6..7 │ 7..8 │ 8..9 │ 9..10│10..11│11..12│ Outcome
  ─────────┼──────┴──────┴──────┴──────┼──────┴──────┴──────┼──────┴──────┼──────┴──────┴──────┼────────
  CPU Core │     P3 (Non-Crit, D=5)    │  P1 (Crit, D=6)    │ P4(Crit,D=7)│   P2 (Crit, D=8)   │ 0% Crit Met!
  Status   │ P3 finishes at t=4 (MET)  │ P1 finishes t=7(X) │ P4 t=9 (X)  │ P2 finishes t=12(X)│ Domino Collapse!

  [MUF Schedule] -> Critical Set (P1, P4, P2) isolated & scheduled by Urgency; 100% Critical Tasks MET!
  Time (t) │ 0..1 │ 1..2 │ 2..3 │ 3..4 │ 4..5 │ 5..6 │ 6..7 │ 7..8 │ 8..9 │ 9..10│10..11│11..12│ Outcome
  ─────────┼──────┴──────┴──────┼──────┴──────┼──────┴──────┴──────┼──────┴──────┴──────┴──────┼────────
  CPU Core │   P1 (Crit, D=6)   │P4 (Crit,D=7)│   P2 (Crit, D=8)   │     P3 (Non-Crit, D=5)    │ 100% Crit Met!
  Status   │ P1 finishes t=3(OK)│ P4 t=5 (OK) │ P2 finishes t=8(OK)│ P3 isolated miss at t=12  │ Optimal Protection!
```

---

### 8. Installation, Usage & Repository Structure

```bash
git clone [https://github.com/YOUR_USERNAME/muf-realtime-scheduler.git](https://github.com/YOUR_USERNAME/muf-realtime-scheduler.git)
cd muf-realtime-scheduler
python maximum_urgency_first.py
```

```text
muf-realtime-scheduler/
├── maximum_urgency_first.py                    # Object-Oriented MUF Simulator & ASCII Gantt Engine
├── muf_gantt_report.html                       # Auto-generated Graphic HTML Gantt Chart Report
├── README.md                                   # Bilingual Documentation & Comparative Study Summary
└── docs/
    ├── MUF_vs_RM_EDF_Comparative_Study_EN.docx # Full 11-Chapter English Research Monograph (DOCX)
    └── MUF_vs_RM_EDF_Comparative_Study_FA.docx # Full 11-Chapter Persian Research Monograph (DOCX)
```

---
---

<a name="مستندات-فارسی"></a>
## 🇮🇷 مستندات فارسی

### ۱. مقدمه و معرفی پژوهش (Introduction)
در **سیستم‌های نهفته و بی‌درنگ (Embedded and Real-Time Systems)**، درستی عملکرد سیستم تنها به صحت منطقی محاسبات وابسته نیست، بلکه به **زمان تحویل خروجی پیش از فرارسیدن ددلاین (Deadline)** وابسته است. الگوریتم‌های زمان‌بندی کلاسیک با یک تضاد ذاتی میان **بهره‌وری پردازنده (CPU Utilization)** و **مقاومت در برابر اضافه‌بار (Overload Resilience)** روبرو هستند:
* **الگوریتم Rate Monotonic (RM):** اولویت‌ها را به صورت ایستا و بر اساس عکس دوره تناوب ($1/T_i$) تعیین می‌کند. اگرچه در زمان اضافه‌بار رفتاری قابل پیش‌بینی دارد، اما در بدترین حالت تنها تا **۶۹.۳۱٪ ($\ln 2$)** از ظرفیت پردازنده را تضمین می‌کند و تا ۳۰.۷٪ قدرت سخت‌افزار بلااستفاده می‌ماند.
* **الگوریتم Earliest Deadline First (EDF):** اولویت را به صورت پویا به تسکی می‌دهد که نزدیک‌ترین ددلاین مطلق ($D_i$) را دارد. EDF در شرایط عادی تا **۱۰۰٪ ظرفیت پردازنده** را پوشش می‌دهد، اما به محض وقوع **اضافه‌بار موقت (Transient Overload)**، دچار پدیده فاجعه‌بار **اثر دومینو (Domino Effect)** می‌شود؛ یعنی یک تسک غیرحیاتی با ددلاین نزدیک، پردازنده را تصاحب کرده و باعث سوختن زنجیره‌ای ددلاین تمامی تسک‌های حیاتی سیستم می‌گردد.
* **الگوریتم Maximum Urgency First (MUF):** که توسط *Stewart* و *Khosla* (۱۹۹۱) معرفی شد، با ترکیب هوشمند **اولویت ایستای سطح بحرانی (Criticality)** و **اولویت پویای فوریت (Urgency / Laxity)**، هم بهره‌وری ۱۰۰٪ را برای تسک‌های حیاتی فراهم می‌سازد و هم وقوع اثر دومینو را به طور کامل ریشه‌کن می‌کند.

---

### ۲. اصول ریاضی و نحوه عملکرد الگوریتم MUF
در هر تیک زمانی $t$، برای هر فرآیند آماده $P_i$ با زمان ورود $A_i$، زمان اجرای کل $C_i$، زمان اجرای باقی‌مانده $R_i(t)$، ددلاین مطلق $D_i$ و سطح بحرانی $K_i \in \{1 \text{ (حیاتی)}, 0 \text{ (غیرحیاتی)}\}$:

$$\text{Laxity}_i(t) = D_i - t - R_i(t)$$

$$\text{Urgency}_i(t) = -\text{Laxity}_i(t) = t + R_i(t) - D_i$$

* **فیلتر مرحله اول (سطح بحرانی ایستا - Criticality):** زمان‌بند ابتدا تنها تسک‌های آماده در **دسته بحرانی ($K_i = 1$)** را بررسی می‌کند. تا زمانی که حتی یک تسک حیاتی در صف آماده وجود دارد، تسک‌های عادی ($K_i = 0$) اجازه تصاحب پردازنده را ندارند.
* **فیلتر مرحله دوم (بیشترین فوریت پویا - Maximum Urgency):** در میان تسک‌های هم‌سطح، پردازنده به تسکی داده می‌شود که **کمترین مهلت آزاد (Laxity)** یا **بیشترین فوریت (Urgency)** را داشته باشد.

---

### ۳. ویژگی‌ها و بررسی نقدی الگوریتم‌ها (Features & Critique)

#### ۳.۱. ویژگی‌های برجسته (Features)
* **ویژگی RM:** پیاده‌سازی فوق‌سریع با پیچیدگی $O(1)$ در کرنل؛ عدم تأثیرپذیری تسک‌های دوره کوتاه از اضافه‌بار تسک‌های دوره بلند.
* **ویژگی EDF:** بهینگی مطلق روی تک‌پردازنده (بهره‌وری ۱۰۰٪) و کمترین تعداد تعویض زمینه (Context Switch) در بارهای مجاز.
* **ویژگی طلایی MUF (تشخیص زودهنگام خطا - Early Failure Detection):** برخلاف EDF که تنها در لحظه انقضای ددلاین ($t = D_i$) متوجه سوختن آن می‌شود، در MUF به محض اینکه $\text{Laxity}_i(t) < 0$ شود (یعنی در لحظه $t = D_i - R_i(t)$ و بسیار پیش از رسیدن به ددلاین)، کرنل متوجه عدم امکان اتمام به موقع تسک شده و می‌تواند بلافاصله تسک غیرحیاتی را متوقف کند یا روال جایگزین را فراخوانی نماید.

#### ۳.۲. بررسی نقدی و نقاط ضعف (Critique)
* **نقد الگوریتم RM:** یکسان فرض کردن «فرکانس اجرا» با «اهمیت تسک». یک تسک کم‌اهمیت با دوره تناوب کوتاه (مثلاً چشمک‌زن LED هر ۵ میلی‌ثانیه) اولویت بالاتری نسبت به تسک حیاتی کنترل فشار راکتور با دوره تناوب ۵۰ میلی‌ثانیه دریافت می‌کند!
* **نقد الگوریتم EDF:** آسیب‌پذیری شدید در برابر اضافه‌بار (Overload) و سقوط نرخ موفقیت کل سیستم به نزدیک صفر بر اثر **اثر دومینو (Domino Effect)**.
* **نقد الگوریتم MUF و LLF (پدیده Laxity Thrashing):** هنگامی که دو تسک هم‌سطح دارای Laxity برابر می‌شوند، اجرای یکی از آن‌ها باعث کاهش Laxity تسک منتظر در ثانیه بعد شده و در صورت عدم استفاده از قانون Tie-Breaking غیرقبضه‌کردنی، در هر تیک ساعت تعویض زمینه مکرر رخ می‌دهد.

---

### ۴. تحلیل گرسنگی (Starvation)، بن‌بست (Deadlock) و چندپردازنده‌ای (Multiprocessing)

* **تحلیل گرسنگی (Starvation):**
  * در **RM**، تسک‌های دارای دوره تناوب بلند در بارهای بالا دچار گرسنگی دائمی می‌شوند.
  * در **MUF**، در درون یک سطح بحرانی یکسان، **وقوع گرسنگی از نظر ریاضی غیرممکن است**؛ زیرا در هر ثانیه اجرا، Laxity تسک در حال اجرا ثابت می‌ماند ($\Delta L_{run} = 0$)، اما Laxity تسک منتظر در صف ۱ واحد کاهش و فوریت آن ۱ واحد افزایش می‌یابد ($\Delta L_{wait} = -1$). برای جلوگیری از گرسنگی طولانی‌مدت تسک‌های غیربحرانی در زمان ترافیک سنگین، از تکنیک **سالخوردگی اولویت (Priority Aging)** یا **سرور رزرو پهنای باند (CBS)** استفاده می‌شود.
* **تحلیل بن‌بست (Deadlock) و وارونگی اولویت:**
  * در صورت اشتراک منابع و قفل‌ها (Mutex)، هر سه الگوریتم نیازمند پروتکل‌های همگام‌سازی هستند. ترکیب MUF با **پروتکل وراثت اولویت دو سطحی (PIP)** مانع از وارونگی اولویت می‌شود و ترکیب آن با **سیاست منابع پشته (Stack Resource Policy - SRP)** با تعریف سقف قبضه‌کردن پویا، **عدم وقوع بن‌بست (Deadlock Freedom)** را به صورت ۱۰۰٪ تضمین کرده و زمان انسداد هر تسک را به حداکثر یک ناحیه بحرانی محدود می‌سازد.
* **پردازش چندگانه (Multiprocessing / Multicore SMP):**
  * در زمان‌بندی سراسری (**Global RM / Global EDF / Global MUF**) روی $m$ هسته پردازشی، پدیده اثبات‌شده **اثر دال (Dhall's Effect)** باعث می‌شود حتی در بار کل $U \approx 1.01$ ددلاین‌ها بسوزند و مهاجرت مداوم تسک‌ها بین هسته‌ها باعث تخریب حافظه کش (Cache Thrashing) شود.
  * بهترین معماری چندپردازنده‌ای برای MUF، روش **افرازبندی مبتنی بر سطح بحرانی (Criticality-Partitioned MUF)** است که تسک‌های حیاتی را روی هسته‌های اختصاصی مقید می‌کند (با تضمین ۱۰۰٪ بهره‌وری و صفر بودن هزینه مهاجرت) و تسک‌های عادی را در زمان‌های آزاد سایر هسته‌ها اجرا می‌نماید.

---

### ۵. جدول جامع مقایسه‌ای (RM ، EDF ، LLF و MUF)

| معیار مقایسه | الگوریتم RM | الگوریتم EDF | الگوریتم LLF (LST) | الگوریتم MUF (پروژه حاضر) |
| :--- | :---: | :---: | :---: | :---: |
| **مبنای تعیین اولویت** | ایستا ($1 / T_i$) | پویا ($\min D_i$) | پویا ($\min \text{Laxity}_i$) | **ترکیبی (Criticality ایستا + Laxity پویا)** |
| **سقف بهره‌وری تک‌پردازنده** | $\approx 69.31\%$ | $100\%$ | $100\%$ | **$100\%$ برای دسته بحرانی** |
| **رفتار در زمان اضافه‌بار (Overload)** | قابل پیش‌بینی | فاجعه‌بار (اثر دومینو) | فاجعه‌بار (دومینو + نوسان) | **کاملاً ایمن (حفظ ۱۰۰٪ تسک‌های حیاتی)** |
| **تشخیص زودهنگام خطای ددلاین** | خیر (در لحظه $D_i$) | خیر (در لحظه $D_i$) | بله ($\text{Laxity}_i < 0$) | **بله ($\text{Laxity}_i < 0$ پیش از $D_i$)** |
| **گرسنگی درون‌سطحی** | بالا برای $T_i$ بزرگ | ندارد (عامل دومینو) | ندارد | **ندارد (افزایش خطی فوریت در انتظار)** |
| **مکانیزم ضد بن‌بست (Deadlock)** | پروتکل PCP / PIP | پروتکل SRP / PIP | پروتکل SRP / PIP | **پروتکل ترکیبی SRP / PIP دو سطحی** |
| **پیچیدگی زمانی انتخاب در کرنل** | $O(1)$ | $O(\log n)$ | $O(n)$ | **$O(n)$** |
| **معماری بهینه چندپردازنده‌ای** | افرازبندی P-RM | سراسری/افراز EDF | سراسری/افراز LLF | **افرازبندی بحرانی (CP-MUF)** |

---

### ۶. راهنمای دانلود گزارش‌های کامل Word و نحوه اجرای کد
تمامی فصول ۱۱گانه این تحقیق به همراه نمودارهای گرافیکی، فلوچارت، شبهکد و جداول کامل در پوشه [`docs/`](./docs/) قرار داده شده‌اند:
* 📘 **[نسخه کامل انگلیسی (MUF_vs_RM_EDF_Comparative_Study_EN.docx)](./docs/MUF_vs_RM_EDF_Comparative_Study_EN.docx)**
* 📗 **[نسخه کامل فارسی (MUF_vs_RM_EDF_Comparative_Study_FA.docx)](./docs/MUF_vs_RM_EDF_Comparative_Study_FA.docx)**

برای اجرای شبیه‌ساز پایتون در ترمینال:
```bash
python maximum_urgency_first.py
```

---
> **Course Project:** Embedded & Real-Time Systems — Eshragh Higher Education Institute | Developed by [@atnc6](https://github.com/atnc6)
