import csv
import os
import sys

# === Constants ===
THROTTLE_COL = "Throttle pedal (%)"
RPM_COL = "RPM"
TIME_COL = "Time (msec)"
MIN_WOT_DURATION_MS = 3000.0  # 3 seconds continuous
OUTPUT_DIR = "pulls"           # Subfolder for extracted pulls


def read_csv(filepath):
    """Read CSV and return (header, rows as list of dicts)."""
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)

    # Ignore last row (commonly malformed due to logger power loss)
    if rows:
        rows = rows[:-1]
    return header, rows


def find_wot_pulls(rows, filename):
    """
    Find continuous segments where Throttle pedal = 100.0
    lasting at least 3 seconds (based on Time (msec)).
    Return list of (start_idx, end_idx) pairs.
    """
    pulls = []
    start_idx = None

    for i, row in enumerate(rows):
        raw_throttle = row.get(THROTTLE_COL)

        # Detect missing throttle except for the last line (already skipped)
        if raw_throttle is None or raw_throttle == "":
            raise ValueError(
                f"Missing throttle value at line {i+2} in file '{filename}'. "
                "Only the last line may be malformed."
            )

        try:
            throttle = float(raw_throttle)
        except ValueError:
            raise ValueError(
                f"Invalid throttle value '{raw_throttle}' at line {i+2} in file '{filename}'."
            )

        if throttle == 100.0:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                # Segment ended
                start_time = float(rows[start_idx][TIME_COL])
                end_time = float(rows[i - 1][TIME_COL])
                duration = end_time - start_time
                if duration >= MIN_WOT_DURATION_MS:
                    pulls.append((start_idx, i - 1))
                start_idx = None

    # Handle case where file ends during WOT
    if start_idx is not None:
        start_time = float(rows[start_idx][TIME_COL])
        end_time = float(rows[-1][TIME_COL])
        duration = end_time - start_time
        if duration >= MIN_WOT_DURATION_MS:
            pulls.append((start_idx, len(rows) - 1))

    return pulls


def write_pull_csv(header, rows, start_idx, end_idx, pull_num, orig_filepath):
    """Write a new CSV file for the pull with descriptive name inside 'pulls/' subfolder."""
    start_rpm = int(float(rows[start_idx][RPM_COL]))
    end_rpm = int(float(rows[end_idx][RPM_COL]))
    base = os.path.basename(orig_filepath)
    dirname = os.path.dirname(orig_filepath)

    # Ensure output subdirectory exists
    output_dir = os.path.join(dirname, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    new_filename = f"Pull {pull_num} {start_rpm}-{end_rpm} RPM {base}"
    new_path = os.path.join(output_dir, new_filename)

    with open(new_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows[start_idx:end_idx + 1]:
            writer.writerow(row)

    print(f"Saved: {os.path.relpath(new_path, start=dirname)}")


def process_file(filepath):
    """Process one CSV file to extract and save WOT pulls."""
    header, rows = read_csv(filepath)
    pulls = find_wot_pulls(rows, filepath)

    if not pulls:
        print(f"No WOT pulls found in {os.path.basename(filepath)}")
        return

    for idx, (start, end) in enumerate(pulls, start=1):
        write_pull_csv(header, rows, start, end, idx, filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_wot_pulls.py <logfile.csv> [more.csv ...]")
        sys.exit(1)

    for file in sys.argv[1:]:
        # Skip files that are already in the 'pulls' subdirectory
        if os.path.basename(os.path.dirname(file)) == OUTPUT_DIR:
            continue
        try:
            process_file(file)
        except Exception as e:
            print(f"Error processing {file}: {e}")
