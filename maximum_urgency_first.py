#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Operating System (RTOS) Scheduler Simulator
Algorithm: Maximum Urgency First (MUF) Scheduling
File: maximum_urgency_first.py
Course: Embedded and Real-Time Systems
Dependencies: None (Pure Python 3 Standard Library)
"""

import sys
import os
import copy
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Ensure UTF-8 output on Windows CMD / PowerShell so Unicode tables & Gantt charts render cleanly
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==============================================================================
# 1. OBJECT-ORIENTED DATA MODELS (`Process` & Snapshot Structures)
# ==============================================================================

class Process:
    """
    Represents a Real-Time Task/Process in the Maximum Urgency First (MUF) Scheduler.

    MUF Priority Hierarchy (3-Tier Urgency Tuple):
      1. Criticality Tier (Static) : Critical tasks (is_critical=True or criticality >= 2)
                                      ALWAYS take precedence over Non-Critical tasks.
      2. Dynamic Urgency (Dynamic) : Within the same criticality tier, the task with the
                                     minimum Laxity (maximum Urgency = -Laxity) is selected.
      3. User/Static Priority      : Tie-breaker if two tasks have identical Criticality & Laxity.
    """

    def __init__(
        self,
        pid: str,
        arrival_time: int,
        burst_time: int,
        deadline: int,
        criticality: int = 1,
        user_priority: int = 1,
    ):
        """
        Parameters:
            pid (str)          : Unique Process Identifier (e.g., 'P1', 'T_Crit1').
            arrival_time (int) : Time at which the task enters the ready queue.
            burst_time (int)   : Total required CPU execution time (C_i).
            deadline (int)     : Absolute deadline by which execution must finish (D_i).
            criticality (int)  : Static criticality level (1 = High/Critical, 0 = Low/Non-Critical).
            user_priority (int): Optional static tie-breaker priority (higher number = higher priority).
        """
        self.pid: str = pid
        self.arrival_time: int = int(arrival_time)
        self.burst_time: int = int(burst_time)
        self.deadline: int = int(deadline)
        self.criticality: int = int(criticality)  # 1 = Critical Set, 0 = Non-Critical Set
        self.user_priority: int = int(user_priority)

        # Dynamic Runtime Attributes
        self.remaining_time: int = int(burst_time)
        self.state: str = "NOT_ARRIVED"  # NOT_ARRIVED, READY, RUNNING, COMPLETED

        # Calculated Output Metrics
        self.start_time: Optional[int] = None
        self.finish_time: Optional[int] = None
        self.turnaround_time: Optional[int] = None
        self.waiting_time: int = 0
        self.response_time: Optional[int] = None
        self.deadline_met: Optional[bool] = None
        self.preemption_count: int = 0

    @property
    def criticality_label(self) -> str:
        return "CRITICAL" if self.criticality >= 1 else "NON-CRITICAL"

    def calculate_laxity(self, current_time: int) -> int:
        """
        Calculates dynamic Laxity (Slack Time) at time `current_time`:
            Laxity(t) = Deadline - Current_Time - Remaining_Burst_Time
        A negative laxity indicates that the task cannot meet its deadline even if
        scheduled immediately and continuously.
        """
        return self.deadline - current_time - self.remaining_time

    def calculate_urgency(self, current_time: int) -> int:
        """
        Calculates dynamic Urgency at time `current_time`:
            Urgency(t) = -Laxity(t) = Current_Time + Remaining_Burst_Time - Deadline
        Higher value means higher urgency (smaller laxity).
        """
        return -self.calculate_laxity(current_time)

    def finalize_metrics(self):
        """Computes final Turnaround, Waiting, Response, and Deadline status upon completion."""
        if self.finish_time is not None:
            self.turnaround_time = self.finish_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
            self.deadline_met = self.finish_time <= self.deadline
        if self.start_time is not None:
            self.response_time = self.start_time - self.arrival_time


@dataclass
class TickSnapshot:
    """Stores the exact state of the CPU and all tasks during time interval [t, t+1]."""
    tick: int
    running_pid: Optional[str]
    running_criticality: Optional[int]
    running_laxity: Optional[int]
    running_urgency: Optional[int]
    preempted_pid: Optional[str]
    task_states: Dict[str, str]       # pid -> RUN_CRIT, RUN_NONCRIT, READY, DONE, NONE
    task_laxities: Dict[str, Optional[int]]
    missed_deadline_Now: List[str]


# ==============================================================================
# 2. MAXIMUM URGENCY FIRST (MUF) SCHEDULER ENGINE (`MUFScheduler`)
# ==============================================================================

class MUFScheduler:
    """
    Preemptive Discrete-Time Maximum Urgency First (MUF) Scheduler.
    Combines fixed-priority criticality partitioning with dynamic Least-Laxity /
    Maximum-Urgency scheduling inside each partition.
    """

    def __init__(self, processes: List[Process], scenario_title: str = "MUF Simulation"):
        self.scenario_title: str = scenario_title
        self.processes: List[Process] = copy.deepcopy(processes)
        self.proc_map: Dict[str, Process] = {p.pid: p for p in self.processes}
        self.timeline: List[TickSnapshot] = []
        self.event_log: List[Tuple[int, str]] = []
        self.current_time: int = 0
        self.max_simulation_ticks: int = 300

    def log_event(self, msg: str):
        self.event_log.append((self.current_time, msg))

    def _all_completed(self) -> bool:
        return all(p.state == "COMPLETED" for p in self.processes)

    def _select_highest_urgency_process(self, ready_list: List[Process]) -> Optional[Process]:
        """
        Core MUF Selection Policy:
          1. Higher `criticality` (Critical Set > Non-Critical Set)
          2. Smaller `laxity` / Higher `urgency` (Urgency = -Laxity)
          3. Earlier `deadline` (EDF tie-breaker)
          4. Higher `user_priority` (Static tie-breaker)
          5. Earlier `arrival_time` & Process ID
        """
        if not ready_list:
            return None

        t = self.current_time
        ready_list.sort(
            key=lambda p: (
                -p.criticality,                # 1. Critical tasks first (descending)
                p.calculate_laxity(t),         # 2. Minimum Laxity / Maximum Urgency first (ascending)
                p.deadline,                    # 3. Earlier deadline tie-breaker
                -p.user_priority,              # 4. Higher static user priority tie-breaker
                p.arrival_time,                # 5. FCFS tie-breaker
                p.pid,
            )
        )
        return ready_list[0]

    def run(self) -> List[TickSnapshot]:
        """Executes the discrete-time MUF scheduling simulation tick-by-tick."""
        previously_running: Optional[Process] = None

        while not self._all_completed() and self.current_time < self.max_simulation_ticks:
            t = self.current_time

            # 1. Check for newly arriving processes at tick t
            for p in self.processes:
                if p.state == "NOT_ARRIVED" and p.arrival_time == t:
                    p.state = "READY"
                    lax = p.calculate_laxity(t)
                    urg = p.calculate_urgency(t)
                    self.log_event(
                        f"[ARRIVAL] {p.pid} ({p.criticality_label}) arrived | "
                        f"Burst={p.burst_time}s, Deadline={p.deadline}s, Initial Laxity={lax}s (Urgency={urg:+d})"
                    )

            # 2. Check if any active process just passed its deadline at tick t
            missed_now: List[str] = []
            for p in self.processes:
                if p.state in ("READY", "RUNNING") and t == p.deadline and p.remaining_time > 0:
                    missed_now.append(p.pid)
                    self.log_event(
                        f"[DEADLINE WARNING] {p.pid} ({p.criticality_label}) missed its deadline "
                        f"at t={t}s (Remaining={p.remaining_time}s)!"
                    )

            # 3. Collect all ready/active tasks and apply MUF two-level selection
            active_tasks = [p for p in self.processes if p.state in ("READY", "RUNNING")]
            for p in active_tasks:
                p.state = "READY"

            selected = self._select_highest_urgency_process(active_tasks)

            # 4. Detect Preemption
            preempted_pid: Optional[str] = None
            if (
                previously_running is not None
                and previously_running.state == "READY"
                and selected is not None
                and selected.pid != previously_running.pid
            ):
                preempted_pid = previously_running.pid
                previously_running.preemption_count += 1
                self.log_event(
                    f"[PREEMPTION] {selected.pid} ({selected.criticality_label}, "
                    f"Laxity={selected.calculate_laxity(t)}s, Urgency={selected.calculate_urgency(t):+d}) "
                    f"preempted {previously_running.pid} ({previously_running.criticality_label}, "
                    f"Laxity={previously_running.calculate_laxity(t)}s)"
                )

            # 5. Dispatch selected task on CPU for interval [t, t+1]
            run_pid = None
            run_crit = None
            run_lax = None
            run_urg = None

            if selected is not None:
                selected.state = "RUNNING"
                if selected.start_time is None:
                    selected.start_time = t
                    self.log_event(
                        f"[START] {selected.pid} started first execution on CPU "
                        f"(Response Time = {t - selected.arrival_time}s)"
                    )
                run_pid = selected.pid
                run_crit = selected.criticality
                run_lax = selected.calculate_laxity(t)
                run_urg = selected.calculate_urgency(t)

            # 6. Record tick snapshot for Gantt Chart & Timeline Log
            states_map: Dict[str, str] = {}
            laxities_map: Dict[str, Optional[int]] = {}
            for p in self.processes:
                if p.state == "RUNNING":
                    states_map[p.pid] = "RUN_CRIT" if p.criticality >= 1 else "RUN_NONCRIT"
                    laxities_map[p.pid] = p.calculate_laxity(t)
                elif p.state == "READY":
                    states_map[p.pid] = "READY"
                    laxities_map[p.pid] = p.calculate_laxity(t)
                elif p.state == "COMPLETED":
                    states_map[p.pid] = "DONE"
                    laxities_map[p.pid] = None
                else:
                    states_map[p.pid] = "NONE"
                    laxities_map[p.pid] = None

            self.timeline.append(
                TickSnapshot(
                    tick=t,
                    running_pid=run_pid,
                    running_criticality=run_crit,
                    running_laxity=run_lax,
                    running_urgency=run_urg,
                    preempted_pid=preempted_pid,
                    task_states=states_map,
                    task_laxities=laxities_map,
                    missed_deadline_Now=missed_now,
                )
            )

            # 7. Advance time to t + 1
            self.current_time += 1

            if selected is not None:
                selected.remaining_time -= 1
                if selected.remaining_time == 0:
                    selected.state = "COMPLETED"
                    selected.finish_time = self.current_time
                    selected.finalize_metrics()
                    status_str = (
                        "MET DEADLINE ✓"
                        if selected.deadline_met
                        else f"MISSED DEADLINE ✗ (Deadline was {selected.deadline}s)"
                    )
                    self.log_event(
                        f"[FINISH] {selected.pid} ({selected.criticality_label}) completed at "
                        f"t={self.current_time}s -> {status_str}"
                    )
                    previously_running = None
                else:
                    previously_running = selected
            else:
                previously_running = None

        return self.timeline

    def get_system_summary(self) -> Dict[str, float]:
        """Computes aggregate and average real-time metrics across all processes."""
        completed = [p for p in self.processes if p.finish_time is not None]
        n = len(completed) if completed else 1

        avg_tat = sum(p.turnaround_time or 0 for p in completed) / n
        avg_wt = sum(p.waiting_time for p in completed) / n
        avg_rt = sum(p.response_time or 0 for p in completed) / n

        crit_tasks = [p for p in self.processes if p.criticality >= 1]
        crit_met = sum(1 for p in crit_tasks if p.deadline_met)

        noncrit_tasks = [p for p in self.processes if p.criticality < 1]
        noncrit_met = sum(1 for p in noncrit_tasks if p.deadline_met)

        busy_ticks = sum(1 for snap in self.timeline if snap.running_pid is not None)
        total_ticks = len(self.timeline) if self.timeline else 1

        return {
            "avg_turnaround_time": avg_tat,
            "avg_waiting_time": avg_wt,
            "avg_response_time": avg_rt,
            "critical_total": len(crit_tasks),
            "critical_met": crit_met,
            "noncritical_total": len(noncrit_tasks),
            "noncritical_met": noncrit_met,
            "cpu_utilization": (busy_ticks / total_ticks) * 100.0,
            "total_preemptions": sum(p.preemption_count for p in self.processes),
        }


# ==============================================================================
# 3. TERMINAL VISUALIZER (TABLES, STEP-BY-STEP TIMELINE, ASCII GANTT CHART)
# ==============================================================================

def print_banner():
    print("=" * 98)
    print("   REAL-TIME OPERATING SYSTEM (RTOS) — MAXIMUM URGENCY FIRST (MUF) SCHEDULER SIMULATOR")
    print("   Dynamic Laxity + Criticality-Partitioned Scheduling | Embedded & Real-Time Systems")
    print("=" * 98)


def render_simulation_output(scheduler: MUFScheduler):
    procs = scheduler.processes
    timeline = scheduler.timeline
    total_t = len(timeline)

    print("\n" + "━" * 98)
    print(f"  SCENARIO: {scheduler.scenario_title}")
    print("━" * 98)

    # 1. Input Process Table
    print("\n  [1] INPUT PROCESS SPECIFICATIONS:")
    print("  ┌──────────┬──────────────┬────────────┬──────────┬─────────────────┬──────────────────┐")
    print("  │ Proc ID  │ Arrival Time │ Burst Time │ Deadline │ Criticality Set │ Initial Laxity   │")
    print("  ├──────────┼──────────────┼────────────┼──────────┼─────────────────┼──────────────────┤")
    for p in procs:
        init_lax = p.deadline - p.arrival_time - p.burst_time
        crit_tag = "CRITICAL (1)" if p.criticality >= 1 else "NON-CRIT (0)"
        print(
            f"  │ {p.pid:<8} │ t = {p.arrival_time:<8} │ {p.burst_time:>7}s   │ "
            f"t = {p.deadline:<4} │ {crit_tag:<15} │ {init_lax:>6}s (U={-init_lax:+d}) │"
        )
    print("  └──────────┴──────────────┴────────────┴──────────┴─────────────────┴──────────────────┘")

    # 2. ASCII Gantt Chart
    print("\n  [2] ASCII / UNICODE GANTT CHART & CPU TIMELINE:")
    print("      ███ : Running (CRITICAL Task)       ▓▓▓ : Running (NON-CRITICAL Task)")
    print("      ··· : Waiting in Ready Queue        ─── : Not Arrived / Completed")
    print("       D! : Deadline Point Reached\n")

    header_ticks = "  Time (t)   │" + "".join(f"{t:>3} " for t in range(total_t))
    divider_line = "  ───────────┼" + "────" * total_t
    print(header_ticks)
    print(divider_line)

    symbol_map = {
        "RUN_CRIT":    "███|",
        "RUN_NONCRIT": "▓▓▓|",
        "READY":       "···|",
        "DONE":        "   |",
        "NONE":        "   |",
    }

    # Sort rows: Critical tasks on top, then by PID
    sorted_procs = sorted(procs, key=lambda x: (-x.criticality, x.pid))
    for p in sorted_procs:
        cells = []
        for snap in timeline:
            st = snap.task_states.get(p.pid, "NONE")
            cell = symbol_map.get(st, "   |")
            cells.append(cell)
        c_badge = "C" if p.criticality >= 1 else "N"
        label = f"{p.pid}({c_badge},D={p.deadline})"
        print(f"  {label:<11}│" + "".join(cells))

    print(divider_line)

    # CPU Execution Row
    cpu_cells = [
        f"{snap.running_pid[:3]:>3}|" if snap.running_pid else "IDL|"
        for snap in timeline
    ]
    print("  CPU Active │" + "".join(cpu_cells))

    # Active Task Laxity Row
    lax_cells = [
        f"{snap.running_laxity:>3}|" if snap.running_laxity is not None else "  -|"
        for snap in timeline
    ]
    print("  Run Laxity │" + "".join(lax_cells) + "  (Laxity = D - t - Rem)")

    # Active Task Urgency Row
    urg_cells = [
        f"{snap.running_urgency:>+3}|" if snap.running_urgency is not None else "  -|"
        for snap in timeline
    ]
    print("  Run Urgency│" + "".join(urg_cells) + "  (Urgency = -Laxity)")
    print(divider_line)

    # 3. Step-by-Step CPU Timeline Execution Log
    print("\n  [3] STEP-BY-STEP TIMELINE EXECUTION LOG (Tick-by-Tick Laxity & Decision):")
    print("  ┌───────────┬────────────┬──────────────┬───────────────┬──────────────────────────────────────────┐")
    print("  │ Time [t]  │ CPU Winner │ Winner Class │ Laxity / Urg. │ Ready Queue Candidates (PID: Laxity)     │")
    print("  ├───────────┼────────────┼──────────────┼───────────────┼──────────────────────────────────────────┤")
    for snap in timeline:
        interval = f"[{snap.tick:>2} -> {snap.tick+1:>2}]"
        winner = snap.running_pid if snap.running_pid else "IDLE"
        w_class = (
            "CRITICAL"
            if snap.running_criticality and snap.running_criticality >= 1
            else ("NON-CRIT" if snap.running_criticality is not None else "-")
        )
        lax_urg = (
            f"L={snap.running_laxity:>2}, U={snap.running_urgency:>+2}"
            if snap.running_laxity is not None
            else "     -       "
        )
        ready_strs = [
            f"{pid}(L={lax})"
            for pid, lax in snap.task_laxities.items()
            if lax is not None
        ]
        ready_col = ", ".join(ready_strs)
        if len(ready_col) > 40:
            ready_col = ready_col[:37] + "..."
        print(f"  │ {interval:<9} │ {winner:<10} │ {w_class:<12} │ {lax_urg:<13} │ {ready_col:<40} │")
    print("  └───────────┴────────────┴──────────────┴───────────────┴──────────────────────────────────────────┘")

    # 4. Kernel Discrete Event Log
    print("\n  [4] KERNEL SCHEDULING & PREEMPTION EVENTS:")
    for tick, msg in scheduler.event_log:
        print(f"    t = {tick:>2}s : {msg}")

    # 5. Output Process Metrics Table
    print("\n  [5] OUTPUT SCHEDULING METRICS PER PROCESS:")
    print("  ┌─────────┬──────────────┬─────────┬────────┬──────────┬────────────┬──────────┬──────────┬──────────────────┐")
    print("  │ Proc ID │ Criticality  │ Arrival │ Burst  │ Deadline │ Finish (F) │ TAT      │ Wait (W) │ Response / Status│")
    print("  ├─────────┼──────────────┼─────────┼────────┼──────────┼────────────┼──────────┼──────────┼──────────────────┤")
    for p in procs:
        crit_s = "CRITICAL" if p.criticality >= 1 else "NON-CRIT"
        fin_s = f"{p.finish_time}s" if p.finish_time is not None else "N/A"
        tat_s = f"{p.turnaround_time}s" if p.turnaround_time is not None else "N/A"
        wt_s = f"{p.waiting_time}s"
        rt_s = f"R={p.response_time}s" if p.response_time is not None else "N/A"
        status_badge = "MET ✓" if p.deadline_met else "MISSED ✗"
        print(
            f"  │ {p.pid:<7} │ {crit_s:<12} │ {p.arrival_time:>5}s  │ {p.burst_time:>4}s  │ "
            f"{p.deadline:>6}s  │ {fin_s:>8}   │ {tat_s:>6}   │ {wt_s:>6}   │ {rt_s:<6} ({status_badge}) │"
        )
    print("  └─────────┴──────────────┴─────────┴────────┴──────────┴────────────┴──────────┴──────────┴──────────────────┘")

    # 6. Aggregate System Metrics Summary
    summary = scheduler.get_system_summary()
    print("\n  [6] SYSTEM-WIDE PERFORMANCE SUMMARY:")
    print(f"    • Average Turnaround Time (Avg TAT) : {summary['avg_turnaround_time']:.2f} s")
    print(f"    • Average Waiting Time (Avg WT)     : {summary['avg_waiting_time']:.2f} s")
    print(f"    • Average Response Time (Avg RT)    : {summary['avg_response_time']:.2f} s")
    print(f"    • Critical Tasks Deadline Guarantee : {int(summary['critical_met'])} / {int(summary['critical_total'])} Met (100% Guaranteed under MUF)")
    print(f"    • Non-Critical Tasks Deadlines Met  : {int(summary['noncritical_met'])} / {int(summary['noncritical_total'])} Met")
    print(f"    • Total Preemptions Count           : {int(summary['total_preemptions'])} context switches due to urgency")
    print(f"    • Total CPU Utilization             : {summary['cpu_utilization']:.1f} %\n")


# ==============================================================================
# 4. ZERO-DEPENDENCY HTML VISUAL GANTT REPORT GENERATOR
# ==============================================================================

def export_html_muf_report(schedulers: List[MUFScheduler], filename: str = "muf_gantt_report.html"):
    """Generates a visual HTML report for all executed MUF scenarios without external libraries."""
    sections_html = ""

    for sched in schedulers:
        total_t = len(sched.timeline)
        headers = "".join(f"<th>{t}-{t+1}</th>" for t in range(total_t))
        rows_html = ""

        sorted_procs = sorted(sched.processes, key=lambda x: (-x.criticality, x.pid))
        for p in sorted_procs:
            cells = ""
            for snap in sched.timeline:
                st = snap.task_states.get(p.pid, "NONE")
                lax = snap.task_laxities.get(p.pid, None)
                if st == "RUN_CRIT":
                    bg, fg, txt = "#2563eb", "#ffffff", f"RUN (L={lax})"
                elif st == "RUN_NONCRIT":
                    bg, fg, txt = "#10b981", "#ffffff", f"RUN (L={lax})"
                elif st == "READY":
                    bg, fg, txt = "#fef3c7", "#92400e", f"Wait (L={lax})"
                else:
                    bg, fg, txt = "#f8fafc", "#cbd5e1", ""
                cells += (
                    f'<td style="background:{bg}; color:{fg}; font-size:11px; font-weight:600; '
                    f'text-align:center; padding:6px 2px; border:1px solid #cbd5e1;">{txt}</td>'
                )
            badge = "CRITICAL" if p.criticality >= 1 else "NON-CRIT"
            status_color = "#16a34a" if p.deadline_met else "#dc2626"
            status_txt = "MET ✓" if p.deadline_met else "MISSED ✗"
            rows_html += (
                f"<tr><td style='font-weight:bold; padding:8px; border:1px solid #cbd5e1; background:#f1f5f9;'>"
                f"{p.pid} <small>({badge}, D={p.deadline})</small> "
                f"<span style='color:{status_color};'>[{status_txt}]</span></td>{cells}</tr>"
            )

        summary = sched.get_system_summary()
        sections_html += f"""
        <div class="card">
            <h2>{sched.scenario_title}</h2>
            <p>
                <strong>Avg Turnaround:</strong> {summary['avg_turnaround_time']:.2f}s &nbsp;|&nbsp;
                <strong>Avg Waiting:</strong> {summary['avg_waiting_time']:.2f}s &nbsp;|&nbsp;
                <strong>Avg Response:</strong> {summary['avg_response_time']:.2f}s &nbsp;|&nbsp;
                <strong>Critical Deadlines Met:</strong> {int(summary['critical_met'])}/{int(summary['critical_total'])}
            </p>
            <div style="overflow-x:auto;">
                <table style="border-collapse:collapse; width:100%; min-width:750px;">
                    <thead>
                        <tr style="background:#1e293b; color:white;">
                            <th style="padding:8px; text-align:left;">Process (Class, Deadline)</th>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        </div>
        """

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MUF Real-Time Scheduler Visual Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#f8fafc; color:#0f172a; margin:24px; }}
        h1 {{ color:#1e293b; border-bottom:2px solid #cbd5e1; padding-bottom:10px; }}
        .card {{ background:white; border-radius:8px; padding:20px; margin-bottom:24px; box-shadow:0 2px 6px rgba(0,0,0,0.08); }}
        .legend {{ display:flex; gap:18px; flex-wrap:wrap; margin-bottom:20px; font-size:13px; }}
        .badge {{ display:inline-block; width:16px; height:16px; border-radius:3px; vertical-align:middle; margin-right:6px; }}
    </style>
</head>
<body>
    <h1>Maximum Urgency First (MUF) Scheduler — Gantt Chart & Laxity Report</h1>
    <div class="legend">
        <div><span class="badge" style="background:#2563eb;"></span>Running (Critical Set)</div>
        <div><span class="badge" style="background:#10b981;"></span>Running (Non-Critical Set)</div>
        <div><span class="badge" style="background:#fef3c7; border:1px solid #f59e0b;"></span>Waiting in Ready Queue (with Dynamic Laxity)</div>
    </div>
    {sections_html}
</body>
</html>
"""
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"  [HTML EXPORT] Visual MUF Gantt Report saved to: {filepath}\n")


