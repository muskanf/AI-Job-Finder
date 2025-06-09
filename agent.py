"""
ReAct loop for the Job Assistant.
"""
import os, json, sys
from typing import Callable, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from planner import generate_tasks
import tools

load_dotenv()
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


def parse_cover_letter(cover_md):
    """Parse the Markdown cover letter into sections."""
    sections = {}
    current = None
    lines = cover_md.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            current = line.replace("##", "").strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    # Join lines for each section
    for k in sections:
        sections[k] = "\n".join(sections[k]).strip()
    return sections

def parse_resume(resume_md):
    """Parse the Markdown resume into sections."""
    sections = {}
    current = None
    lines = resume_md.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            current = line.replace("##", "").strip()
            sections[current] = []
        if line.startswith("# "):
            # Top-level header, use as name
            current = "contact"
            sections[current] = [line.replace("#", "").strip()]
        elif current:
            sections[current].append(line)
    # Join lines for each section
    for k in sections:
        sections[k] = "\n".join(sections[k]).strip()
    return sections

def run_agent(job_title: str, log: Callable[[str], None] = print):
    log(f"PLAN: tasks for → {job_title}")
    tasks = generate_tasks(job_title)
    memory: Dict[str, Any] = {}

    for task in tasks:
        log(f"\nTHOUGHT: {task['thought']}")
        output = tools.use_tool(task["tool"], memory=memory, goal=job_title)
        memory[task["tool"]] = output
        log(f"OBSERVE: {str(output)[:600]}")

    

    log("\nFINISH.")

    return memory

if __name__ == "__main__":
    md, _ = run_agent("Data Analyst")
    print(md)
