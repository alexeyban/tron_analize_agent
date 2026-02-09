from pathlib import Path
from crewai import Task, Crew
from agents.ingestion_agent.agent import ingestion_agent

BASE = Path(__file__).parent

SYSTEM_PROMPT = (BASE / "prompts/system.txt").read_text()
TASK_PROMPT = (BASE / "prompts/task_001_depth1.txt").read_text()

task = Task(
    description=TASK_PROMPT,
    agent=ingestion_agent,
    expected_output="""
A working Python ingestion module that fetches forward USDT transfers (depth=1),
with normalized output and at least one unit test.
"""
)

crew = Crew(
    agents=[ingestion_agent],
    tasks=[task],
    verbose=True,
    tracing=False,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== INGESTION RESULT ===\n")
    print(result)
