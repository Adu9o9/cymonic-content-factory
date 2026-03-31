import os
from dotenv import load_dotenv
from crewai import Crew, Process
from core.agents import ContentFactoryAgents
from core.tasks import ContentFactoryTasks

load_dotenv()

dummy_source_text = """
Introducing the new SuperWidget 3000. It features a quantum processor and is generally very fast. 
It has 16GB of RAM and a battery that lasts all day, maybe even two days depending on how you use it. 
It's perfect for enterprise software developers who need high performance. We might add a cloud sync feature later this year.
"""

agents = ContentFactoryAgents()
tasks = ContentFactoryTasks()

# 1. Initialize Agents
researcher = agents.research_agent()
copywriter = agents.copywriter_agent()
editor = agents.editor_agent()

# 2. Initialize Tasks
extract_truth = tasks.extraction_task(researcher, dummy_source_text)
write_campaign = tasks.copywriting_task(copywriter, context_task=extract_truth)
audit_campaign = tasks.editing_task(editor, extract_truth, write_campaign)

# 3. Form the Crew
crew = Crew(
    agents=[researcher, copywriter, editor],
    tasks=[extract_truth, write_campaign, audit_campaign],
    process=Process.sequential, 
    verbose=True
)

print("Starting the Autonomous Content Factory - Full 3-Agent Test...")
result = crew.kickoff()

print("\n================================================")
print("FINAL EDITED OUTPUT")
print("================================================")
print(result)