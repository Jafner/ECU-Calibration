# WARNING: VIBE CODED

import csv
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

# === CONFIGURATION ===
RPM_COL = "RPM"
LOAD_COL = "Load (g/rev)"
SPEED_COL = "Speed (mph)"
TIMING_COL = "Timing (deg)"
MAF_COL = "MAF (g/s)"

HP_PER_GS = 0.96


def read_csv(filepath):
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def process_pull(rows):
    rpm, load, speed, timing, maf = [], [], [], [], []
    for r in rows:
        try:
            rpm.append(float(r[RPM_COL]))
            load.append(float(r[LOAD_COL]))
            speed.append(float(r[SPEED_COL]))
            timing.append(float(r[TIMING_COL]))
            maf.append(float(r[MAF_COL]))
        except (ValueError, KeyError):
            continue
    return rpm, load, speed, timing, maf


def compute_derived(rpm, maf):
    hp, torque = [], []
    for i in range(len(rpm)):
        hp_val = maf[i] * HP_PER_GS
        hp.append(hp_val)
        rpm_val = rpm[i]
        torque.append(hp_val * 5252.0 / rpm_val if rpm_val > 0 else 0.0)
    return hp, torque

def interactive_plot(filepath, rpm, series_data, hp, torque):
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax_bottom.tick_params(axis='x', labelbottom=True)
    ax_top.tick_params(axis='x', labelbottom=True)
    fig.canvas.manager.set_window_title(os.path.basename(filepath))
    fig.suptitle(os.path.basename(filepath), fontsize=14, fontweight="bold")

    # Align X-axis limits
    x_min, x_max = min(rpm), max(rpm)
    ax_top.set_xlim(x_min, x_max)
    ax_bottom.set_xlim(x_min, x_max)

    # --- Top panel: signals vs RPM ---
    axes = [ax_top]
    for i in range(1, len(series_data)):
        ax_new = ax_top.twinx()
        ax_new.spines["right"].set_position(("axes", 1 + 0.1 * (i - 1)))
        axes.append(ax_new)

    lines = []
    for ax, (label, unit, data, color) in zip(axes, series_data):
        line, = ax.plot(rpm, data, color=color, label=f"{label} ({unit})")
        ax.set_ylabel(f"{label} ({unit})", color=color)
        ax.tick_params(axis='y', colors=color)
        lines.append(line)

    ax_top.grid(True, alpha=0.3)
    ax_top.legend([l for l in lines], [l.get_label() for l in lines], loc="upper right", fontsize=9)

    # --- Static tooltip in top-left ---
    tooltip_text = ax_top.text(
        0.01, 0.95, "", transform=ax_top.transAxes,
        fontsize=9, verticalalignment="top",
        bbox=dict(boxstyle="round", fc="black", ec="white", lw=0.5, alpha=0.7),
        color="white"
    )

    locked = {"state": False, "x": None}
    vline = ax_top.axvline(x=0, color='grey', linestyle='--', lw=1, visible=False)

    def on_click(event):
        if event.inaxes == ax_top:
            locked["state"] = not locked["state"]
            if locked["state"]:
                locked["x"] = event.xdata
                vline.set_xdata(locked["x"])
                vline.set_visible(True)
            else:
                vline.set_visible(False)
            fig.canvas.draw_idle()

    def on_move(event):
        if locked["state"]:
            return
        if event.inaxes != ax_top:
            return
        xdata = event.xdata
        if xdata is None:
            return
        idx = min(range(len(rpm)), key=lambda i: abs(rpm[i] - xdata))
        text_lines = [f"RPM = {rpm[idx]:.0f}"]
        for label, unit, data, _ in series_data:
            text_lines.append(f"{label}: {data[idx]:.2f} {unit}")
        tooltip_text.set_text("\n".join(text_lines))
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_move)
    fig.canvas.mpl_connect("button_press_event", on_click)
    Cursor(ax_top, useblit=True, color='gray', lw=1)

    # --- Bottom panel: HP & Torque vs RPM ---
    ax_bottom.plot(rpm, hp, color="magenta")
    ax_bottom.set_ylabel("Est HP", color="magenta")
    ax_bottom.tick_params(axis='y', colors="magenta")
    ax_bottom.grid(True, alpha=0.3)

    ax2_bottom = ax_bottom.twinx()
    ax2_bottom.plot(rpm, torque, color="brown")
    ax2_bottom.set_ylabel("Est Torque (lb-ft)", color="brown")
    ax2_bottom.tick_params(axis='y', colors="brown")

    # --- Annotate peaks ---
    # HP peak
    hp_max = max(hp)
    idx_hp = hp.index(hp_max)
    rpm_hp = rpm[idx_hp]
    ax_bottom.plot(rpm_hp, hp_max, "o", color="magenta")
    ax_bottom.annotate(f"{hp_max:.0f} HP @ {int(rpm_hp)} RPM",
                       xy=(rpm_hp, hp_max), xytext=(rpm_hp, hp_max * 1.05),
                       ha='center', color="magenta", fontsize=9)

    # Torque peak
    torque_max = max(torque)
    idx_tq = torque.index(torque_max)
    rpm_tq = rpm[idx_tq]
    ax2_bottom.plot(rpm_tq, torque_max, "o", color="brown")
    ax2_bottom.annotate(f"{torque_max:.0f} lb-ft @ {int(rpm_tq)} RPM",
                        xy=(rpm_tq, torque_max), xytext=(rpm_tq, torque_max * 1.05),
                        ha='center', color="brown", fontsize=9)

    # Legend with peaks
    lines_bottom = [ax_bottom.lines[0], ax2_bottom.lines[0]]
    labels_bottom = [
        f"{int(hp_max)} HP @ {int(rpm_hp)} RPM",
        f"{int(torque_max)} lb-ft @ {int(rpm_tq)} RPM"
    ]
    ax_bottom.legend(lines_bottom, labels_bottom, loc="upper right", fontsize=9)

    plt.savefig(os.path.splitext(filepath)[0] + ".png")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_pull_rpm_peaks.py <Pull CSV file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    rows = read_csv(csv_path)
    rpm, load, speed, timing, maf = process_pull(rows)
    hp, torque = compute_derived(rpm, maf)

    series = [
        ("Load", "g/rev", load, "blue"),
        ("Timing", "°", timing, "orange"),
    ]

    interactive_plot(csv_path, rpm, series, hp, torque)
