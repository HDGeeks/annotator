import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ----------------------------
# GLOBALS (loaded at runtime)
# ----------------------------
INPUT_PATH = None
OUTPUT_PATH = None
DATA_INPUT = []   # Original input file
DATA_OUTPUT = []  # Loaded output file rows (if present)
PROGRESS = 0
EMOTIONS = {}

# ----------------------------
# HELPERS
# ----------------------------
def load_jsonl(path):
    """Load a JSONL file into a list of dicts."""
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_jsonl(path, rows):
    """Rewrite the entire JSONL output file."""
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ----------------------------
# ROUTES
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    global INPUT_PATH, OUTPUT_PATH, DATA_INPUT, DATA_OUTPUT, PROGRESS, EMOTIONS

    if request.method == "POST":
        INPUT_PATH = request.form["input_path"]
        OUTPUT_PATH = request.form["output_path"]

        # Load input + existing output
        DATA_INPUT = load_jsonl(INPUT_PATH)
        DATA_OUTPUT = load_jsonl(OUTPUT_PATH)

        # Load emotion map
        with open("emotions.json", "r", encoding="utf-8") as f:
            EMOTIONS = json.load(f)

        # Where did they leave off?
        PROGRESS = len(DATA_OUTPUT)

        return redirect(url_for("annotate", row=PROGRESS))

    return render_template("index.html")


@app.route("/annotate", methods=["GET", "POST"])
def annotate():
    global DATA_INPUT, DATA_OUTPUT, PROGRESS

    row_index = request.args.get("row", type=int)
    if row_index is None:
        row_index = PROGRESS

    # End of dataset
    if row_index >= len(DATA_INPUT):
        return "🎉 All rows annotated. You’re done!"

    # -----------------------------------------
    # POST REQUEST → either Save or Navigate
    # -----------------------------------------
    if request.method == "POST":

        action = request.form.get("action", "save")  # save OR navigate

        # Navigation event → skip saving
        goto = request.form.get("goto_row", type=int)
        if action == "navigate":
            return redirect(url_for("annotate", row=goto))

        # SAVE EVENT → rewrite output row
        total_items = int(request.form["total_items"])
        edited_output = []

        for i in range(total_items):
            edited_output.append({
                "aspect": request.form.get(f"aspect_{i}"),
                "polarity": request.form.get(f"polarity_{i}"),
                "emotion": request.form.get(f"emotion_{i}")
            })

        # Construct saved entry
        new_entry = {
            "input": DATA_INPUT[row_index]["input"],
            "output": edited_output
        }

        # Write into output buffer at the correct row
        if row_index < len(DATA_OUTPUT):
            DATA_OUTPUT[row_index] = new_entry
        else:
            DATA_OUTPUT.append(new_entry)

        # Rewrite output file safely
        save_jsonl(OUTPUT_PATH, DATA_OUTPUT)

        # Update progress pointer
        if row_index >= PROGRESS:
            PROGRESS = row_index + 1

        # Move to next row automatically
        return redirect(url_for("annotate", row=row_index + 1))

    # -----------------------------------------
    # GET REQUEST → Load for display
    # -----------------------------------------

    # Load from OUTPUT if exists, else INPUT
    if row_index < len(DATA_OUTPUT):
        row = DATA_OUTPUT[row_index]
    else:
        row = DATA_INPUT[row_index]

    all_aspects = ["food","place","staff","service","miscellaneous","price","ambience","menu"]
    polarity_options = ["positive","negative","neutral"]

    return render_template(
        "annotate.html",
        idx=row_index,
        total=len(DATA_INPUT),
        row=row,
        emotions=EMOTIONS,
        aspects=all_aspects,
        polarity_options=polarity_options,
        row_index=row_index
    )


if __name__ == "__main__":
    app.run(debug=True)

    
# import json
# import os
# from flask import Flask, render_template, request, redirect, url_for

# app = Flask(__name__)

# # ----------------------------
# # GLOBALS (loaded at runtime)
# # ----------------------------
# INPUT_PATH = None
# OUTPUT_PATH = None
# DATA = []
# PROGRESS = 0
# EMOTIONS = {}

# # ----------------------------
# # HELPERS
# # ----------------------------
# def load_data(input_path):
#     lines = []
#     with open(input_path, "r", encoding="utf-8") as f:
#         for line in f:
#             if line.strip():
#                 lines.append(json.loads(line))
#     return lines

# def load_progress(output_path):
#     if not os.path.exists(output_path):
#         return 0
#     with open(output_path, "r", encoding="utf-8") as f:
#         return sum(1 for _ in f)

# def write_output(output_path, row):
#     with open(output_path, "a", encoding="utf-8") as f:
#         f.write(json.dumps(row, ensure_ascii=False) + "\n")

# # ----------------------------
# # ROUTES
# # ----------------------------

# @app.route("/", methods=["GET", "POST"])
# def index():
#     global INPUT_PATH, OUTPUT_PATH, DATA, PROGRESS, EMOTIONS

#     if request.method == "POST":
#         INPUT_PATH = request.form["input_path"]
#         OUTPUT_PATH = request.form["output_path"]

#         # Load main data
#         DATA = load_data(INPUT_PATH)

#         # Load emotion map
#         with open("emotions.json", "r", encoding="utf-8") as f:
#             EMOTIONS = json.load(f)

#         # Load where user left off
#         PROGRESS = load_progress(OUTPUT_PATH)

#         return redirect(url_for("annotate"))

#     return render_template("index.html")


# @app.route("/annotate", methods=["GET", "POST"])
# def annotate():
#     global PROGRESS

#     row_index = request.args.get("row", type=int)
#     if row_index is None:
#         row_index = PROGRESS

#     # All rows done?
#     if row_index >= len(DATA):
#         return "🎉 All rows annotated. You’re done!"

#     row = DATA[row_index]

#     if request.method == "POST":
#         edited_output = []

#         # Build updated annotations from form
#         total_items = int(request.form["total_items"])
#         for i in range(total_items):
#             aspect = request.form.get(f"aspect_{i}")
#             polarity = request.form.get(f"polarity_{i}")
#             emotion = request.form.get(f"emotion_{i}")

#             edited_output.append({
#                 "aspect": aspect,
#                 "polarity": polarity,
#                 "emotion": emotion
#             })

#         # append-only overwrite behavior
#         with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
#             f.write(json.dumps({
#                 "input": row["input"],
#                 "output": edited_output
#             }, ensure_ascii=False) + "\n")

#         next_row = request.form.get("goto_row", type=int)
#         if next_row is not None:
#             if next_row > PROGRESS:
#                 PROGRESS = next_row
#             return redirect(url_for("annotate", row=next_row))

#         PROGRESS += 1
#         return redirect(url_for("annotate"))

#     # Suggested emotion list for UI
#     all_aspects = ["food","place","staff","service","miscellaneous","price","ambience","menu"]
#     polarity_options = ["positive","negative","neutral"]

#     return render_template(
#         "annotate.html",
#         idx=row_index,
#         total=len(DATA),
#         row=row,
#         emotions=EMOTIONS,
#         aspects=all_aspects,
#         polarity_options=polarity_options,
#         row_index=row_index
#     )


# if __name__ == "__main__":
#     app.run(debug=True)