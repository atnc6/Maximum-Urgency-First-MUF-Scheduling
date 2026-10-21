# Maximum Urgency First (MUF) — Real-Time Scheduler Simulator
### شبیه‌ساز الگوریتم زمان‌بندی بیشترین فوریت اول (MUF) در سیستم‌های بی‌درنگ

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-brightgreen.svg)
![Course](https://img.shields.io/badge/Course-Embedded%20%26%20Real--Time%20Systems-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

[**GB English Documentation**](#english-documentation) **| [IR مستندات فارسی](#مستندات-فارسی)**

---

<a name="english-documentation"></a>
## English Documentation

### 1. Title & Overview
**Maximum Urgency First (MUF)** is a hybrid, preemptive real-time scheduling algorithm introduced by *David B. Stewart and Pradeep K. Khosla (1992)* for the Chimera II Real-Time Operating System. MUF combines the predictability of **fixed-priority scheduling** (like Rate Monotonic) with the high CPU utilization bound of **dynamic-priority scheduling** (like Earliest Deadline First and Least Laxity First).

This repository provides a clean, object-oriented, zero-dependency Python simulator (`maximum_urgency_first.py`) featuring `Process` and `MUFScheduler` classes, tick-by-tick timeline logging, ASCII Gantt chart visualization, and an automatic HTML visual dashboard generator.

---

### 2. Background & Motivation
Traditional real-time scheduling algorithms suffer from a fundamental trade-off:
1. **Static Priority Algorithms (e.g., Rate Monotonic - RM):** Guarantee that the highest-priority critical tasks will meet their deadlines even during transient system overload, but their guaranteed schedulable CPU utilization bound drops to $U = n(2^{1/n} - 1) \approx 69.3\%$.
2. **Pure Dynamic Priority Algorithms (e.g., EDF, LLF/LST):** Achieve up to $100\%$ CPU utilization under normal conditions. However, during a **Transient Overload** (when total requested CPU demand exceeds $100\%$), pure EDF and LLF suffer from the **Domino Effect**: a non-critical task with an imminent deadline can preempt critical system tasks, potentially causing **all** tasks (including safety-critical ones) to miss their deadlines.

**Why MUF?** Maximum Urgency First (MUF) resolves this dilemma by partitioning tasks into a **Critical Set** and a **Non-Critical Set** (fixed priority), while scheduling tasks within each set dynamically according to their **Urgency** (inverse of Laxity). Thus, MUF achieves up to $100\%$ utilization for the critical set while strictly guaranteeing that no critical task ever misses its deadline due to non-critical traffic.

---

### 3. Algorithm Principles & How It Works

Each process $P_i$ is assigned a three-part priority vector evaluated at every time tick $t$:

#### 3.1. Step 1: Criticality Partitioning (Static Priority)
Tasks are divided into two static tiers based on their `criticality` attribute:
* **Critical Set ($\text{Criticality} = 1$):** Tasks whose deadlines must never be missed even under overload. Their combined CPU utilization is bounded at $\le 100\%$.
* **Non-Critical Set ($\text{Criticality} = 0$):** Best-effort / soft real-time tasks executed only when no Critical task requires the processor.

#### 3.2. Step 2: Dynamic Laxity & Urgency Calculation
Within the same criticality tier, the scheduler selects the ready task with the **Maximum Urgency** (which corresponds to the **Minimum Laxity**). At any current time $t$, for a task $P_i$ with absolute deadline $D_i$ and remaining execution time $R_i(t)$:

$$\text{Laxity}_i(t) = D_i - t - R_i(t)$$

$$\text{Urgency}_i(t) = -\text{Laxity}_i(t) = t + R_i(t) - D_i$$

* **Physical Meaning of Laxity:** The maximum amount of time task $P_i$ can be delayed (wait in the ready queue) without missing its deadline.
* When $\text{Laxity}_i(t) = 0$, the task **must** run immediately and continuously until completion to meet its deadline.
* When $\text{Laxity}_i(t) < 0$, the deadline can no longer be met.

#### 3.3. Step 3: Preemption & Tie-Breaking Rules
* **Preemption:** MUF is strictly preemptive. At each clock tick, if a newly arrived task (or a waiting task whose laxity has shrunk) has a higher criticality or—within the same criticality class—a strictly higher urgency (smaller laxity) than the currently running task, a context switch (preemption) occurs immediately.
* **Tie-Breaking:** If two tasks share the exact same Criticality and Dynamic Laxity, ties are broken by:
  1. Earlier Absolute Deadline ($D_i$)
  2. Higher Static User Priority (`user_priority`)
  3. First-Come, First-Served (`arrival_time`, then `pid`).

---

### 4. Input & Output Parameters

#### 4.1. Input Parameters per Process
| Parameter | Symbol | Type | Description |
| :--- | :---: | :---: | :--- |
| **Process ID** | `pid` | `str` | Unique identifier of the task (e.g., `P1`, `P_C1`) |
| **Arrival Time** | $A_i$ | `int` | Time tick when the process enters the Ready Queue |
| **CPU Burst Time** | $C_i$ | `int` | Total CPU execution time required by the process |
| **Absolute Deadline** | $D_i$ | `int` | Time tick by which the process must complete execution |
| **Criticality** | $K_i$ | `int` | `1` for Critical Set (Hard Real-Time), `0` for Non-Critical Set |

#### 4.2. Calculated Output Metrics & Formulas
| Metric | Formula | Description |
| :--- | :---: | :--- |
| **Finish Time ($F_i$)** | Recorded at completion | Exact time tick when $R_i(t)$ reaches $0$ |
| **Turnaround Time ($TAT_i$)** | $TAT_i = F_i - A_i$ | Total time spent in the system from arrival to completion |
| **Waiting Time ($WT_i$)** | $WT_i = TAT_i - C_i$ | Total time spent waiting in the Ready Queue |
| **Response Time ($RT_i$)** | $RT_i = S_i - A_i$ | Time from arrival ($A_i$) until the **first** CPU allocation ($S_i$) |
| **Deadline Status** | $F_i \le D_i$ | `MET ✓` if completed on or before $D_i$; otherwise `MISSED ✗` |

---

### 5. Comparison of Real-Time Scheduling Algorithms

| Feature / Criterion | Rate Monotonic (RM) | Earliest Deadline First (EDF) | Least Laxity First (LLF / LST) | Maximum Urgency First (MUF) |
| :--- | :---: | :---: | :---: | :---: |
| **Priority Assignment** | Static (Fixed) | Dynamic | Dynamic | **Hybrid (Static + Dynamic)** |
| **Scheduling Metric** | Task Period ($T_i$) | Absolute Deadline ($D_i$) | Laxity ($D_i - t - R_i$) | **Criticality Tier + Laxity** |
| **Schedulable Utilization Bound** | $\approx 69.3\%$ | $100\%$ | $100\%$ | **$100\%$ (for Critical Set)** |
| **Overload Predictability** | High (Protects high-prio) | Poor (Domino Effect) | Poor (Domino Effect) | **High (Protects Critical Set)** |
| **Guarantees Critical Tasks in Overload?** | Yes | No | No | **Yes (100% Guaranteed)** |
| **Preemptive?** | Yes | Yes | Yes | **Yes** |

---

### 6. Sample Simulation Scenarios & Results

#### Scenario 1: Normal Schedulable Traffic
* **Input:** `P1(A=0, C=4, D=10, Crit=1)`, `P2(A=1, C=3, D=14, Crit=0)`, `P3(A=2, C=2, D=5, Crit=1)`, `P4(A=4, C=3, D=15, Crit=0)`
* **Behavior:** `P1` starts at $t=0$. At $t=2$, `P3` arrives (Critical, $\text{Laxity}=1\text{s}$) and preempts `P1` ($\text{Laxity}=6\text{s}$). Once `P3` and `P1` complete, Non-Critical tasks `P2` and `P4` execute. All deadlines are met.

```text
  Time (t)   │  0   1   2   3   4   5   6   7   8   9  10  11 
  ───────────┼────────────────────────────────────────────────
  P1(C,D=10) │███|███|···|···|███|███|   |   |   |   |   |   |
  P3(C,D=5)  │   |   |███|███|   |   |   |   |   |   |   |   |
  P2(N,D=14) │   |···|···|···|···|···|▓▓▓|▓▓▓|▓▓▓|   |   |   |
  P4(N,D=15) │   |   |   |   |···|···|···|···|···|▓▓▓|▓▓▓|▓▓▓|
  ───────────┼────────────────────────────────────────────────
  CPU Active │ P1| P1| P3| P3| P1| P1| P2| P2| P2| P4| P4| P4|
  Run Laxity │  6|  6|  1|  1|  4|  4|  5|  5|  5|  3|  3|  3|  (Laxity = D - t - Rem)
  Run Urgency│ -6| -6| -1| -1| -4| -4| -5| -5| -5| -3| -3| -3|  (Urgency = -Laxity)
```

#### Scenario 2: Transient System Overload (Proving MUF Superiority)
* **Input:** `P_C1(A=0, C=4, D=9, Crit=1)`, `P_NC1(A=0, C=3, D=4, Crit=0)`, `P_C2(A=1, C=3, D=6, Crit=1)`, `P_C3(A=3, C=2, D=8, Crit=1)`, `P_NC2(A=2, C=3, D=16, Crit=0)`
* **Behavior:** Even though `P_NC1` has the tightest deadline in the entire system ($D=4$, $\text{Laxity}=1$), MUF prevents it from preempting the Critical tasks (`P_C1`, `P_C2`, `P_C3`). Inside the Critical Set, `P_C2` ($\text{Laxity}=2$) preempts `P_C1` ($\text{Laxity}=5$) at $t=1$, and `P_C3` ($\text{Laxity}=2$) preempts `P_C1` ($\text{Laxity}=3$) at $t=4$. **All 3 Critical tasks meet their deadlines (3/3 Met)**, while overload is safely absorbed by `P_NC1`.

```text
  Time (t)   │  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14 
  ───────────┼────────────────────────────────────────────────────────────
  P_C1(C,D=9)│███|···|···|···|···|···|███|███|███|   |   |   |   |   |   |
  P_C2(C,D=6)│   |███|███|███|   |   |   |   |   |   |   |   |   |   |   |
  P_C3(C,D=8)│   |   |   |···|███|███|   |   |   |   |   |   |   |   |   |
  P_NC1(N,D=4│···|···|···|···|···|···|···|···|···|▓▓▓|▓▓▓|▓▓▓|   |   |   |
  P_NC2(N,D=1│   |   |···|···|···|···|···|···|···|···|···|···|▓▓▓|▓▓▓|▓▓▓|
  ───────────┼────────────────────────────────────────────────────────────
  CPU Active │P_C|P_C|P_C|P_C|P_C|P_C|P_C|P_C|P_C|P_N|P_N|P_N|P_N|P_N|P_N|
  Run Laxity │  5|  2|  2|  2|  2|  2|  0|  0|  0| -8| -8| -8|  1|  1|  1|
  Run Urgency│ -5| -2| -2| -2| -2| -2| +0| +0| +0| +8| +8| +8| -1| -1| -1|
```

---

### 7. Installation & Usage

No third-party packages are required. Make sure **Python 3.8+** is installed:

```bash
git clone https://github.com/YOUR_USERNAME/muf-realtime-scheduler.git
cd muf-realtime-scheduler
python maximum_urgency_first.py
```

---

### 8. Repository Structure
```text
muf-realtime-scheduler/
│
├── maximum_urgency_first.py   # Object-oriented MUF simulator (`Process` & `MUFScheduler`)
├── README.md                  # Bilingual (EN/FA) academic documentation & formulas
└── muf_gantt_report.html      # Auto-generated visual HTML Gantt chart report
```

---
---

<a name="مستندات-فارسی"></a>
## مستندات فارسی

### ۱. معرفی الگوریتم (Title & Overview)
الگوریتم **Maximum Urgency First (بیشترین فوریت اول - MUF)** یک الگوریتم زمان‌بندی ترکیبی (Hybrid) و قبضه‌کننده (Preemptive) برای سیستم‌های عامل بی‌درنگ (RTOS) است که توسط *Stewart* و *Khosla* معرفی شد. این الگوریتم مزایای **اولویت‌بندی ایستا (Static Priority)** و **اولویت‌بندی پویا (Dynamic Priority)** را با هم ترکیب می‌کند تا هم از ۱۰۰٪ ظرفیت پردازنده استفاده کند و هم اجرای تسک‌های حیاتی (Critical Tasks) را در شرایط بحرانی تضمین نماید.

---

### ۲. پیشینه و انگیزه پیدایش (Background & Motivation)
در سیستم‌های بی‌درنگ، الگوریتم‌های کلاسیک با دو چالش اساسی روبه‌رو هستند:
1. **مشکل الگوریتم‌های ایستا (مانند Rate Monotonic - RM):** با وجود اینکه در زمان اضافه‌بار (Overload) از تسک‌های با اولویت بالا محافظت می‌کنند، اما سقف بهره‌وری تضمین‌شده پردازنده در آن‌ها به حدود $69.3\%$ محدود می‌شود.
2. **مشکل الگوریتم‌های پویا (مانند EDF و LLF/LST):** در شرایط عادی تا $100\%$ ظرفیت پردازنده را پوشش می‌دهند؛ اما به محض وقوع **اضافه‌بار گذرا (Transient Overload)** دچار پدیده خطرناک **اثر دومینو (Domino Effect)** می‌شوند. یعنی یک تسک غیرحیاتی که ددلاین نزدیکی دارد، پردازنده را از تسک‌های حیاتی سیستم می‌گیرد و باعث می‌شود **تمام تسک‌های حیاتی** ددلاین خود را از دست بدهند!

**راه‌حل MUF:** الگوریتم MUF ابتدا تسک‌ها را به صورت ایستا به دو دسته **حیاتی (Critical Set)** و **غیرحیاتی (Non-Critical Set)** تفکیک می‌کند و سپس در داخل هر دسته، زمان‌بندی را به صورت پویا بر اساس **بیشترین فوریت (کمترین Laxity)** انجام می‌دهد. در نتیجه، در زمان ترافیک سنگین (Overload)، اجرای ۱۰۰٪ تسک‌های حیاتی تضمین می‌شود.

---

### ۳. اصول عملکرد الگوریتم (Algorithm Principles & How It Works)

در هر واحد زمانی (Tick) برابر با $t$، زمان‌بند `MUFScheduler` به صورت زیر تصمیم‌گیری می‌کند:

#### ۳.۱. مرحله اول: تفکیک بر اساس بحرانی بودن (Criticality)
تسک‌های موجود در صف آماده (Ready Queue) ابتدا بر اساس پارامتر `criticality` دسته‌بندی می‌شوند:
* **دسته بحرانی (Critical Set - سطح ۱):** تا زمانی که حتی یک تسک آماده در این دسته وجود داشته باشد، هیچ تسک غیرحیاتی اجازه ورود به پردازنده را ندارد.
* **دسته غیربحرانی (Non-Critical Set - سطح ۰):** تنها زمانی اجرا می‌شوند که هیچ تسک بحرانی در صف آماده نباشد.

#### ۳.۲. مرحله دوم: محاسبه پویا Laxity و Urgency
درون هر دسته، تسکی انتخاب می‌شود که **کمترین زمان شناوری (Minimum Laxity)** یا معادلاً **بیشترین فوریت (Maximum Urgency)** را داشته باشد. در لحظه $t$، اگر ددلاین تسک $D_i$ و مدت زمان اجرای باقی‌مانده آن $R_i(t)$ باشد:

$$\text{Laxity}_i(t) = D_i - t - R_i(t)$$

$$\text{Urgency}_i(t) = -\text{Laxity}_i(t) = t + R_i(t) - D_i$$

* **مفهوم Laxity (مهلت تاخیر):** نشان می‌دهد یک تسک حداکثر چند واحد زمانی دیگر می‌تواند در صف آماده معطل بماند بدون اینکه ددلاین خود را از دست بدهد.
* هرچه `Laxity` کوچکتر باشد، `Urgency` (فوریت) بزرگتر است. اگر `Laxity = 0` شود، تسک باید بلافاصله و بدون وقفه اجرا شود.

#### ۳.۳. مرحله سوم: قانون قبضه کردن (Preemption)
الگوریتم MUF کاملاً **Preemptive** است. در هر لحظه $t$، اگر تسک جدیدی وارد شود که بحرانی‌تر است یا در همان سطح بحرانی دارای فوریت بالاتر (Laxity کمتر) نسبت به تسک در حال اجراست، پردازنده بلافاصله از تسک جاری گرفته شده و به تسک فوری‌تر داده می‌شود.

---

### ۴. پارامترهای ورودی و فرمول‌های خروجی (Input & Output Parameters)

* **زمان پایان (Finish Time - $F_i$):** لحظه‌ای که زمان اجرای باقی‌مانده تسک به صفر می‌رسد.
* **زمان بازگشت (Turnaround Time - $TAT_i$):** کل زمان حضور تسک در سیستم از لحظه ورود تا پایان:
  $$TAT_i = F_i - A_i$$
* **زمان انتظار (Waiting Time - $WT_i$):** مجموع زمان‌هایی که تسک در صف Ready منتظر مانده است:
  $$WT_i = TAT_i - C_i$$
* **زمان پاسخ (Response Time - $RT_i$):** فاصله زمانی بین ورود تسک ($A_i$) تا **اولین لحظه‌ای** که پردازنده به آن اختصاص می‌یابد ($S_i$):
  $$RT_i = S_i - A_i$$

---

### ۵. جدول مقایسه الگوریتم‌های زمان‌بندی بی‌درنگ

| ویژگی / معیار مقایسه | الگوریتم RM | الگوریتم EDF | الگوریتم LLF (LST) | الگوریتم MUF (این پروژه) |
| :--- | :---: | :---: | :---: | :---: |
| **نوع اولویت‌بندی** | ایستا (ثابت) | پویا | پویا | **ترکیبی (ایستا + پویا)** |
| **معیار تصمیم‌گیری** | دوره تناوب ($T_i$) | نزدیک‌ترین ددلاین ($D_i$) | کمترین زمان شناوری (Laxity) | **دسته بحرانی + کمترین Laxity** |
| **حداکثر بهره‌وری CPU** | $\approx 69.3\%$ | $100\%$ | $100\%$ | **$100\%$ (برای تسک‌های بحرانی)** |
| **رفتار در شرایط Overload** | پایدار (حفظ اولویت بالا) | ناپایدار (اثر دومینو) | ناپایدار (اثر دومینو) | **کاملاً پایدار و قابل پیش‌بینی** |
| **تضمین تسک‌های حیاتی در ترافیک سنگین** | بله | خیر | خیر | **بله (تضمین ۱۰۰٪)** |

---

### ۶. نحوه نصب و اجرا (Installation & Usage)

این پروژه با **پایتون خالص (Pure Python 3)** نوشته شده و به هیچ کتابخانه خارجی نیاز ندارد. برای اجرا کافیست دستور زیر را در ترمینال وارد کنید:

```bash
python maximum_urgency_first.py
```

پس از اجرا، می‌توانید از منوی تعاملی یکی از گزینه‌های زیر را انتخاب کنید:
1. **گزینه ۱ (پیش‌فرض):** اجرای همزمان هر دو سناریوی تستی (سناریوی ۱: حالت عادی + سناریوی ۲: حالت Overload) و تولید گزارش گرافیکی `muf_gantt_report.html`.
2. **گزینه ۲:** اجرای فقط سناریوی ۱ (ترافیک عادی و نمایش Preemption بر اساس Laxity).
3. **گزینه ۳:** اجرای فقط سناریوی ۲ (ترافیک سنگین / Overload و اثبات حفاظت ۱۰۰٪ از تسک‌های بحرانی).
4. **گزینه ۴:** وارد کردن دستی پردازش‌ها، ددلاین‌ها و سطح بحرانی توسط کاربر.

---
> **Course Project:** Embedded & Real-Time Systems — Eshragh Higher Education Institute | Developed by [@atnc6](https://github.com/atnc6)
