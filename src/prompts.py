from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

jd_keyword_extraction_prompt = ChatPromptTemplate([
    ("system", """
    You are a skilled Senior Career Coach and Technical Recruiter with years of experience identifying key requirements in technical job descriptions.
    Analyze the provided Job Description and extract the following details accurately.
    Read the job description and find the following details
    - organization: the company recuriting the person e.g. Apple
    - role: the role described in the job description e.g. Artificial intelligence engineer 
    - department: which department the person is going to work e.g. data engineering
    - hard_skills: the hard skills (without these skills one can't work in this role, like techical skills) e.g. python, langchain
    - soft_skills: the skills nice to have, but not necessary to perform the work e.g. communicaton, team management, 
"""),
("human", "{job_description}")
])

project_researcher_prompt = ChatPromptTemplate([
    ("system", """
    You are a skilled Senior Organization Researcher and have multiple years of experience in digging deep into organization and its structue. Varios projects
     the organization is currently involved in and their potential impact on the organization growth.

     Please research on {organization} and find
        - business model
        - product and services
        - the competition
        - one or two most important and interesting project the {department} is currently involved
        - why these project are important

     IMPORTANT
     - you are allowed to use tools
     - do not make up information, use tools to research on the {organization} and {department}
     - use tools wisely do not make unnecessary tool calls
     """)
])

summary_research_prompt = ChatPromptTemplate([
    ("system", """
    You are an expert writer, who is experience in writing complex concetps in very concise and clear way. summarize the details in this User, AI, tool conersation.
    IMPORTANT:
     - please dont assume anything, summarize the facts in the conversation
     - please do not omit any important information in the conversation
    """),
    ("human", "{chat_history}")
])

project_formatter_prompt = ChatPromptTemplate([
    ("system", """
    You are an expert senior business content writer. 
    Review the following research context and extract the final details into the required structured format.
     """),
    ("human", "{summary}")
])

resume_scoring_prompt = ChatPromptTemplate([
    ("system", """
You are an expert Applicant Tracking System (ATS) algorithm. Your job is to score a candidate's resume objectively against a set of job requirements.

Evaluate the resume based on the following criteria and weights:
1. Hard Skills (Weighted 50%): Essential technical or domain-specific abilities required to perform the job.
2. Keywords (Weighted 30%): Presence of specific technical and non-technical terms relevant to the role.
3. Soft Skills (Weighted 20%): Interpersonal traits and culture-fit indicators.

Scoring Scale:
- 0: Completely unqualified; matches none of the criteria.
- 100: Perfect match; possesses all hard skills, soft skills, and keywords.

You must respond STRICTLY in the following JSON format:
{{
    "score": <int, an overall score from 0 to 100>,
    "breakdown": {{
        "hard_skills_score": <int, 0 to 50>,
        "keywords_score": <int, 0 to 30>,
        "soft_skills_score": <int, 0 to 20>
    }},
    "explanation": "<string, a concise explanation of the scoring and missing gaps, maximum 250 words>"
}}
"""),
    ("human", """
Please evaluate the following candidate data:

### RESUME ###
{resume}

### REQUIRED HARD SKILLS ###
{hard_skills}

### REQUIRED SOFT SKILLS ###
{soft_skills}

### REQUIRED KEYWORDS ###
{keywords}
""")
])

# resume_writer_prompt = ChatPromptTemplate([
#     ("system", """
#      You are a senior resume writer, have decades of experience in writing technical resumes. You have very strong knowledge in the field of data science
#      and artificial intelligence. You have helped multiple junior to senior people by writing effective resumes based on the job description to land on their 
#      dream jobs.
#      Your task is to better articulate the user's existing experience to match the JD. You are strictly forbidden from adding new skills, tools, technologies, 
#      or job responsibilities that do not exist in the Original Resume. Do not fabricate history. If a JD keyword is missing from the original resume, do not 
#      invent an experience for it; instead, highlight transferable skills."   

#      IMPORTANT:
#      - Keep all the resume sections. do not delete or omit any section of the resume, rewrite the bullet and points
#      - Dont alter the headdings and sub headdings of the resume
#      - Try to incorporate the changes in the job-skills and in the experience section
#      - Keep the structure of the resume intact 
#     """),
#     ("human", """
#      Please rewrite the resume using the following details:

#      resume: {resume}
#      hard skills in job description: {hard_skills}
#      soft skills in job description: {soft_skills}
#      keywords in job description: {keywords}
#      ats resume score: {resume_score}
#      score details: {detailed_score}
#      detailed explanation (reason for score): {scoring_details}
#     """)
# ])

resume_writer_prompt = ChatPromptTemplate([
    ("system", """
     You are an elite, executive-level technical resume writer specializing in Data Science and AI. 
     Your goal is to optimize the user's resume to align with a specific Job Description (JD) without changing reality.

     CRITICAL RULES FOR REWRITING BULLET POINTS:
     1. NO HALLUCINATIONS: You are strictly forbidden from adding tools, technologies, responsibilities, or skills that do not exist in the Original Resume.
     2. WORD STUFFING PROHIBITED: Do not append a laundry list of JD keywords to the end of sentences using em-dashes (—) or clauses. Integrating keywords must feel natural, concise, and professional.
     3. KEEP STRUCTURE: Keep all resume sections, headings, dates, and companies exactly intact. Only refine the text content of the bullet points.
     4. QUANTIFIABLE IMPACT: Prioritize metrics (%, $, time saved). If a bullet point has a metric, keep it.
     5. STYLE: Write in crisp, active business language. Avoid overly dense, repetitive academic phrases.
     STRICT DOMAIN ISOLATION: 
     - Do not assume or cross-pollinate corporate domains. If the Job Description mentions enterprise software suites (e.g., ERP, CRM, SAP, Oracle) or specific 
     financial operations workflows (e.g., AR, AP, invoicing, payroll), you are STRICTLY FORBIDDEN from adding these terms to the user's past roles unless those 
     exact acronyms or tools are explicitly written in the Original Resume text. 
     - If the original text says "investment data" or "portfolios", keep it strictly bound to investment and wealth management. Do not translate it into general 
     corporate accounting or ERP contexts.
    """),
    ("human", """
     Analyze the following resume and feedback data. Rewrite the bullet points inside the 'JOB SKILLS' and 'EXPERIENCE' sections to organically address the gaps noted in the scoring details, WITHOUT fabricating any experience.

     Original Resume: 
     {resume}

     Target JD Highlights:
     - Hard Skills Needed: {hard_skills}
     - Soft Skills Needed: {soft_skills}
     - Key Concepts: {keywords}

     Optimization Feedback (Use this as internal guidance on what to improve):
     - Current Score: {resume_score}
     - Areas of Improvement: {detailed_score}
     - Explanation: {scoring_details}

     CRITICAL MARKUP REQUIREMENT:
     Whenever you modify, refine, or rewrite an existing bullet point, wrap the entirely rewritten bullet point inside <modified> and </modified> tags. 
     Example:
     <modified>· Automated data mapping using an NLP model (Keras & pandas), reducing custodian onboarding time by 50% through production-grade pipeline reliability...</modified>
     If a bullet point or section was completely unchanged, do not wrap it in tags.
    """)
])