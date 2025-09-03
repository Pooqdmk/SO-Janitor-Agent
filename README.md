
SO-Janitor-Agent 🤖
===================

SO-Janitor-Agent is an autonomous agent designed to improve the quality of new questions on Stack Overflow. It monitors the stream of new questions for the top 50 most popular tags, identifies likely duplicates using a semantic search model, and proposes existing high-quality answers to help new users.

The core of the project is a machine learning model trained on a "golden dataset" of nearly 900,000 high-quality questions, extracted and processed from the official Stack Exchange data dump.

✨ How It Works
--------------

The agent leverages a multi-stage, serverless architecture to provide real-time analysis and assistance.

1.  **Scheduled Trigger (n8n):** A Cron job acts as the agent's heartbeat, waking it up every 5 minutes to check for new activity.

2.  **Data Ingestion (n8n):** The workflow fetches the latest questions from the Stack Exchange API for the top 50 most popular tags.

3.  **Semantic Analysis (Cloud Run):** Each new question is sent to a dedicated FastAPI endpoint. Here, the core AI model converts the question's text into a vector embedding and uses a FAISS index to find the most conceptually similar questions from the golden dataset in milliseconds.

4.  **Human-in-the-Loop Action (n8n):** The agent uses an advanced scoring system to gauge its confidence. If a match has a high similarity score (>90%), a notification is posted to a dedicated Slack channel, allowing human moderators to review the suggestion before it's posted publicly. This ensures quality and prevents spam.

🧠 Methodology & Key Concepts
-----------------------------

The effectiveness of this agent is built on a foundation of careful data processing and modern machine learning techniques.

### The Data Funnel: From 60 Million to 885k

To ensure the agent learns from the best possible examples, we refined the massive Stack Exchange data dump through a strict filtering process:

-   **Start:** Began with over 60 million raw posts.

-   **Filter 1 (Post Type):** Selected only questions, reducing the pool to ~24 million.

-   **Filter 2 (Relevance):** Identified the top 50 most common tags to focus on the most active parts of the community.

-   **Filter 3 (Quality):** Kept only questions that were **a)** tagged with a top-50 tag, **b)** had a high score (**> 5**), and **c)** had an **accepted answer**.

-   **Result:** A "golden dataset" of 885,116 high-quality, canonical questions.

### Semantic Search vs. Keyword Search

This agent does not simply match keywords. It uses **semantic search** to understand the *intent* behind a question.

-   **How it works:** We use a `Sentence-Transformer` model to convert every question into a 384-dimensional vector. This vector is a numerical "fingerprint" of the question's meaning.

-   **Why it's better:** This allows the agent to find duplicates that use different wording but describe the same problem, something a keyword search would miss.

### High-Speed Indexing with FAISS

To search through nearly a million vectors instantly, we use **FAISS (Facebook AI Similarity Search)**. It creates a pre-compiled index of all vectors, enabling the agent to find the top 5 most similar questions in under 100 milliseconds.

🛠️ Tech Stack
--------------

-   **Backend:** **Python** & **FastAPI** to build a high-performance, scalable API for our model.

-   **Data Processing:** **Pandas** & **lxml** to efficiently parse and filter the massive 100GB+ XML data dump.

-   **Machine Learning:**

    -   **Sentence-Transformers:** To generate meaningful vector embeddings from text.

    -   **Faiss:** For building a highly efficient, high-speed similarity search index.

-   **Deployment:** **Docker** for containerizing the application and **Google Cloud Run** for serverless, auto-scaling deployment.

-   **Automation:** **n8n** to orchestrate the entire workflow, from data fetching to analysis and alerting.

🚀 Setup and Installation
-------------------------

Follow these steps to get the project running on your local machine.

### 1\. Clone the Repository

```
git clone [https://github.com/Pooqdmk/SO-Janitor-Agent.git](https://github.com/Pooqdmk/SO-Janitor-Agent.git)
cd SO-Janitor-Agent

```

