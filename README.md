# Foundational Literature Archive: Maximum Urgency First (MUF) & Its Evolution (MMUF, EMUF)
### آرشیو مقالات مرجع و بنیادین: الگوریتم زمان‌بندی Maximum Urgency First (MUF) و نسخه‌های توسعه‌یافته آن (MMUF و EMUF)

![Literature](https://img.shields.io/badge/Literature-Academic%20Papers-blue.svg)
![Domain](https://img.shields.io/badge/Domain-Real--Time%20%26%20Embedded%20Systems-orange.svg)
![Algorithms](https://img.shields.io/badge/Algorithms-MUF%20%7C%20MMUF%20%7C%20EMUF-brightgreen.svg)
![Language](https://img.shields.io/badge/Docs-Bilingual%20(EN%20%7C%20FA)-purple.svg)

**[🇬🇧 English Literature Guide](#english-documentation) | [🇮🇷 راهنمای فارسی مقالات](#مستندات-فارسی)**

---

## 📚 Repository Papers & Direct Downloads / لیست مقالات موجود و لینک دانلود مستقیم

This repository serves as a curated academic reference archive tracing the theoretical birth, critical critique, and algorithmic evolution of the **Maximum Urgency First (MUF)** real-time scheduling paradigm across seminal peer-reviewed publications:

| # | Year | Paper Title & Direct Link | Authors & Affiliation | Core Contribution |
| :-: | :-: | :--- | :--- | :--- |
| **1** | **1991/1992** | 📄 **[Real-Time Scheduling of Sensor-Based Control Systems](./Sensor_Based%20Control_Systems.pdf)** | **David B. Stewart, Pradeep K. Khosla**<br>*(Carnegie Mellon University — CHIMERA II RTOS)* | **Original MUF Formulation:** Unites static Criticality isolation with dynamic Laxity urgency; guarantees $100\%$ Critical Set utilization and early deadline failure detection. |
| **2** | **2005** | 📄 **[A Modified Maximum Urgency First Scheduling Algorithm for Real-Time Tasks](./A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf)** | **Vahid Salmani, Saman Taghavi Zargar, Mahmoud Naghibzadeh**<br>*(Ferdowsi University of Mashhad)* | **Modified MUF (MMUF):** Resolves critical task failure edge-cases in MUF by decoupling task *Importance* from period length and replacing LLF with **EDF** to cut context switches. |
| **3** | **2012** | 📄 **[Enhanced Maximum Urgency First Algorithm with Intelligent Laxity for Real Time Systems](./Enhanced_MUF_with_Intelligent_Laxity.pdf)** | **H. S. Behera, Naziya Raffat, Minarva Mallik**<br>*(Veer Surendra Sai University of Technology)* | **Enhanced MUF (EMUF):** Introduces **Intelligent Laxity ($IL_i$)** recalculated at every scheduling event, immediately pruning doomed processes ($IL_i < 0$) to maximize throughput and minimize TAT/WT. |

---

<a name="english-documentation"></a>
## 🇬🇧 English Documentation

### 1. Overview & Purpose of This Literature Archive
In **Hard Real-Time Operating Systems (RTOS)**, classical scheduling theory historically divided into static-priority policies like **Rate Monotonic (RM)** (predictable under overload, but capped at $\approx 69.31\%$ utilization) and dynamic-priority policies like **Earliest Deadline First (EDF)** and **Least Laxity First (LLF)** ($100\%$ utilization, but prone to catastrophic Domino failures during transient overloads). 

To document how researchers solved and iteratively refined this trade-off, this repository collects three milestone papers spanning two decades of real-time scheduling research:

---

### 2. Detailed Paper Summaries & Evolutionary Lineage

#### 📄 Paper 1: Stewart & Khosla (1991/1992) — *The Original MUF Scheduler*
* **File:** [`Sensor_Based Control_Systems.pdf`](./Sensor_Based%20Control_Systems.pdf)
* **Venue:** *Proceedings of the IEEE International Conference on Systems Engineering / IFAC Real-Time Programming (CHIMERA II RTOS)*
* **Key Architectural Concepts:**
  * Introduces **Maximum Urgency First (MUF)** as a mixed-priority scheduler combining two static priorities (**Criticality** and **User Priority**) with one dynamic priority (**inverse Laxity**).
  * Defines the **Critical Set** (tasks ordered by shortest period whose cumulative CPU utilization $\sum C_i / T_i \le 100\%$), mathematically guaranteeing that critical tasks never miss deadlines even during transient system overloads ($U > 100\%$).
  * Encodes urgency into a single $n$-bit integer (`[criticality | dynamic priority | user priority]`) for fast hardware/kernel dispatch ($28\ \mu\text{s}$ reschedule time on a $20\text{ MHz}$ M68020).
  * Introduces **three-tier deadline failure detection** and custom failure handlers.

#### 📄 Paper 2: Salmani, Zargar & Naghibzadeh (2005) — *Modified MUF (MMUF)*
* **File:** [`A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf`](./A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf)
* **Venue:** *World Academy of Science, Engineering and Technology (WASET), Vol. 9, pp. 19–23, 2005*
* **Key Architectural Concepts:**
  * **Identifies Two Flaws in Original MUF:** (1) MUF assumes shorter-period tasks are always more critical (Period-Importance Fallacy), and (2) using LLF for dynamic priority causes excessive **laxity-tie context switches** and can cause a critical task with long remaining execution to block another critical task past its deadline.
  * **Proposed Solution (MMUF):** Introduces an explicit static **Importance Parameter** to form the Critical Set without period transformation, and evaluates **MMUF-EDF** vs. **MMUF-MLLF** as the dynamic priority engine.
  * **Empirical Findings:** Demonstrates via simulation (10 and 20 periodic tasks across CPU loads $0.1$ to $1.5$) that **MMUF-EDF** significantly reduces context switch overhead ($N_{\text{MMUF}} / N_{\text{MUF}} < 1$) and decreases failed non-critical tasks during overload.

#### 📄 Paper 3: Behera, Raffat & Mallik (2012) — *Enhanced MUF (EMUF)*
* **File:** [`Enhanced_MUF_with_Intelligent_Laxity.pdf`](./Enhanced_MUF_with_Intelligent_Laxity.pdf)
* **Venue:** *International Journal of Computer Applications (IJCA), Vol. 44, No. 8, pp. 20–26, April 2012*
* **Key Architectural Concepts:**
  * **Critique of MMUF-EDF:** Scheduling strictly by earliest deadline in MMUF can still dispatch a task whose remaining burst exceeds its remaining deadline window, wasting CPU cycles on a doomed job.
  * **Proposed Solution (EMUF):** Replaces EDF with **Intelligent Laxity ($IL_i = D_i - RBT_i - \text{current\_time}$)** dynamically recomputed upon every task arrival and completion.
  * **Early Pruning & Performance Gains:** Tasks with $IL_i < 0$ are immediately terminated from the ready queue before consuming CPU time, yielding lower Average Turnaround Time (TAT), lower Average Waiting Time (WT), and higher system Throughput than both MUF and MMUF.

---

### 3. Algorithmic Evolution Comparison Table

| Feature / Dimension | MUF (Stewart & Khosla, 1991) | MMUF (Salmani et al., 2005) | EMUF (Behera et al., 2012) |
| :--- | :---: | :---: | :---: |
| **Critical Set Selection Basis** | Shortest Period ($1/T_i$) | Explicit User **Importance** | Explicit User **Importance** |
| **Dynamic Priority Engine** | Least Laxity First (LLF / MLF) | **EDF** (Recommended) or MLLF | **Intelligent Laxity ($IL_i$)** |
| **Laxity-Tie Context Switches** | High (Frequent LLF ties) | **Low** (Eliminated via EDF/Sticky) | Moderate (Evaluated at events) |
| **Negative Laxity ($IL_i < 0$) Handling** | Failure Handler Invocation | Pre-start feasibility check | **Immediate Queue Termination** |
| **Primary Optimization Goal** | Overload Isolation ($100\%$ Crit) | Context Switch & Overhead Reduction | Min Avg TAT/WT & Max Throughput |

---

### 4. Repository Structure

```text
muf-literature-archive/
├── README.md                                                     # Bilingual Literature Guide & Citations
├── Sensor_Based Control_Systems.pdf                              # [1991/92] Stewart & Khosla (Original MUF)
├── A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf        # [2005] Salmani, Zargar & Naghibzadeh (MMUF)
└── Enhanced_MUF_with_Intelligent_Laxity.pdf                      # [2012] Behera, Raffat & Mallik (EMUF)
```

---
---

<a name="مستندات-فارسی"></a>
## 🇮🇷 مستندات فارسی (راهنمای مقالات مرجع)

### ۱. معرفی و هدف این مخزن (Literature Archive)
این مخزن شامل مجموعه‌ای از مقالات مرجع و کلاسیک بین‌المللی پیرامون **الگوریتم زمان‌بندی بی‌درنگ Maximum Urgency First (MUF)** و نسخه‌های تکامل‌یافته آن (**MMUF** و **EMUF**) است. هدف از گردآوری این مقالات، مستندسازی سیر تحول تئوریک و عملی زمان‌بندهای ترکیبی (Hybrid Fixed/Dynamic Schedulers) برای مقابله با **اضافه‌بار گذرا (Transient Overload)**، کاهش **تعویض متن (Context Switch)** و تشخیص زودهنگام خطای ددلاین در سیستم‌های بی‌درنگ سخت است.

---

### ۲. معرفی و خلاصه مقالات موجود

#### 📄 مقاله اول: Stewart & Khosla (۱۹۹۱/۱۹۹۲) — *ارائه الگوریتم پایه MUF*
* **فایل مقاله:** [`Sensor_Based Control_Systems.pdf`](./Sensor_Based%20Control_Systems.pdf)
* **نویسندگان:** دیوید استوارت و پرادیپ کوسلا (دانشگاه کارنگی ملون — سیستم‌عامل بی‌درنگ CHIMERA II)
* **دستاوردهای کلیدی:**
  * معرفی الگوریتم **MUF** با ترکیب دو اولویت ایستا (**سطح بحرانیت Criticality** و **اولویت کاربر**) و یک اولویت پویا (**معکوس سستی / Laxity**).
  * تضمین **۱۰۰٪ بهره‌وری پردازنده برای مجموعه تسک‌های بحرانی (Critical Set)** حتی در شرایطی که بار کل سیستم از ۱۰۰٪ فراتر می‌رود.
  * کدگذاری بردار اولویت در یک مقدار صحیح $n$-بیتی برای کاهش سربار زمان‌بندی کرنل ($28\ \mu\text{s}$) و ارائه مکانیزم **تشخیص سه‌گانه شکست ددلاین**.

#### 📄 مقاله دوم: سلمانی، تقوی زرگر و نقیب‌زاده (۲۰۰۵) — *الگوریتم اصلاح‌شده MMUF*
* **فایل مقاله:** [`A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf`](./A_Modified_Maximum_Urgency_First_Scheduling_Algori.pdf)
* **نویسندگان:** وحید سلمانی، سامان تقوی زرگر و دکتر محمود نقیب‌زاده (دانشگاه فردوسی مشهد)
* **دستاوردهای کلیدی:**
  * **نقد الگوریتم MUF اولیه:** نشان می‌دهد که در MUF فرض می‌شود تسک با دوره تناوب کوتاه‌تر لزوماً مهم‌تر است، و همچنین استفاده از LLF در تساوی سستی‌ها باعث **تعویض متن‌های مکرر** و احتمال شکست یک تسک بحرانی می‌شود.
  * **راهکار پیشنهادی (MMUF):** جایگزینی دوره تناوب با پارامتر صریح **اهمیت (Importance)** برای تشکیل مجموعه بحرانی و استفاده از **EDF** به عنوان اولویت پویا (`MMUF-EDF`).
  * **نتایج شبیه‌سازی:** کاهش چشمگیر تعداد Context Switchها و کاهش تعداد تسک‌های غیربحرانی ناموفق در بارهای کاری سنگین ($U > 100\%$).

#### 📄 مقاله سوم: بهرا، رفعت و مالیک (۲۰۱۲) — *الگوریتم بهبودیافته EMUF با سستی هوشمند*
* **فایل مقاله:** [`Enhanced_MUF_with_Intelligent_Laxity.pdf`](./Enhanced_MUF_with_Intelligent_Laxity.pdf)
* **نویسندگان:** اچ. اس. بهرا، نازیا رفعت و میناروا مالیک (دانشگاه صنعتی VSSUT هند)
* **دستاوردهای کلیدی:**
  * معرفی معیار **سستی هوشمند ($IL_i = D_i - RBT_i - \text{current\_time}$)** که در هر رویداد ورود و اتمام فرآیند مجدداً محاسبه می‌شود.
  * حذف فوری تسک‌های دارای سستی هوشمند منفی ($IL_i < 0$) از صف آماده پیش از هدر دادن زمان CPU که منجر به کاهش **میانگین زمان گردش (TAT)**، کاهش **میانگین زمان انتظار (WT)** و افزایش **گذردهی (Throughput)** نسبت به MUF و MMUF می‌شود.

---

### ۳. جدول مقایسه سیر تکامل مقالات

| ویژگی / معیار مقایسه | مقاله اول: MUF (۱۹۹۱) | مقاله دوم: MMUF (۲۰۰۵) | مقاله سوم: EMUF (۲۰۱۲) |
| :--- | :---: | :---: | :---: |
| **معیار انتخاب مجموعه بحرانی** | کوتاه‌ترین دوره تناوب ($1/T_i$) | پارامتر صریح **اهمیت (Importance)** | پارامتر صریح **اهمیت (Importance)** |
| **الگوریتم اولویت پویا** | کمترین سستی (LLF / MLF) | **EDF** (پیشنهاد اصلی) یا MLLF | **سستی هوشمند ($IL_i$)** |
| **نرخ تعویض متن (Context Switch)** | زیاد (در تساوی‌های سستی) | **کم** (بهینه شده با EDF) | متوسط (در رویدادهای تکمیل) |
| **مدیریت سستی منفی ($IL_i < 0$)** | فراخوانی Failure Handler | بررسی امکان‌پذیری پیش از شروع | **حذف فوری از صف آماده** |
| **دستاورد اصلی پژوهش** | ایمنی در برابر اثر دومینو | کاهش سربار و تعویض متن | بهبود میانگین TAT، WT و گذردهی |

---
> **Course Project:** Operating Systems / Embedded & Real-Time Systems — Eshragh Higher Education Institute | Developed by [@atnc6](https://github.com/atnc6)