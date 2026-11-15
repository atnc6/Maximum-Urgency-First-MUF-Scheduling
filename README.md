# Maximum Urgency First (MUF) — Unified RTOS Scheduler & Concurrency Suite
### شبیه‌ساز جامع الگوریتم زمان‌بندی بیشترین فوریت اول (MUF) و مجموعه مطالعات هم‌روندی سیستم‌عامل

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-brightgreen.svg)
![Architecture](https://img.shields.io/badge/Branches-8%20Research%20Modules-purple.svg)
![Course](https://img.shields.io/badge/Course-Embedded%20%26%20Real--Time%20Systems-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

[**GB English Documentation**](#english-documentation) **| [IR مستندات فارسی](#مستندات-فارسی)**

---

## 🌿 Repository Branch Architecture (Master Research Hub) / نقشه شاخه‌های پژوهشی مخزن

This repository (`Maximum-Urgency-First-MUF-Scheduling`) is organized into **8 specialized branches**, each containing a dedicated academic study, mathematical proofs, or multimedia demonstrations. The unified simulator on this main branch (`maximum_urgency_first.py`) integrates the core execution engines across these studies:

| # | Branch Name | Research Focus & Contents | Interactive CLI Module |
| :-: | :--- | :--- | :-: |
| **1** | `1-Maximum-Urgency-First-MUF-Scheduling` *(Main)* | Core Object-Oriented MUF Simulator, ASCII Gantt Engine & HTML Visual Report Generator | **Module `[1]`** |
| **2** | `2-Comprehensive-Comparative-Analysis-of-MUF-vs.-RM-and-EDF` | 10-Chapter Comparative Monograph: **MUF vs. Rate Monotonic (RM) & EDF** (Domino Effect Collapse) | **Module `[2]`** |
| **3** | `3-MUF-handwritten-gantt-chart` | Step-by-step handwritten mathematical derivations, laxity traces, and manual Gantt charts | — |
| **4** | `4-MUF-videos` | Video presentations, walkthroughs, and visual demonstrations of MUF scheduling | — |
| **5** | `5-(MUF)-Real-Time-Scheduler-Using-Semaphore,-Monitor,-and-Hybrid-Synchronization-Architectures` | 10-Chapter Study: **MUF Synchronization via Semaphore (PIP), Monitor, and Hybrid SRP Gate** (3, 5, 10 Tasks) | **Module `[3]`** |
| **6** | `6-Synchronization-Primitives-Comparative-Study-Peterson-Dekker-Semaphore-Monitor` | 8-Chapter Study: **Peterson's & Dekker's Spinlocks vs. OS Semaphores & Monitors** | **Module `[4]`** |
| **7** | `7-Readers-Writers-Comparative-Study` | 8-Chapter Study: **Readers-Writers Problem** (Reader-Pref, Fair Turnstile Sem, Monitor vs. Spinlocks) | **Module `[5]`** |
| **8** | `8-MUF-Articles` | Foundational Literature Archive: Original **MUF (1992)**, **MMUF (2005)**, and **EMUF (2012)** papers | — |

---

<a name="english-documentation"></a>
## English Documentation

### 1. Overview
**Maximum Urgency First (MUF)** is a hybrid, preemptive real-time scheduling algorithm introduced by *David B. Stewart and Pradeep K. Khosla (1991/1992)* for the Chimera II Real-Time Operating System (RTOS). MUF resolves the classical trade-off between **Rate Monotonic (RM)** under-utilization ($U_{LUB} \approx 69.31\%$) and **Earliest Deadline First (EDF)** overload collapse (the **Domino Effect**) by uniting static criticality isolation with dynamic laxity scheduling.

This repository provides a **Unified RTOS & Concurrency Benchmark Suite** (`maximum_urgency_first.py`) written in 100% pure Python 3. Through an interactive terminal menu, you can simulate core MUF scheduling, compare it side-by-side against RM and EDF, benchmark Semaphore/Monitor/Hybrid critical section synchronization, and test live multi-threaded implementations of Peterson, Dekker, and Readers-Writers locks.

---

### 2. Mathematical Principles & How MUF Works

Each process $P_i$ is characterized by Arrival Time $A_i$, Worst-Case Execution Time (Burst) $C_i$, Remaining Execution Time $R_i(t)$, Absolute Deadline $d_i$, and Static Criticality Level $K_i \in \{1 \text{ (Critical)}, 0 \text{ (Non-Critical)}\}$.

#### 2.1. Tier 1: Static Criticality Partitioning
Tasks are partitioned offline into two disjoint sets:
* **Critical Set ($K_i = 1$):** Hard real-time tasks whose combined CPU utilization satisfies $U_{crit} = \sum (C_i / T_i) \le 100\%$. Tasks in this tier strictly preempt Non-Critical tasks.
* **Non-Critical Set ($K_i = 0$):** Soft/firm real-time tasks executed during processor slack when no Critical task is ready.

#### 2.2. Tier 2: Dynamic Laxity & Urgency Evaluation
Within the same criticality tier, the scheduler dispatches the ready task with the **Maximum Urgency** (equivalent to **Minimum Dynamic Laxity**). At clock tick $t$:

$$L_i(t) = d_i - t - R_i(t)$$

$$U_i(t) = -L_i(t) = t + R_i(t) - d_i$$

* **Early Deadline Failure Detection:** The exact instant $L_i(t) < 0$ (which occurs at $t_{alert} = d_i - R_i(t) + 1$, well before $d_i$), the kernel knows the task cannot finish on time and triggers an early overload alert!
* **Anti-Thrashing Sticky Tie-Breaker:** If two tasks in the same tier reach equal laxity ($L_1(t) = L_2(t)$), MUF retains the currently running task (`Sticky = 1`) to prevent LLF laxity-tie context switch thrashing.

---

### 3. Unified Interactive CLI Menu (`maximum_urgency_first.py`)

When you run `python maximum_urgency_first.py`, the simulator presents an interactive menu covering the experimental engines across the repository's branches:

```text
Select Repository Branch / Simulation Module to Execute:
  [1] Branch 1: Core MUF Preemptive Scheduler (ASCII Gantt, Laxity Log & Custom Input)
  [2] Branch 2: Comparative Analysis — MUF vs. Rate Monotonic (RM) & EDF (Domino Collapse)
  [3] Branch 5: Synchronized MUF — Semaphore (PIP), Monitor, & Hybrid SRP (3, 5, 10 Tasks)
  [4] Branch 6: Concurrency Primitives — Peterson, Dekker, Semaphore & Monitor Benchmark
  [5] Branch 7: Readers-Writers Problem — Spinlocks vs. Fair Turnstile Sem & Monitor
  [6] Run ALL Modules (Complete Master Demonstration + Export Visual HTML Gantt Report) [Default]
```

* **Module `[1]` (Core MUF Engine):** Runs Scenario 1 (Normal Load), Scenario 2 (Transient Overload), or Custom User Input, outputting tick-by-tick laxity tables and Unicode ASCII Gantt charts.
* **Module `[2]` (MUF vs. RM & EDF):** Executes a 150% transient overload counter-example across RM, EDF, and MUF, proving how RM and EDF suffer a **0% Critical Hit Ratio** (Domino Collapse) while MUF guarantees **100% Critical Set survival (3/3 Met)** and early failure detection at $t = 2\text{s}$.
* **Module `[3]` (Synchronized MUF — Sem, Mon, Hybrid):** Evaluates shared resource contention across 3-, 5-, and 10-task workloads comparing `MUF-Sem` (Dynamic PIP), `MUF-Mon` (Mesa CondVar), and `MUF-Hybrid` (Stage-1 SRP Monitor Gate + Stage-2 Fast Semaphore).
* **Module `[4]` (Concurrency Primitives Live Benchmark):** Performs live multi-threaded verification and nanosecond latency profiling (`time.perf_counter_ns()`) of **Peterson's Spinlock**, **Dekker's Spinlock**, **OS Semaphores**, and **Monitors**.
* **Module `[5]` (Readers-Writers Live Benchmark):** Verifies concurrent shared reading ($R(t) \ge 2$) and bounded writer waiting using a **Fair Turnstile Semaphore RW-Lock** and **Monitor RW-Lock** vs. spinlock serialization.
* **Module `[6]` (Master Suite + HTML Export):** Runs all 5 modules sequentially and generates `muf_gantt_report.html` containing color-coded visual Gantt charts for MUF, RM, and EDF.

---

### 4. Sample Terminal Output (ASCII Gantt Charts)

#### 4.1. Normal Schedulable Traffic (Dynamic Laxity Preemption)
`P1(A=0, C=4, d=10, K=1)`, `P2(A=1, C=3, d=14, K=0)`, `P3(A=2, C=2, d=5, K=1)`, `P4(A=4, C=3, d=15, K=0)`

```text
  Time (t)   │  0   1   2   3   4   5   6   7   8   9  10  11 
  ───────────┼────────────────────────────────────────────────
  P1(C,d=10) │███|███|···|···|███|███|   |   |   |   |   |   |
  P3(C,d=5)  │   |   |███|███|   |   |   |   |   |   |   |   |
  P2(N,d=14) │   |···|···|···|···|···|▓▓▓|▓▓▓|▓▓▓|···|███|   |
  P4(N,d=15) │   |   |   |   |···|···|···|···|▓▓▓|▓▓▓|···|▓▓▓|
  ───────────┼────────────────────────────────────────────────
  CPU Active │ P1| P1| P3| P3| P1| P1| P2| P2| P4| P4| P2| P4|
  Run Laxity │  6|  6|  1|  1|  4|  4|  5|  5|  4|  4|  3|  3|  (Laxity = d - t - R)
```

#### 4.2. RM & EDF Domino Collapse vs. MUF Critical Set Isolation (150% Overload)
```text
  ┌──────────────────────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
  │ Evaluation Metric (Overload Case B)  │ Rate Monotonic (RM)  │ Earliest Deadl.(EDF) │ Max Urgency (MUF)    │
  ├──────────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ P1 (Crit, d=6s) Finish               │ t=9s (MISS ✗)        │ t=7s (MISS ✗)        │ t=3s (MET ✓)         │
  │ P4 (Crit, d=7s) Finish               │ t=6s (MET ✓)         │ t=9s (MISS ✗)        │ t=7s (MET ✓)         │
  │ P2 (Crit, d=8s) Finish               │ t=12s (MISS ✗)       │ t=12s (MISS ✗)       │ t=8s (MET ✓)         │
  │ P3 (NonC, d=5s) Finish [Trap!]       │ t=4s (MET ✓)         │ t=4s (MET ✓)         │ t=12s (MISS ✗)       │
  ├──────────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ Critical Set Hit Ratio (HR_crit)     │   33.3% / 0% (Fail)  │    0.0% (Domino!)    │  100.0% (3/3 Met!)   │
  │ Early Overload Failure Detection     │ None (At t=d_i)      │ None (At t=d_i)      │ t=2s (L_P3 = -1 < 0) │
  └──────────────────────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

---

### 5. Installation & Quick Start

No external dependencies are required (100% Python 3 Standard Library):

```bash
git clone https://github.com/atnc6/Maximum-Urgency-First-MUF-Scheduling.git
cd Maximum-Urgency-First-MUF-Scheduling
python maximum_urgency_first.py
```

To explore any of the dedicated research branches:
```bash
git branch -a
git checkout 2-Comprehensive-Comparative-Analysis-of-MUF-vs.-RM-and-EDF
```

---
---

<a name="مستندات-فارسی"></a>
## مستندات فارسی

### ۱. معرفی پروژه و معماری مخزن
الگوریتم **Maximum Urgency First (بیشترین فوریت اول — MUF)** یک الگوریتم زمان‌بندی ترکیبی (Hybrid) و قبضه‌کننده (Preemptive) برای سیستم‌های عامل بی‌درنگ (RTOS) است که توسط *Stewart* و *Khosla* در دانشگاه کارنگی ملون معرفی شد. این الگوریتم با ترکیب **اولویت ایستای سطح بحرانیت (Criticality Tier)** و **اولویت پویای سستی/فوریت (Laxity / Urgency)**، هم مشکل هدررفت ۳۰.۷٪ ظرفیت پردازنده در الگوریتم Rate Monotonic (RM) را برطرف می‌کند و هم مانع از وقوع فاجعه **اثر دومینو (Domino Effect)** در الگوریتم Earliest Deadline First (EDF) هنگام اضافه‌بار گذرا می‌شود.

این مخزن (`Maximum-Urgency-First-MUF-Scheduling`) به عنوان **پروژه جامع درس سیستم‌های نهفته و بی‌درنگ** در **۸ شاخه (Branch)** تخصصی سازماندهی شده است و فایل `maximum_urgency_first.py` در شاخه اصلی، موتور شبیه‌ساز یکپارچه تمامی این مباحث را در اختیار شما قرار می‌دهد.

---

### ۲. اصول ریاضی و نحوه عملکرد الگوریتم MUF

در هر تیک زمانی $t$، زمان‌بند برای هر تسک آماده $P_i$ با زمان ورود $A_i$، زمان اجرای کل $C_i$، زمان اجرای باقی‌مانده $R_i(t)$، ددلاین مطلق $d_i$ و سطح بحرانیت ایستا $K_i \in \{1 \text{ (بحرانی)}, 0 \text{ (غیربحرانی)}\}$ مقادیر زیر را محاسبه می‌کند:

$$L_i(t) = d_i - t - R_i(t) \quad \text{(Dynamic Laxity / سستی پویا)}$$

$$U_i(t) = -L_i(t) = t + R_i(t) - d_i \quad \text{(Dynamic Urgency / فوریت پویا)}$$

1. **سطح اول (جداسازی ایستای بحرانیت $K_i$):** تا زمانی که حتی یک تسک آماده در **مجموعه بحرانی ($K_i = 1$)** وجود داشته باشد، هیچ تسک غیربحرانی ($K_i = 0$) اجازه اخذ پردازنده را ندارد.
2. **سطح دوم (بیشترین فوریت پویا $U_i(t)$):** در میان تسک‌های هم‌سطح، پردازنده به تسکی اختصاص می‌یابد که **کمترین سستی ($L_i(t)$)** یا **بیشترین فوریت ($U_i(t)$)** را داشته باشد.
3. **تشخیص زودهنگام خطای ددلاین ($L_i(t) < 0$):** به محض آنکه سستی یک تسک منفی شود (در لحظه $t = d_i - R_i(t) + 1$، بسیار پیش از رسیدن به ددلاین $d_i$)، کرنل MUF متوجه عدم امکان اتمام به‌موقع تسک شده و هشدار زودهنگام صادر می‌کند.
4. **قانون Sticky Priority (مهار Laxity Tie Thrashing):** در صورت برابری سستی دو تسک هم‌سطح، تسک در حال اجرا اولویت خود را حفظ می‌کند تا از تعویض متن‌های مکرر در هر تیک ساعت جلوگیری شود.

---

### ۳. راهنمای منوی تعاملی شبیه‌ساز (`maximum_urgency_first.py`)

با اجرای دستور `python maximum_urgency_first.py` در ترمینال، منوی تعاملی زیر ظاهر می‌شود که شبیه‌سازی‌های مربوط به شاخه‌های مختلف این مخزن را اجرا می‌کند:

* **گزینه `[1]` (شاخه ۱ — شبیه‌ساز اصلی MUF):** اجرای سناریوی ۱ (بار عادی)، سناریوی ۲ (اضافه‌بار گذرا)، یا دریافت دستی تسک‌ها از کاربر همراه با رسم جدول گانت ASCII و لاگ تیک‌به‌تیک سستی.
* **گزینه `[2]` (شاخه ۲ — مقایسه MUF با RM و EDF):** اجرای سناریوی اضافه‌بار ۱۵۰٪ روی هر سه الگوریتم و نمایش شکست دومینویی EDF (نرخ موفقیت ۰٪ تسک‌های بحرانی) در برابر حفاظت ۱۰۰٪ تسک‌های بحرانی در MUF.
* **گزینه `[3]` (شاخه ۵ — همگام‌سازی ناحیه بحرانی در MUF با سمافور، مانیتور و معماری ترکیبی):** مقایسه نتایج تجربی `MUF-Sem` (مجهز به PIP پویا)، `MUF-Mon` (مانیتور Mesa) و `MUF-Hybrid` (دروازه مانیتور SRP + سمافور سریع) در مقیاس‌های ۳، ۵ و ۱۰ تسک.
* **گزینه `[4]` (شاخه ۶ — بنچمارک زنده الگوریتم‌های Peterson، Dekker، Semaphore و Monitor):** اجرای چندنخی واقعی در پایتون، اثبات صحت انحصار متقابل روی شمارنده مشترک و اندازه‌گیری زنده تأخیر نانوثانیه‌ای اخذ قفل.
* **گزینه `[5]` (شاخه ۷ — بنچمارک مسئله خوانندگان و نویسندگان Readers-Writers):** تست زنده هم‌روندی خوانندگان ($R(t) \ge 2$) با قفل منصفانه Turnstile Semaphore در مقایسه با مانیتور و قفل‌های چرخشی پترسون و دکر.
* **گزینه `[6]` (پیش‌فرض — اجرای کامل تمامی ماژول‌ها + گزارش گرافیکی HTML):** اجرای متوالی هر ۵ ماژول بالا و تولید خودکار فایل گرافیکی `muf_gantt_report.html`.

---

### ۴. نحوه دریافت و اجرای پروژه

```bash
git clone https://github.com/atnc6/Maximum-Urgency-First-MUF-Scheduling.git
cd Maximum-Urgency-First-MUF-Scheduling
python maximum_urgency_first.py
```

برای جابه‌جایی بین شاخه‌های پژوهشی (Branches) و دسترسی به فایل‌های Word/PDF هر تحقیق:
```bash
git branch -a
git checkout 5-(MUF)-Real-Time-Scheduler-Using-Semaphore,-Monitor,-and-Hybrid-Synchronization-Architectures
```

---
> **Course Project:** Embedded & Real-Time Systems — Eshragh Higher Education Institute | Developed by [@atnc6](https://github.com/atnc6)
