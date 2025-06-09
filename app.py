import streamlit as st
from dotenv import load_dotenv
from agent import run_agent
from agent import parse_resume
from agent import parse_cover_letter
import urllib.parse
load_dotenv()
import re

st.set_page_config(page_title="Job Assistant", layout="wide")
st.title("💼 AI Job Assistant")


def clean_text(text):
    if not isinstance(text, str):
        return text
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

job = st.text_input("🔎︎ Desired Job Title")

if st.button("Generate") and job.strip():
    trace = st.empty()
    buf = []

    def logger(line):
        buf.append(line)
        trace.text_area("Agent Trace", "\n".join(buf), height=300)

    memory = run_agent(job, log=logger)

    st.success("Job search completed! Here are the results:")
    if "jobs" in memory and memory["jobs"]:
        st.markdown("## 🔎︎ Job Listings")
        for i, job in enumerate(memory["jobs"]):
            title = clean_text(job['title'])
            company = clean_text(job['company'])
            location = clean_text(job['location'])
            salary = clean_text(job.get('salary', ''))
            description = clean_text(job['description'][:300] + "...")
            with st.expander(f"{i+1}. {title} at {company}"):
                st.markdown(f"### {title}", unsafe_allow_html=True) 
                st.write(f"**Company:** {company}")
                st.write(f"**Location:** {location}")
                if job.get('date_posted'):
                    st.write(f"**Posted:** {job['date_posted']}")
                st.write(description)
                if job.get('url'):
                    st.markdown(f"[Apply Here]({job['url']})")
    if "posts" in memory and memory["posts"]:
        st.markdown("## 📝 Related Posts for This Job")
        for event in memory["posts"]:
            st.markdown(f"**{event['title']}**  \n{event['snippet']}  \n[More Info]({event['link']})")

    st.markdown("\n\n")
    if "resume" in memory and memory["resume"]:
        st.markdown("## 📄 Sample Resume")
        resume_sections = parse_resume(memory["resume"])
        contact_lines = []
        for line in memory["resume"].splitlines():
            if line.strip().startswith("##"):
                break
            if line.strip().lower() in {"summary", "key skills", "experience", "education", "---"}:
                continue
            if line.strip():
                # Remove leading '#' if present
                contact_lines.append(line.strip().replace("#", "").strip())
        # Remove code block markers if present
        if contact_lines and contact_lines[0].startswith("```"):
            contact_lines[0] = contact_lines[0].replace("```markdown", "").replace("```", "").strip()
        if contact_lines and contact_lines[-1].endswith("```"):
            contact_lines[-1] = contact_lines[-1].replace("```", "").strip()
        if contact_lines:
            for line in contact_lines:
                st.markdown(f"**{line}**")
        if "Summary" in resume_sections:
            st.write(resume_sections["Summary"])
        if "Key Skills" in resume_sections:
            st.write(resume_sections["Key Skills"])
        if "Experience" in resume_sections:
                st.write(resume_sections["Experience"])
        if "Education" in resume_sections:
            education_lines = [
                line for line in resume_sections["Education"].splitlines()
                if "references available upon request" not in line.lower()
            ]
            # Remove trailing code block markers, horizontal rules, or blank lines
            while education_lines and education_lines[-1].strip() in {"```"}:
                education_lines = education_lines[:-1]
            st.write("\n".join(education_lines))


    if "cover" in memory:
        if memory["cover"]:
            st.markdown("## ✉️ Sample Cover Letter")
            cover_sections = parse_cover_letter(memory["cover"])
            if cover_sections:
                for section, content in cover_sections.items():
                    st.markdown(f"#### {section}")
                    st.write(content)
            else:
                st.write(memory["cover"])
        else:
            st.warning("No cover letter was generated.")

   
        
else:
    st.info("Type a job title and press **Generate**.")
