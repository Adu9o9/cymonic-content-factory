import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

class ContentFactoryAgents:
    def __init__(self):
        # Using Google's OpenAI-compatible endpoint to bypass native SDK crash loops
        self.base_llm = LLM(
            model="openai/gemini-3.8-flash",
            api_key=os.environ.get("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.writer_llm = LLM(
            model="openai/gemini-3.8-flash",
            api_key=os.environ.get("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def research_agent(self):
        return Agent(
            role='Researcher',
            goal='Extract product facts and flag ambiguous claims.',
            backstory='Analytical researcher strictly finding facts in raw text. CRITICAL: DO NOT output <think> tags or your internal reasoning process. Output ONLY the final requested format.',
            verbose=True,
            allow_delegation=False,
            llm=self.base_llm,
            max_iter=1
        )

    def copywriter_agent(self):
        return Agent(
            role='Copywriter',
            goal='Write a Blog Post, Social Strategy, and Email Teasers using only verified facts.',
            backstory='Creative marketer who strictly follows fact-sheets. CRITICAL: DO NOT output <think> tags or your internal reasoning process. Output ONLY the final requested format.',
            verbose=True,
            allow_delegation=False,
            llm=self.writer_llm,
            max_iter=1
        )

    def editor_agent(self):
        return Agent(
            role='Editor-in-Chief',
            goal='Remove unverified Red Flag claims from marketing drafts.',
            backstory='Ruthless editor ensuring zero hallucinations. CRITICAL: DO NOT output <think> tags or your internal reasoning process. Output ONLY the final requested format.',
            verbose=True,
            allow_delegation=False,
            llm=self.writer_llm,
            max_iter=1
        )

    def visual_director_agent(self):
        return Agent(
            role='Visual Director',
            goal='Design a single 30-word image generation prompt.',
            backstory='Minimalist art director. CRITICAL: DO NOT output <think> tags or your internal reasoning process. Output ONLY the final requested format.',
            verbose=True,
            allow_delegation=False,
            llm=self.base_llm,
            max_iter=1
        )