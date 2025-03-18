# reguai

## Overview  
Regulatory AI Agent is an AI-powered solution designed to improve regulatory compliance by monitoring, analyzing, and summarizing legal updates. It minimizes manual effort, enhances decision-making, and ensures organizations remain compliant with ever-evolving regulations.  

## Staying Ahead of Regulatory Changes  
Keeping up with legal updates is a complex and time-consuming task. This AI-driven agent automates regulatory tracking, delivering precise and timely insights. By providing summaries and actionable recommendations, it helps organizations quickly adapt to new requirements and reduce compliance risks.  

## Intelligent Monitoring & Adaptation  
- **Automated Regulatory Updates**: Identifies and summarizes legal and compliance changes, reducing reliance on manual tracking.  
- **Context-Aware Insights**: Interprets how new regulations impact existing policies and operational workflows.  
- **Reliable Decision Support**: Ensures accuracy and relevance by flagging misinformation and verifying sources.  

## Seamless User Experience  
- **Effortless Navigation & Accessibility**: Designed for professionals with varying levels of technical expertise, ensuring intuitive interaction.  
- **Clear & Transparent Information**: Regulatory updates are presented with structured explanations and linked references for easy validation.  
- **Engaging & Interactive**: Users can query specific regulations, receive instant responses, and explore real-time compliance insights in an interactive format.  

A real-time multimodal RAG agent powered by Gemini, supporting audio/video/text chat with vector DB-backed responses

Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack)

## Project Structure

This project is organized as follows:

```
reguai/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── server.py        # FastAPI Backend server
│   └── utils/           # Utility functions and helpers
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
└── pyproject.toml       # Project dependencies and configuration
```

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


### Installation

Install required packages using uv:

```bash
make install
```

### Setup

If not done during the initialization, set your default Google Cloud project and Location:

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export LOCATION="us-central1"
gcloud config set project $PROJECT_ID
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT_ID
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment with backend and frontend |
| `make backend`       | Start backend server only |
| `make ui`            | Launch Streamlit frontend without local backend |
| `make test`          | Run unit and integration tests                                                              |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)                                             |
| `uv run jupyter lab` | Launch Jupyter notebook                                                                     |

For full command options and usage, refer to the [Makefile](Makefile).


## Usage

1.  **Install Dependencies:**

    ```bash
    make install
    ```

2.  **Start the Backend and Frontend:**

    **Backend:**
    ```bash
    make backend
    ```
    
    The backend will be ready when you see `INFO:     Application startup complete.` in the console.

    <details>
    <summary><b>Click here if you want to use AI Studio and API Key instead of Vertex AI:</b></summary>

    ```bash
    export VERTEXAI=false
    export GOOGLE_API_KEY=your-google-api-key
    ```

    </details>
    <br>
    
    **Frontend:**
    ```bash
    # In a different shell
    make ui
    ```

    This is the suggested mode for development as it allows you to see changes in real-time.

3.  **Interact with the Agent**
    Once both the backend and frontend are running, click the play button in the frontend UI to establish a connection with the backend. You can now interact with the Multimodal Live Agent! You can try asking questions such as "Using the tool you have, define Governance in the context MLOPs" to allow the agent to use the documentation it was provided to.

**Remote access**:
Use [Cloud Run proxy](https://cloud.google.com/sdk/gcloud/reference/run/services/proxy) for local access. The backend will be accessible at `http://localhost:8000`:

   ```bash
   gcloud run services proxy genai-app-sample --port 8000 --project $PROJECT_ID --region $REGION
   ```

   You can then use the same frontend setup described above to interact with your Cloud Run deployment.

<details>
<summary><b>Cloud Shell usage</b></summary>

To use the `multimodal_live_api` agent in Cloud Shell, follow these steps:

1.  **Start the Frontend:**

    ```bash
    make ui
    ```

    You may be prompted to run the app on a different port if port 3000 is in use. Accept by pressing Enter. You'll see a message similar to:

    ```
    You can now view multimodal-live-api-web-console in the browser.

      Local:            http://localhost:3001
      On Your Network:  http://10.88.0.4:3001
    ```

    Click the `localhost` link to open a web preview in Cloud Shell.

2.  **Start the Backend:**

    Open a *new* Cloud Shell terminal tab. Remember to set your Cloud Platform project in this new session using `gcloud config set project [PROJECT_ID]`. Then from the root of the repository, run:

    ```bash
    make backend
    ```

3.  **Configure Web Preview for the Backend:**

    Trigger a web preview for port 8000 - you'll need to change the default port which is `8080`.  See [Cloud Shell Web Preview documentation](https://cloud.google.com/shell/docs/using-web-preview#preview_the_application) for details.

4.  **Connect Frontend to Backend:**

    *   The web preview will open a new tab in your browser. Copy the URL from the address bar (e.g., `https://8000-cs-8a3189b8-5295-4085-9893-c318f1724456.ql-europe-west1-ojep.cloudshell.dev/?authuser=0`).
    *   Return to the frontend preview tab (from step 1).
    *   Paste the copied URL into the frontend's "Server URL" connection settings.
    *   Click the "Play button" to connect. Start interacting with it!

*   When using Cloud Shell there is a known limitation when using the feedback feature in the Frontend. Feedback submission might fail due to different origins between the frontend and backend in the Cloud Shell environment.
</details>

## Deployment

### Dev Environment

The repository includes a Terraform configuration for the setup of the Dev Google Cloud project.
See [deployment/README.md](deployment/README.md) for instructions.

### Production Deployment

The repository includes a Terraform configuration for the setup of a production Google Cloud project. Refer to [deployment/README.md](deployment/README.md) for detailed instructions on how to deploy the infrastructure and application.

## Monitoring and Observability

>> You can use [this Looker Studio dashboard](https://lookerstudio.google.com/c/reporting/fa742264-4b4b-4c56-81e6-a667dd0f853f/page/tEnnC) template for visualizing events being logged in BigQuery. See the "Setup Instructions" tab to getting started.

The application uses OpenTelemetry for comprehensive observability with all events being sent to Google Cloud Trace and Logging for monitoring and to BigQuery for long term storage. 
