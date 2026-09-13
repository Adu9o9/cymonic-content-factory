from crewai import Task

class ContentFactoryTasks:
    def extraction_task(self, agent, source_text):
        return Task(
            description=f"Extract Product Name, Features, Specs, Target Audience, and Red Flags from this text: {source_text[:1500]}",
            expected_output="Markdown document with extracted facts and a 'Red Flags' section.",
            agent=agent
        )

    def copywriting_task(self, agent, context_task):
        return Task(
            description="""
            Using the Source of Truth, write:
            1. ## Blog Post (Professional, 300 words).
            2. ## Social Media Strategy (Punchy, 3 posts max based on B2B/B2C).
            3. ## Email Teasers (Variant A: Logic, Variant B: Emotion).
            CRITICAL: Exclude any claims from the Red Flags section. Output ONLY the campaign text.
            """,
            expected_output="Markdown campaign with 3 sections.",
            agent=agent,
            context=[context_task]
        )

    def editing_task(self, agent, extract_task, copy_task):
        return Task(
            description="""
            Review the Campaign Draft against the Source of Truth. Remove any Red Flag claims.
            Output format MUST BE:
            [Final Campaign Markdown]
            ===AUDIT_LOG===
            {"removed_features": [{"feature": "...", "reason": "..."}]}
            """,
            expected_output="Corrected markdown, the exact delimiter '===AUDIT_LOG===', and a JSON log.",
            agent=agent,
            context=[extract_task, copy_task]
        )

    def image_prompt_task(self, agent, truth_task):
        return Task(
            description="Read the Source of Truth. Output a 30-word image generation prompt. Ask to write the Product Name subtly on a relevant physical surface.",
            expected_output="A single sentence image prompt.",
            agent=agent,
            context=[truth_task]
        )
