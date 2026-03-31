import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

class ContentFactoryAgents:
    def __init__(self):
        # We are using Llama 3.3 70B for the ENTIRE assembly line. 
        # It is brilliant, fast, and 100% free with no credit card locks.
        self.llm = LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.4 # A balanced temperature for both facts and creativity
        )

    def research_agent(self):
        return Agent(
            role='Lead Research & Fact-Check Analyst',
            goal='Extract core product features, technical specs, and target audience from raw text to produce a structured "Source of Truth".',
            backstory='You are a meticulous, highly analytical lead researcher. Your primary directive is to find the absolute truth in raw source material. You never assume, guess, or invent facts. You ruthlessly flag ambiguous statements.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def copywriter_agent(self):
        return Agent(
            role='Creative Copywriter',
            goal='Transform structured fact-sheets into engaging, multi-channel marketing campaigns.',
            backstory='You are a versatile, highly creative copywriter. You excel at adapting your tone for different platforms, from formal blogs to punchy social media threads. You strictly adhere to fact-sheets and never invent features, prices, or timelines that are not explicitly confirmed.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def editor_agent(self):
        return Agent(
            role='Chief Editor & Brand Compliance Officer',
            goal='Audit marketing copy to ensure absolute compliance with the Source of Truth and remove any unverified claims.',
            backstory='You are a ruthless, detail-oriented Editor-in-Chief. You despise false advertising. You will read marketing drafts and cross-reference them against the original Source of Truth. If a draft mentions ANY feature listed in the "Red Flags" section, you will rewrite the copy to completely remove it.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def visual_director_agent(self):
        return Agent(
            role='Creative Visual Director',
            goal='Analyze a marketing campaign and write a highly detailed, comma-separated prompt for an AI image generator.',
            backstory='You are an elite art director. You read marketing copy and visualize the perfect accompanying image. You know that AI image generators need specific, comma-separated keywords (e.g., "subject, lighting, camera angle, style"). You output ONLY the prompt string, with no conversational text.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )