

# AI Job Assistant 💼

AI Job Assistant is an intelligent tool designed to help users find jobs, generate tailored resumes, and create personalized cover letters. It integrates modern generative AI with real-time job search data to streamline the job application process.

## Features

- **Task Planning:**  
  Break down the job search process into actionable tasks using the planner module.

- **Job Search Integration:**  
  Find matching job listings using the Google Jobs Scraper API (via RapidAPI).

- **Resume and Cover Letter Generation:**  
  Use OpenAI's API to generate tailored resumes and personalized cover letters based on the job title and required skills.

- **Skill Extraction:**  
  Automatically extract key skills required for the desired job using generative AI.

- **Streamlit UI:**  
  A user-friendly interface that displays the agent's thought process and outputs in real-time.

## Installation

Create a virtual environment and install the required packages:

```bash
python -m venv .venv 
# Windows: .venv\Scripts\activate
# Unix/macOS: source .venv/bin/activate
pip install -r requirements.txt
```



## Running the App

Start the Streamlit app using:

```bash
streamlit run app.py
```

Then view the app in your browser at the local URL provided by Streamlit.

## Overview

AI Job Assistant demonstrates the potential of integrated AI systems:
- **Planner Module:** Breaks the job search process into actionable tasks.
- **Tool Module:** Uses APIs to gather job data, generate resumes, and create cover letters.
- **ReAct Loop:** Displays each step (thought, action, and observation) in a transparent, interactive UI.

## License

Distributed under the MIT License. See `LICENSE` for more information.