### 2\. Set Up the Python Virtual Environment

```
# Create a virtual environment named 'agent'
python -m venv agent

# Activate the environment
# On Windows:
.\agent\Scripts\activate
# On macOS/Linux:
source agent/bin/activate

```

### 3\. Install Dependencies

```
pip install -r requirements.txt

```

### 4\. Download the Processed Dataset (IMPORTANT)

The "golden dataset" is required for the agent to function. Download it from the link below and place it in the correct directory.

-   **Download File:** `top_50_tags_golden_questions.parquet`

-   **Download Link:** `https://drive.google.com/file/d/12l_MKJ_Khg8e_p56Vp80ZEuoCxslTdha/view?usp=sharing`

-   **Destination Folder:** After downloading, place the file inside the `data/processed/` directory.

⚙️ Local Development & Usage
----------------------------

### 1\. Create the AI Model and Index

Before running the API for the first time, generate the search index from the golden dataset.

```
python src/scripts/4_create_search_index.py

```

This will create the `faiss_index.bin` and `id_map.pkl` files in your `models/` directory.

### 2\. Run the API Server Locally

To test the agent's "brain," run the FastAPI server on your local machine.

```
uvicorn src.main:app --reload

```

The API is available at `http://127.0.0.1:8000`. Access the interactive documentation at `http://127.0.0.1:8000/docs`.

☁️ Deployment to Cloud Run
--------------------------

To make the agent available 24/7, deploy the FastAPI application as a serverless container on Google Cloud Run.

### 1\. Prerequisites

-   Install [Docker Desktop](https://www.docker.com/products/docker-desktop/ "null").

-   Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install "null").

### 2\. Create the `Dockerfile`

Create a file named `Dockerfile` in the root of your project with the following content:

```
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code and model files into the container
COPY ./src ./src
COPY ./models ./models

# Command to run the application using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

```

### 3\. Build, Push, and Deploy

Run the following commands in your terminal, replacing `[YOUR_PROJECT_ID]` with your Google Cloud Project ID.

```
# Enable the necessary services
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create a repository to store your image
gcloud artifacts repositories create so-janitor-repo --repository-format=docker --location=us-central1

# Build, tag, and push the container image
gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/so-janitor-repo/so-janitor-agent

# Deploy to Cloud Run
gcloud run deploy so-janitor-agent\
  --image=us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/so-janitor-repo/so-janitor-agent\
  --platform=managed\
  --region=us-central1\
  --allow-unauthenticated

```

After deployment, Google Cloud will provide a public **Service URL** for your API.

🤖 Automation with n8n
----------------------

The final step is to create the n8n workflow that calls your deployed API.

1.  **Trigger:** Use a **Cron Node** set to run every 5 minutes (`*/5 * * * *`).

2.  **Fetch Questions:** Use an **HTTP Request Node** to call the Stack Exchange API and get the latest questions.

3.  **Analyze Question:** Use another **HTTP Request Node** to send each new question to your public Cloud Run **Service URL**.

4.  **Decision:** Use a **Switch Node** to check if the `similarity_percent` from your API is greater than a threshold (e.g., 90).

5.  **Act:** On the "true" path of the Switch, use a **Slack Node** to send a formatted message to your review channel.

📂 Project Structure
--------------------

```
SO-Janitor-Agent/
│
├── data/
│   └── processed/        # (Ignored by Git) Processed golden dataset
│
├── models/               # (Ignored by Git) Saved FAISS index and ID map
│
├── src/
│   ├── scripts/          # Scripts for data processing, model creation, etc.
│   └── main.py           # The main FastAPI application
│
├── .gitignore            # Specifies files and folders to be ignored by Git
├── Dockerfile            # Instructions to build the container image
├── requirements.txt      # A list of all Python dependencies
└── README.md             # This file

```

🤝 Contributing
---------------

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