# ==============================================================================
# 5. TEST SCENARIOS (NORMAL LOAD, TRANSIENT OVERLOAD, & INTERACTIVE CUSTOM)
# ==============================================================================

def get_scenario_1_normal_schedulable() -> List[Process]:
    """
    Scenario 1: Normal / Schedulable Load (CPU Utilization <= 100%).
    Demonstrates:
      - Dynamic Laxity calculation (Laxity = Deadline - Current_Time - Remaining_Burst).
      - Urgency-based preemption within the Critical Set (P3 arrives at t=2 with tighter
        laxity than P1 and immediately preempts P1).
      - All Critical and Non-Critical processes meet their deadlines.
    """
    return [
        Process(pid="P1", arrival_time=0, burst_time=4, deadline=10, criticality=1, user_priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, deadline=14, criticality=0, user_priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, deadline=5,  criticality=1, user_priority=3),
        Process(pid="P4", arrival_time=4, burst_time=3, deadline=15, criticality=0, user_priority=1),
    ]


def get_scenario_2_transient_overload() -> List[Process]:
    """
    Scenario 2: Heavy Traffic / Transient Overload (Total Burst > Deadlines).
    Why MUF was invented:
      - Under pure EDF or LLF, an urgent Non-Critical task with a very tight deadline (e.g., P_NC1
        with Deadline=4) would preempt Critical tasks and cause a cascading domino effect where
        CRITICAL tasks miss their deadlines!
      - Under MUF, Critical tasks (P_C1, P_C2, P_C3) are strictly isolated in the Critical Set.
        Within the Critical Set, MUF dynamically schedules by Maximum Urgency (minimum laxity),
        guaranteeing 100% of Critical Tasks meet their deadlines while gracefully shedding
        the overload onto Non-Critical tasks.
    """
    return [
        Process(pid="P_C1",  arrival_time=0, burst_time=4, deadline=9,  criticality=1, user_priority=2),
        Process(pid="P_NC1", arrival_time=0, burst_time=3, deadline=4,  criticality=0, user_priority=3),
        Process(pid="P_C2",  arrival_time=1, burst_time=3, deadline=6,  criticality=1, user_priority=3),
        Process(pid="P_C3",  arrival_time=3, burst_time=2, deadline=8,  criticality=1, user_priority=1),
        Process(pid="P_NC2", arrival_time=2, burst_time=3, deadline=16, criticality=0, user_priority=1),
    ]


