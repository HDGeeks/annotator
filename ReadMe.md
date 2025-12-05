

📝 README.md — Annotation Tool

A modern, browser-based annotation tool for labeling aspect, polarity, and emotion in text reviews.
Built with a sleek Flask + Bootstrap interface, automatic progress tracking, and support for custom emotion taxonomies.

⸻

🚀 Features
	•	🔹 Clean, modern annotation UI
	•	🔹 Auto-resume from your last saved annotation
	•	🔹 Input + output folder support
	•	🔹 JSONL processing
	•	🔹 Emotion selection filtered by aspect
	•	🔹 Outputs saved safely without overwriting
	•	🔹 Super lightweight (Flask only)

⸻

📂 Project Structure

annotator/
│
├── app.py
├── requirements.txt
├── emotions.json
│
├── input/
│   └── your_input_file.jsonl
│
├── output/
│   └── your_output_file.jsonl   (auto-created)
│
└── templates/
    ├── index.html
    └── annotate.html


⸻

⚙️ Installation & Setup

Follow these steps exactly to ensure the tool runs correctly.

⸻

1️⃣ Create & Activate a Virtual Environment

macOS / Linux

cd annotator
python3 -m venv venv
source venv/bin/activate

Windows (PowerShell)

cd annotator
python -m venv venv
venv\Scripts\activate


⸻

2️⃣ Install Required Packages

pip install -r requirements.txt

This installs:
	•	Flask
	•	Jinja2
	•	Werkzeug

Nothing heavy, nothing extra.

⸻

📥 3️⃣ Add Your Input File

Place your JSONL dataset inside the input/ folder:

annotator/input/my_reviews.jsonl

Each line must be valid JSON, e.g.:

{"input": "The food was great!", "output": []}


⸻

📤 4️⃣ Prepare Your Output Path

You don’t need to create the file.

Just choose a filename, for example:

annotator/output/my_annotations.jsonl

The tool will create it automatically and append annotations safely.

⸻

▶️ 5️⃣ Run the Annotation Tool

python app.py

Then open the app in your browser:

http://127.0.0.1:5000


⸻

🖱️ 6️⃣ Using the Web Interface
	1.	Enter input file path (example):

./input/my_reviews.jsonl


	2.	Enter output file path:

./output/my_annotations.jsonl


	3.	Click Start Annotation.
	4.	For each review:
	•	Choose the aspect
	•	Choose the polarity
	•	Choose the emotion (UI filters appropriate emotions)
	•	Click Save & Next →

Your progress is saved line by line.
If you restart the app, it picks up exactly where you stopped.

⸻

📄 Output Format

Each annotation is stored as one JSONL entry:

{
  "input": "The food was amazing but the service was slow.",
  "output": [
    {"aspect": "food", "polarity": "positive", "emotion": "joy"},
    {"aspect": "service", "polarity": "negative", "emotion": "annoyance"}
  ]
}


⸻

🛑 Stopping & Continuing Later

Just close the browser or stop the terminal.

To continue later:

source venv/bin/activate   # or Windows equivalent
python app.py

Select the same input/output paths → annotation resumes automatically.


