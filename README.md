# Readers-Writers Synchronization Problem vs. Semaphore, Monitor, Dekker & Peterson Algorithms

### تحلیل و مقایسه جامع مسئله خوانندگان و نویسندگان (Readers-Writers) با الگوریتم‌های سمافور، مانیتور، دکر و پترسون

[**GB English Documentation**](#english-documentation) **| [IR مستندات فارسی](#مستندات-فارسی)**

## 📄 Academic Research Monographs (PDF Documents) / دانلود فایل‌های کامل مقاله پژوهشی (نسخه PDF)

The complete 8-chapter comparative research monographs (including asymmetric shared-exclusive safety invariants, Dijkstra's three criteria, Reader-Preference vs. Fair Turnstile Semaphore solutions, Monitor condition broadcasts, architectural flowcharts, and multi-threaded benchmarks) are available for download:

* 📘 [**Download English Monograph (PDF)**](./Readers_Writers_Comparative_Study_EN.pdf) — *Comprehensive Comparative Analysis of the Readers-Writers Synchronization Problem vs. Semaphore, Monitor, Dekker, and Peterson Algorithms*
* 📗 [**دانلود گزارش جامع پژوهشی به زبان فارسی (PDF)**](./Readers_Writers_Comparative_Study_FA.pdf) — *تحلیل و مقایسه جامع مسئله همگام‌سازی خوانندگان و نویسندگان (Readers-Writers) با الگوریتم‌های Semaphore، Monitor، Dekker و Peterson*

---

<a name="english-documentation"></a>
## English Documentation

### 1. Introduction & Asymmetric Concurrency Semantics
In operating systems, file systems, and concurrent database engines, shared data structures are accessed by two distinct classes of threads:
* **Readers ($R(t) \ge 0$):** Non-destructive threads that only inspect shared state without mutating it.
* **Writers ($W(t) \in \{0, 1\}$):** State-mutating threads that require strict exclusive access.

Unlike classical mutual exclusion primitives (which enforce $R(t) + W(t) \le 1$ and serialize concurrent reads), the **Readers-Writers Problem** *(Courtois, Heymans, and Parnas, 1971)* maximizes read parallelism while guaranteeing write exclusivity:

$$(W(t) \le 1) \quad \text{AND} \quad (W(t) \cdot R(t) == 0)$$

As formalized by **Edsger Dijkstra (1965)**, any valid synchronization solution must balance three core criteria:
1. **Mutual Exclusion (Asymmetric Safety):** Writers exclude all other threads (both Readers and Writers), while multiple Readers execute concurrently.
2. **Progress (Liveness / Deadlock Freedom):** If the resource is idle ($R(t)=0, W(t)=0$), entry selection cannot be postponed indefinitely.
3. **Bounded Waiting (Fairness / Starvation Freedom):** Neither waiting Writers nor waiting Readers may suffer indefinite postponement.

---

### 2. Comparative Architectural Overview

```text
       ┌────────────────────────────────────────────────────────────────────────┐
       │          Readers-Writers vs. Classical Synchronization Models          │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │
             ┌─────────────────────────────┴─────────────────────────────┐
             ▼                                                           ▼
┌──────────────────────────┐                               ┌──────────────────────────┐
│  Asymmetric RW-Locks     │                               │  Symmetric Spinlocks     │
│  (Shared Read/Excl Write)│                               │  (Strict 1-by-1 Excl.)   │
└────────────┬─────────────┘                               └────────────┬─────────────┘
             │                                                           │
     ┌───────┴───────┐                                           ┌───────┴───────┐
     ▼               ▼                                           ▼               ▼
┌─────────┐     ┌─────────┐                                 ┌─────────┐     ┌─────────┐
│Semaphore│     │ Monitor │                                 │ Peterson│     │ Dekker  │
│Turnstile│     │CondVars │                                 │ (1981)  │     │ (1965)  │
└─────────┘     └─────────┘                                 └─────────┘     └─────────┘
```

#### 2.1. Pure Mutual Exclusion Baselines: Peterson (1981) & Dekker (1965)
* **Mechanics:** Software-only busy-waiting spinlocks operating in user space (`flag[2]` and `turn` in Peterson; conditional intent back-off in Dekker).
* **Why They Fail Readers-Writers:**
  1. **Zero Read Parallelism:** Enforces strict mutual exclusion even among non-destructive Readers, collapsing read throughput from $O(N)$ to $O(1)$.
  2. **Strict $N = 2$ Limit:** Cannot scale to arbitrary $N$ threads without complex Filter Locks or Tournament Trees.
  3. **100% CPU Burn:** Spinning threads waste an entire processor core during long disk/database writes and require explicit hardware **Memory Fences** (`mfence` / `dmb`).

#### 2.2. Semaphore-Based Readers-Writers (Reader-Preference vs. Fair Turnstile)
* **First RW Solution (Reader-Preference):** Uses `mutex` to guard `read_count` and `rw_mutex` to block Writers when `read_count >= 1`. Maximizes read throughput, but violates **Bounded Waiting** by causing indefinite **Writer Starvation** under heavy read streams.
* **Starvation-Free Fair Turnstile Solution:** Introduces a third FIFO semaphore (`turnstile = 1`). When a Writer arrives and executes `P(turnstile)`, incoming Readers queue behind the turnstile until active Readers drain and the Writer completes.

#### 2.3. Monitor-Based Readers-Writers (Hoare vs. Mesa Condition Variables)
* **Design:** Encapsulates `active_readers`, `waiting_writers`, `writing`, and Condition Variables (`can_read`, `can_write`) inside a modular class (`StartRead()`, `EndRead()`, `StartWrite()`, `EndWrite()`).
* **Signaling Advantage:** Upon `EndWrite()`, `can_read.broadcast()` (`notifyAll`) wakes all sleeping Readers simultaneously under Mesa semantics (`while` predicate re-testing), eliminating manual `P()`/`V()` ordering deadlocks.

---

### 3. Master Comparative Synthesis Matrix

| Evaluation Criterion | 1. Peterson's Algorithm | 2. Dekker's Algorithm | 3. Reader-Pref Sem RW | 4. Fair Turnstile Sem RW | 5. Monitor RW-Lock |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Access Symmetry** | Symmetric (Excl. Only) | Symmetric (Excl. Only) | **Asymmetric (RW)** | **Asymmetric (RW)** | **Asymmetric (RW)** |
| **1. Mutual Exclusion** | Proven ($N=2$) | Proven ($N=2$) | Strict Writer Excl. | Strict Writer Excl. | Strict Writer Excl. |
| **2. Progress (Deadlock-Free)** | Guaranteed (`turn`) | Guaranteed (Back-off) | Guaranteed | Guaranteed (Turnstile) | Guaranteed (Encaps.) |
| **3. Bounded Waiting** | Bounded ($\le 1$ CS) | Bounded ($\le 1$ CS) | **VIOLATED (Writer Starves)** | **STRICTLY BOUNDED** | **STRICTLY BOUNDED** |
| **Concurrent Readers** | No (Serialized) | No (Serialized) | **Yes ($N$ Readers)** | **Yes ($N$ Readers)** | **Yes (Broadcast)** |
| **CPU State While Waiting** | Busy-Wait (100% CPU) | Busy-Wait (100% CPU) | **OS Sleep (0% CPU)** | **OS Sleep (0% CPU)** | **CondVar Sleep (0%)** |
| **Thread Scalability** | Strictly $N = 2$ | Strictly $N = 2$ | Arbitrary $N$ | Arbitrary $N$ | Arbitrary $N$ |
| **Implementation Safety** | Needs Memory Fences | Needs 2 Fences | Prone to $P/V$ bugs | High (3 Semaphores) | **Highest (OOP)** |

---

### 4. Empirical Performance Benchmarks Summary
Evaluated over $N = 10,000$ operations in `readers_writers_benchmark.py`:
* **Linear Read Throughput Scaling:** Semaphore and Monitor RW-Locks scale read throughput linearly from $96\text{ kOps/s}$ (1 Reader) to $1,340\text{ kOps/s}$ (16 Readers) — a **$13.9\times$ speedup** — whereas Peterson and Dekker remain flat at $\sim 90\text{ kOps/s}$ due to read serialization.
* **Writer Starvation Mitigation:** Under a $90\%$ read workload, Reader-Preference Semaphore spikes maximum Writer wait latency to **$480.0\text{ ms}$**, whereas Fair Turnstile Semaphore (**$14.5\text{ ms}$**) and Writer-Priority Monitor (**$8.2\text{ ms}$**) enforce strict Bounded Waiting.
* **CPU Utilization:** Peterson and Dekker burn **$100.0\%$** of a CPU core while waiting; Semaphore and Monitor drop waiting CPU overhead to **$3.2\%$** and **$4.1\%$** via kernel sleep queues.

---
---

<a name="مستندات-فارسی"></a>
## مستندات فارسی

### ۱. مقدمه و هم‌روندی نامتقارن در مسئله خوانندگان و نویسندگان
در سیستم‌های عامل، سیستم‌های فایل و موتورهای پایگاه داده، داده‌های مشترک توسط دو گروه متفاوت از نخ‌ها مورد دسترسی قرار می‌گیرند:
* **خوانندگان ($R(t) \ge 0$):** نخ‌های غیرمخربی که صرفاً داده‌های مشترک را بدون تغییر دادن می‌خوانند.
* **نویسندگان ($W(t) \in \{0, 1\}$):** نخ‌های تغییر‌دهنده وضعیت که نیازمند دسترسی انحصاری کامل هستند.

برخلاف الگوریتم‌های کلاسیک انحصار متقابل (که شرط $R(t) + W(t) \le 1$ را اعمال کرده و خوانندگان را سریال‌سازی می‌کنند)، **مسئله خوانندگان و نویسندگان (Readers-Writers Problem)** *(Courtois, Heymans, and Parnas, 1971)* موازی‌سازی خواندن را بیشینه کرده و هم‌زمان انحصار نوشتن را تضمین می‌کند:

$$(W(t) \le 1) \quad \text{AND} \quad (W(t) \cdot R(t) == 0)$$

بر اساس معیارهای بنیادین **ادسخر دایکسترا (۱۹۶۵)**، هر راهکار همگام‌سازی معتبر باید سه شرط زیر را برآورده سازد:
1. **انحصار متقابل (Mutual Exclusion):** نویسنده تمامی نخ‌های دیگر (خواننده و نویسنده) را مسدود می‌کند، اما خوانندگان هم‌زمان اجازه اجرای موازی دارند.
2. **پیشرفت (Progress):** در صورت بیکار بودن منبع ($R(t)=0, W(t)=0$)، انتخاب نخ بعدی نباید تا بی‌نهایت به تعویق بیفتد (عدم وقوع بن‌بست).
3. **انتظار محدود (Bounded Waiting):** هیچ نویسنده یا خواننده‌ای نباید تا بی‌نهایت دچار گرسنگی (Starvation) شود.

---

### ۲. مقایسه ساختاری رویکردها

```text
       ┌────────────────────────────────────────────────────────────────────────┐
       │        مقایسه مسئله Readers-Writers با سازوکارهای کلاسیک همگام‌سازی        │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │
             ┌─────────────────────────────┴─────────────────────────────┐
             ▼                                                           ▼
┌──────────────────────────┐                               ┌──────────────────────────┐
│  قفل‌های نامتقارن RW-Lock │                               │  قفل‌های چرخشی متقارن   │
│ (خواندن اشتراکی/نوشتن انحصاری)│                           │  (سریال‌سازی ۱ به ۱ نخ‌ها) │
└────────────┬─────────────┘                               └────────────┬─────────────┘
             │                                                           │
     ┌───────┴───────┐                                           ┌───────┴───────┐
     ▼               ▼                                           ▼               ▼
┌─────────┐     ┌─────────┐                                 ┌─────────┐     ┌─────────┐
│Semaphore│     │ Monitor │                                 │ Peterson│     │ Dekker  │
│Turnstile│     │CondVars │                                 │ (1981)  │     │ (1965)  │
└─────────┘     └─────────┘                                 └─────────┘     └─────────┘
```

#### ۲.۱. الگوریتم‌های پایه انحصار متقابل: Peterson (۱۹۸۱) و Dekker (۱۹۶۵)
* **مکانیزم:** قفل‌های چرخشی نرم‌افزاری (Spinlocks) در فضای کاربر با استفاده از پرچم‌های تمایل (`flag[2]`) و متغیر داوری نوبت (`turn`).
* **دلایل شکست در مدل Readers-Writers:**
  1. **عدم پشتیبانی از خواندن هم‌زمان:** دو خواننده را به صورت سریال پشت هم منتظر نگه می‌دارند و گذردهی خواندن را از $O(N)$ به $O(1)$ کاهش می‌دهند.
  2. **محدودیت سخت $N = 2$ نخ:** بدون ساختارهای پیچیده Filter Lock یا درخت مسابقه، بیش از ۲ نخ را پشتیبانی نمی‌کنند.
  3. **مصرف ۱۰۰٪ هسته CPU:** در زمان انتظار برای عملیات طولانی نوشتن، تمام توان هسته پردازنده را در حلقه چرخش هدر می‌دهند و روی پردازنده‌های مدرن نیازمند **سد حافظه (Memory Fence)** هستند.

#### ۲.۲. پیاده‌سازی با سمافور (نسخه اولویت خواننده در برابر نسخه منصفانه Turnstile)
* **راه‌حل اولویت خواننده (Reader-Preference):** از `mutex` برای محافظت از `read_count` و از `rw_mutex` برای مسدود کردن نویسندگان استفاده می‌کند. گذردهی خواندن را به اوج می‌رساند، اما **شرط انتظار محدود را نقض کرده** و در ترافیک سنگین خواندن باعث **گرسنگی دائمی نویسنده (Writer Starvation)** می‌شود.
* **راه‌حل منصفانه Turnstile Semaphore:** با افزودن سمافور سوم (`turnstile = 1`)، به محض ورود نویسنده دروازه ورود خوانندگان جدید بسته می‌شود تا خوانندگان فعلی خارج شده و نویسنده بدون گرسنگی اجرا گردد.

#### ۲.۳. پیاده‌سازی با مانیتور (Monitor و متغیرهای شرطی)
* **طراحی:** وضعیت‌های `active_readers`، `waiting_writers` و `writing` را به همراه متغیرهای شرطی (`can_read` و `can_write`) درون یک شیء ماژولار کپسوله می‌کند.
* **مزیت سیگنالینگ:** در پایان نوشتن (`EndWrite`)، دستور `can_read.broadcast()` (`notifyAll`) تمامی خوانندگان منتظر را به طور هم‌زمان بیدار می‌کند و خطاهای انسانی ناشی از جابه‌جایی دستورات `P()` و `V()` را از بین می‌برد.

---

### ۳. جدول ماتریس مقایسه‌ای جامع

| معیار ارزیابی | ۱. الگوریتم Peterson | ۲. الگوریتم Dekker | ۳. سمافور اولویت خواننده | ۴. سمافور منصفانه Turnstile | ۵. مانیتور RW-Lock |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **تقارن دسترسی** | متقارن (صرفاً انحصاری) | متقارن (صرفاً انحصاری) | **نامتقارن (اشتراکی/انحصاری)** | **نامتقارن (اشتراکی/انحصاری)** | **نامتقارن (اشتراکی/انحصاری)** |
| **۱. انحصار متقابل** | اثبات‌شده ($N=2$) | اثبات‌شده ($N=2$) | انحصار کامل نویسنده | انحصار کامل نویسنده | انحصار کامل نویسنده |
| **۲. پیشرفت (Progress)** | تضمین‌شده (`turn`) | تضمین‌شده (عقب‌نشینی) | تضمین‌شده | تضمین‌شده (Turnstile) | تضمین‌شده (کپسوله) |
| **۳. انتظار محدود** | کران‌دار ($\le 1$ نوبت) | کران‌دار ($\le 1$ نوبت) | **نقض می‌شود (گرسنگی نویسنده!)** | **کاملاً کران‌دار و منصفانه** | **کاملاً کران‌دار و منصفانه** |
| **خواندن هم‌زمان** | خیر (سریال‌سازی) | خیر (سریال‌سازی) | **بله ($N$ خواننده هم‌زمان)** | **بله ($N$ خواننده هم‌زمان)** | **بله (پخش Broadcast)** |
| **وضعیت CPU در انتظار** | انتظار مشغول (۱۰۰٪) | انتظار مشغول (۱۰۰٪) | **خواب در کرنل (۰٪ CPU)** | **خواب در کرنل (۰٪ CPU)** | **خواب در صف شرط (۰٪)** |
| **سقف تعداد نخ‌ها** | صرفاً $N = 2$ | صرفاً $N = 2$ | تعداد دلخواه $N$ نخ | تعداد دلخواه $N$ نخ | تعداد دلخواه $N$ نخ |
| **ایمنی پیاده‌سازی** | نیازمند Memory Fence | نیازمند ۲ Fence | مستعد خطای ترتیب P/V | ایمنی بالا (۳ سمافور) | **بالاترین ایمنی (شیءگرا)** |

---

### ۴. خلاصه نتایج بنچمارک‌های تجربی
بر اساس ۱۰,۰۰۰ عملیات در شبیه‌ساز چندنخی `readers_writers_benchmark.py`:
* **رشد خطی گذردهی خواندن:** سمافور و مانیتور RW-Lock گذردهی خواندن را از $96\text{ kOps/s}$ (۱ خواننده) به $1,340\text{ kOps/s}$ (۱۶ خواننده) — معادل **۱۳.۹ برابر افزایش سرعت** — می‌رسانند، در حالی که پترسون و دکر به دلیل سریال‌سازی روی $\sim 90\text{ kOps/s}$ ثابت می‌مانند.
* **مهار گرسنگی نویسنده:** در بار کاری با ۹۰٪ عملیات خواندن، بیشینه زمان انتظار نویسنده در سمافور اولویت خواننده به **$480.0\text{ ms}$** می‌رسد؛ در حالی که در سمافور منصفانه Turnstile به **$14.5\text{ ms}$** و در مانیتور RW به **$8.2\text{ ms}$** کاهش می‌یابد.
* **مصرف پردازنده:** پترسون و دکر در حالت انتظار **$۱۰۰.۰٪$** هسته CPU را اشغال می‌کنند؛ در حالی که سمافور و مانیتور با بردن نخ‌ها به حالت خواب، بار انتظار CPU را به **$۳.۲٪$** و **$۴.۱٪$** می‌رسانند.

---
> **Course Project:** Operating Systems / Embedded & Real-Time Systems — Eshragh Higher Education Institute | Developed by [@atnc6](https://github.com/atnc6)