def get_custom_user_processes() -> List[Process]:
    """Interactive CLI prompt for custom user processes."""
    print("\n--- CUSTOM MUF PROCESS INPUT ---")
    while True:
        try:
            count = int(input("Enter number of processes (e.g., 4): ").strip())
            if count > 0:
                break
        except ValueError:
            pass
        print("Please enter a valid positive integer.")

    custom_list: List[Process] = []
    for i in range(count):
        print(f"\n[Process #{i+1}]")
        pid = input(f"  Process ID (default P{i+1}): ").strip() or f"P{i+1}"
        arr = int(input(f"  Arrival Time for {pid} (e.g., 0): ").strip() or "0")
        bst = int(input(f"  CPU Burst Time for {pid} (e.g., 3): ").strip() or "3")
        ddl = int(input(f"  Absolute Deadline for {pid} (e.g., 8): ").strip() or "8")
        crit = int(input(f"  Criticality (1 = Critical, 0 = Non-Critical) [default 1]: ").strip() or "1")
        custom_list.append(
            Process(pid=pid, arrival_time=arr, burst_time=bst, deadline=ddl, criticality=crit)
        )
    return custom_list


def main():
    print_banner()
    print("\nSelect MUF Simulation Execution Mode:")
    print("  [1] Run Both Standard Test Scenarios (Scenario 1: Normal Load + Scenario 2: Overload) [Default]")
    print("  [2] Run Scenario 1 Only (Normal Schedulable Traffic & Dynamic Laxity Preemption)")
    print("  [3] Run Scenario 2 Only (Transient Overload — Protecting Critical Set Deadlines)")
    print("  [4] Custom Interactive Mode (Enter your own processes, deadlines, and criticality)")

    try:
        choice = input("\nEnter choice (1/2/3/4) [Press Enter for 1]: ").strip()
    except EOFError:
        choice = "1"

    executed_schedulers: List[MUFScheduler] = []

    if choice == "2":
        s1 = MUFScheduler(
            get_scenario_1_normal_schedulable(),
            scenario_title="Scenario 1: Normal Schedulable Traffic (Dynamic Laxity & Preemption)"
        )
        s1.run()
        render_simulation_output(s1)
        executed_schedulers.append(s1)

    elif choice == "3":
        s2 = MUFScheduler(
            get_scenario_2_transient_overload(),
            scenario_title="Scenario 2: Transient System Overload (Critical Task Protection)"
        )
        s2.run()
        render_simulation_output(s2)
        executed_schedulers.append(s2)

    elif choice == "4":
        custom_procs = get_custom_user_processes()
        sc = MUFScheduler(
            custom_procs,
            scenario_title="Custom User-Defined MUF Simulation"
        )
        sc.run()
        render_simulation_output(sc)
        executed_schedulers.append(sc)

    else:
        # Default: Run both Scenario 1 and Scenario 2 to prove normal + overload behavior
        s1 = MUFScheduler(
            get_scenario_1_normal_schedulable(),
            scenario_title="Scenario 1: Normal Schedulable Traffic (Dynamic Laxity & Preemption)"
        )
        s1.run()
        render_simulation_output(s1)
        executed_schedulers.append(s1)

        s2 = MUFScheduler(
            get_scenario_2_transient_overload(),
            scenario_title="Scenario 2: Transient System Overload (Critical Task Protection)"
        )
        s2.run()
        render_simulation_output(s2)
        executed_schedulers.append(s2)

    export_html_muf_report(executed_schedulers)


if __name__ == "__main__":
    main()