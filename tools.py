"""
Job-assistant tools (all GPT-powered for now).
"""
import os, re, json, requests
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# ---------- helpers ------------------------------------------------
def _ask(prompt: str, max_tokens=400) -> str:
    return ai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    ).choices[0].message.content.strip()

# ---------- tool functions ----------------------------------------
def required_skills(job: str) -> list[str]:
    prompt = f"List 8–12 core skills or technologies commonly required for the role '{job}'. " \
             "Return just a comma-separated list."
    raw = _ask(prompt, 120)
    return [s.strip() for s in re.split(r",|\n|•|-", raw) if s.strip()]

def sample_resume(job: str, skills: list[str]) -> str:
    prompt = (
        "Create a one-page resume (Markdown) for an applicant targeting the role "
        f"'{job}'. Focus on these skills: {', '.join(skills)}.\n"
        "Sections: Summary | Key Skills | Experience | Education."
    )
    return _ask(prompt, 600)

def sample_cover(job: str, skills: list[str]) -> str:
    prompt = (
        f"Write a brief, personalized cover letter (<= 250 words) for a candidate "
        f"applying to a '{job}' role, highlighting these skills: {', '.join(skills)}."
    )
    return _ask(prompt, 350)

def search_jobs(query: str, location: str = "") -> list[dict]:
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    search_query = f"{query}{' in ' + location if location else ''}"
    
    querystring = {
        "query": search_query,
        "page": "1",
        "num_pages": "1",
        "country": "us",
        "date_posted": "all"
    }

    try:
        resp = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        # Handle HTTP errors
        if resp.status_code == 404:
            print(f"Error: Invalid endpoint - {resp.json().get('message')}")
            return _no_jobs(query, location)
        elif resp.status_code == 401:
            print("Error: Invalid API key or unauthorized access")
            return _no_jobs(query, location)
        
        # Check for empty or invalid responses
        if resp.status_code != 200 or not resp.text.strip():
            print(f"→ Non-200 ({resp.status_code}) or empty response")
            return _no_jobs(query, location)
            
        data = resp.json()
        
        # Extract job listings from response
        lst = data.get("data", [])  # Jsearch returns jobs under "data" key
        
        if not isinstance(lst, list):
            print("→ Response format invalid, expected list")
            return _no_jobs(query, location)
        
        # Process up to 10 job results
        jobs = []
        for item in lst[:10]:
            jobs.append({
                "title": item.get("job_title", ""),
                "company": item.get("employer_name", ""),
                "location": item.get("job_location", ""),
                "description": item.get("job_description", ""),
                "url": item.get("job_apply_link", ""),
                "date_posted": item.get("posted_at", ""),
            })
        
        return jobs or _no_jobs(query, location)
        
    except Exception as e:
        print("Error searching for jobs:", e)
        return _no_jobs(query, location)

def _no_jobs(query: str, location: str = "") -> list[dict]:
    """say no jobs found, so say didn't find any jobs"""
    return [{
        "title": f"No jobs found for '{query}'{' in ' + location if location else ''}",
        "company": "",
        "location": "",
        "description": "No job listings matched your search criteria.",
        "url": "",
        "date_posted": "",
    }]

def search_posts(job_title, company="", location=""):
    # Try most specific query first
    attempts = []
    if job_title and company and location:
        attempts.append([job_title, company, location])
    if job_title and company:
        attempts.append([job_title, company])
    if job_title and location:
        attempts.append([job_title, location])
    if job_title:
        attempts.append([job_title])
    # Add synonyms for posts
    synonyms = "(news OR discussion OR forum OR blog OR review OR post)"
    for terms in attempts:
        query = " ".join(terms + [synonyms])
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 5
        }
        resp = requests.get(url, params=params)
        results = resp.json()
        posts = []
        for item in results.get("items", []):
            posts.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", "")
            })
        if posts:
            return posts
    # If nothing found, return empty list
    return []

# ---------- dispatcher used by agent ------------------------------
def use_tool(name, *, memory, goal):
    if name == "skills":
        memory["skills"] = required_skills(goal)
        return memory["skills"]

    if name == "resume":
        skills = memory.get("skills") or required_skills(goal)
        memory["resume"] = sample_resume(goal, skills)
        return memory["resume"]

    if name == "cover":
        skills = memory.get("skills") or required_skills(goal)
        memory["cover"] = sample_cover(goal, skills)
        return memory["cover"]
        
    if name == "jobs":
        location = memory.get("location", "")
        memory["jobs"] = search_jobs(goal, location)
        return memory["jobs"]
    
    if name == "posts":
        job = goal
        company = memory.get("company", "")
        memory["posts"] = search_posts(job, company)
        return memory["posts"]

    raise ValueError(f"Unknown tool {name}")
