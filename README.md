
# SO-Janitor-Agent 🤖

SO-Janitor-Agent is an autonomous agent designed to improve the quality of new questions on Stack Overflow. It monitors the stream of new questions for the top 50 most popular tags, identifies likely duplicates using a semantic search model, and proposes existing high-quality answers to help new users.

The core of the project is a machine learning model trained on a "golden dataset" of nearly 900,000 high-quality questions, extracted and processed from the official Stack Exchange data dump.

---

## ✨ How It Works

The agent operates on a fully automated, serverless workflow:

1.  **Trigger (n8n):** A Cron job kicks off the workflow every 5 minutes.
2.  **Fetch (n8n):** An HTTP request is made to the Stack Exchange API to get the latest questions.
3.  **Analyze (Cloud Run):** Each new question is sent to a FastAPI endpoint running on Google Cloud Run. The semantic search model finds the most likely duplicate from the golden dataset.
4.  **Act (n8n):** If a high-confidence match is found, the agent posts a notification to a Slack channel for human review.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI
- **Data Processing:** Pandas, lxml
- **Machine Learning:** PyTorch, Sentence-Transformers, Faiss
- **Deployment:** Docker, Google Cloud Run
- **Automation:** n8n

---

## 🚀 Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Pooqdmk/SO-Janitor-Agent.git
cd SO-Janitor-Agent
````

### 2\. Set Up the Python Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment named 'agent'
python -m venv agent

# Activate the environment
# On Windows:
.\agent\Scripts\activate
# On macOS/Linux:
source agent/bin/activate
```

### 3\. Install Dependencies

All required libraries are listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4\. Download the Processed Dataset (IMPORTANT)

The "golden dataset" is required for the agent to function, but it is too large to be stored in Git. Download it from the link below and place it in the correct directory.

  - **Download File:** `top_50_tags_golden_questions.parquet`
  - **Download Link:** `https://drive.google.com/file/d/12l_MKJ_Khg8e_p56Vp80ZEuoCxslTdha/view?usp=sharing`
  - **Destination Folder:** After downloading, place the file inside the `data/processed/` directory.

Your final file path should be: `SO-Janitor-Agent/data/processed/top_50_tags_golden_questions.parquet`.

-----

## ⚙️ Usage

Once the setup is complete, you can run the different components of the project.

### 1\. Create the AI Model and Index

Before running the API for the first time, you need to generate the semantic search index from the golden dataset.

```bash
python src/scripts/2_create_index.py
```

This will create the `faiss_index.bin` and `id_map.pkl` files in your root directory.

### 2\. Run the API Server Locally

To test the agent's "brain," you can run the FastAPI server on your local machine.

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

-----

## 📂 Project Structure

```
SO-Janitor-Agent/
│
├── data/
│   ├── raw/              # (Ignored by Git) Raw data dump
│   └── processed/        # (Ignored by Git) Processed golden dataset
│
├── src/
│   ├── scripts/          # Scripts for data processing, model creation, etc.
│   └── main.py           # The main FastAPI application
│
├── .gitignore            # Specifies files and folders to be ignored by Git
├── requirements.txt      # A list of all Python dependencies
└── README.md             # This file
```

-----

## 🤝 Contributing

Contributions, issues, and feature requests are welcome\! Feel free to check the issues page.

```
```

