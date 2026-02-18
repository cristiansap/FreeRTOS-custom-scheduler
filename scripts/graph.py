import asyncio
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

from debug import capture_traces

def plot_gantt(gantt_data, splits, fix_t_max=None, tasks=[]):
    # Detect which special system events are present
    has_pendsv = any(name == "PendSV" for _, name, _ in gantt_data)
    task_rows = ["Tasks", "PendSV", "SysTick"] if has_pendsv else ["Tasks", "SysTick"]

    # Timeline splits
    t_min, t_max = gantt_data[0][0], gantt_data[-1][2]
    t_max = fix_t_max if fix_t_max else t_max
    slice_size = (t_max - t_min) / splits
    intervals = [(t_min + i * slice_size, t_min + (i + 1) * slice_size) for i in range(splits)]

    # Colors for tasks
    real_tasks = {name for _, name, _ in gantt_data if name not in ("SysTick", "PendSV", "PENDSVSET")}
    task_colors = {name: plt.cm.tab20(i % 20) for i, name in enumerate(real_tasks)}

    fig, axes = plt.subplots(splits, 1, figsize=(14, 4*splits))  # increase height

    if splits == 1:
        axes = [axes]

    for ax, (rs, re) in zip(axes, intervals):
        if tasks:
            for start, end in tasks:
                if end < rs or start > re:
                    continue
                cs, ce = max(start, rs), min(end, re)
                ax.hlines(-0.6, cs, ce, colors="black", linewidth=2)
                ax.vlines([cs, ce], -0.6, -0.5, colors="black", linewidth=2)

        for start, name, end in gantt_data:
            if end < rs or start > re:
                continue  # skip bars fully outside

            # Plot the bar
            clipped_start = max(start, rs)
            clipped_end = min(end, re)
            row = task_rows.index(name) if name in task_rows else 0

            if name == "PENDSVSET":
                ax.plot([clipped_start, clipped_start], [-0.5, has_pendsv + 1.5], color="gray", linestyle="dotted")
                continue
            
            if name == "SysTick":
                ax.plot([clipped_start, clipped_start], [-0.5, has_pendsv + 1.5], color="black", linestyle="dotted")

            if name == "MISS":
                ax.plot(clipped_start, row, marker="x", color="black", markersize=10, markeredgewidth=2)
                continue
            
            color = task_colors.get(name, "lightgray")
            ax.barh(row, clipped_end - clipped_start, left=clipped_start, color=color, edgecolor="black", height=0.8)

        ax.set_xlim(rs, re)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/25000)}ms"))
        ax.set_title(f"{int(rs)} → {int(re)} ticks")

    axes[0].set_yticks(range(len(task_rows)))
    axes[0].set_yticklabels(task_rows)

    legend_handles = [Patch(facecolor=c, edgecolor="black", label=n) for n, c in sorted(task_colors.items())]
    axes[0].legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    plt.subplots_adjust(left=0.08, right=0.85, top=0.95, bottom=0.05, hspace=0.6)
    plt.show()

if __name__ == "__main__":
    plot_gantt(asyncio.run(capture_traces()), splits=6)
