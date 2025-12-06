import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ----------------------------
# GLOBALS
# ----------------------------
INPUT_PATH = None
DATA = []            # dataset being annotated
PROGRESS = 0         # current annotation row
EMOTIONS = {}        # aspect → polarity → emotion list
GLOBAL_POS = []      # fallback global lists
GLOBAL_NEG = []
GLOBAL_NEU = []

PROGRESS_FILE = "progress.json"


# ----------------------------
# HELPERS
# ----------------------------
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def flatten_global_emotions(em_map):
    """Extract global emotion lists."""
    pos, neg, neu = set(), set(), set()
    for asp, groups in em_map.items():
        for pol, emos in groups.items():
            if pol == "positive":
                pos.update(emos)
            elif pol == "negative":
                neg.update(emos)
            elif pol == "neutral":
                neu.update(emos)
    return sorted(pos), sorted(neg), sorted(neu)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f).get("last_row", 0)
        except:
            return 0
    return 0


def save_progress(row):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_row": row}, f)


# ----------------------------
# ROUTES
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    global INPUT_PATH, DATA, PROGRESS, EMOTIONS
    global GLOBAL_POS, GLOBAL_NEG, GLOBAL_NEU

    if request.method == "POST":
        INPUT_PATH = request.form["input_path"]

        # Load dataset
        DATA = load_jsonl(INPUT_PATH)

        # Load emotion map
        with open("emotions.json", "r", encoding="utf-8") as f:
            EMOTIONS = json.load(f)

        GLOBAL_POS, GLOBAL_NEG, GLOBAL_NEU = flatten_global_emotions(EMOTIONS)

        # Resume from previous position
        PROGRESS = load_progress()

        return redirect(url_for("annotate", row=PROGRESS))

    return render_template("index.html")


@app.route("/annotate", methods=["GET", "POST"])
def annotate():
    global DATA, PROGRESS

    row_index = request.args.get("row", type=int)
    if row_index is None:
        row_index = PROGRESS

    # DONE
    if row_index >= len(DATA):
        return "🎉 All rows annotated!"

    # ----------------------
    # POST (save or navigate)
    # ----------------------
    if request.method == "POST":
        action = request.form.get("action", "save")
        goto = request.form.get("goto_row", type=int)

        # Navigation only
        if action == "navigate":
            return redirect(url_for("annotate", row=goto))

        # ----- SAVE -----
        total_items = int(request.form["total_items"])
        edited_output = []

        for i in range(total_items):
            edited_output.append({
                "aspect": request.form.get(f"aspect_{i}"),
                "polarity": request.form.get(f"polarity_{i}"),
                "emotion": request.form.get(f"emotion_{i}")
            })

        new_entry = {
            "input": DATA[row_index]["input"],
            "output": edited_output
        }

        DATA[row_index] = new_entry

        # save file
        save_jsonl(INPUT_PATH, DATA)

        # save progress
        save_progress(row_index + 1)

        return redirect(url_for("annotate", row=row_index + 1))

    # ----------------------
    # GET
    # ----------------------
    row = DATA[row_index]

    aspects = ["food","place","staff","service","miscellaneous","price","ambience","menu"]
    polarity_options = ["positive","negative","neutral"]

    return render_template(
        "annotate.html",
        idx=row_index,
        total=len(DATA),
        row=row,
        emotions=EMOTIONS,
        pos_list=GLOBAL_POS,
        neg_list=GLOBAL_NEG,
        neu_list=GLOBAL_NEU,
        aspects=aspects,
        polarity_options=polarity_options,
        row_index=row_index
    )


if __name__ == "__main__":
    app.run(debug=True)