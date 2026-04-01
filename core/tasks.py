from crewai import Task

class ContentFactoryTasks:
    def extraction_task(self, agent, source_text):
        return Task(
            description=f"""
            Analyze the following raw source text:
            ---
            {source_text}
            ---
            
            1. Identify the specific Product Name.
            2. Identify the core product features.
            3. Extract any technical specifications.
            4. Define the intended target audience.
            5. CRITICAL: Identify and explicitly flag any ambiguous, vague, or potentially confusing statements.
            """,
            expected_output="A structured Markdown document representing the 'Source of Truth' with sections for Product Name, Features, Specs, Target Audience, and Red Flags.",
            agent=agent
        )

    def copywriting_task(self, agent, context_task):
        return Task(
            description="""
            Using ONLY the 'Source of Truth' fact-sheet, create a comprehensive marketing campaign.
            
            CRITICAL RULES:
            - Do NOT include any features or claims listed in the 'Red Flags' section. 
            - You MUST explicitly state the Product Name in all pieces of content.
            - ALL HEADERS MUST USE STRICT MARKDOWN (e.g., ## or ###) followed by a blank line so they render as large text.

            Generate exactly THREE distinct sections with clear Markdown headers (##):
            
            1. ## Blog Post
                - TONE DIRECTIVE: Must be highly **Professional, authoritative, and educational**.
                - Create a catchy title formatted as an H3 Markdown header (e.g., ### [Your Catchy Title]).
                - Write a comprehensive, highly engaging **500-word blog post**. Expand on the value propositions and technical specs to meet this exact length.
               
            2. ## Social Media Strategy
                - TONE DIRECTIVE: Must be **Punchy, engaging, trendy, and scroll-stopping**.
                - Dynamically select the most relevant platforms for this specific target audience (e.g., LinkedIn, X, Instagram, Facebook).
                - FORMATTING: Generate exactly a **5-post Social Media Thread** (e.g., a 5-part thread on X, or 5 distinct posts distributed across LinkedIn/Instagram/Facebook). 
                - Use an H3 sub-header (###) for each post indicating the platform (e.g., ### LinkedIn - Post 1). You MUST add a blank line between the header, the post body, and the hashtags to create visual breathing room.
                - MAKE IT DATA-DRIVEN: You MUST include the specific, impressive technical numbers and flagship features directly from the fact-sheet. Do not write boring, generic descriptions.
                - **Bold** the hashtags at the bottom.
               
            3. ## Email Teaser
                - TONE DIRECTIVE: Must be **Direct, persuasive, and urgency-driven**.
                - 1-paragraph. Direct call-to-action. Mock URL: 'www.cymonic.com/launch'.
            """,
            expected_output="A single Markdown document containing the 500-word Blog Post, the 5-post Social Media Strategy (platform specific), and the Email Teaser, utilizing strict Markdown headers for formatting.",
            agent=agent,
            context=[context_task] 
        )

    def editing_task(self, agent, extract_task, copy_task):
        return Task(
            description="""
            Review the Marketing Campaign draft created by the Copywriter. 
            Cross-reference it strictly against the 'Source of Truth' fact-sheet.
            
            YOUR JOB:
            1. Look at the "Red Flags" section of the Source of Truth. 
            2. If the Copywriter included ANY of the specific red flags in the Blog, X Post, LinkedIn Post, or Email, rewrite that section to remove the claim entirely. 
            3. RULE: Output ONLY the final, polished marketing campaign markdown. Do NOT output any conversational text or notes.
            """,
            expected_output="The final, corrected Markdown document, free of any red-flag claims and conversational notes.",
            agent=agent,
            context=[extract_task, copy_task] 
        )

    def image_prompt_task(self, agent, audit_task):
        return Task(
            description="""
            Read the final, edited Marketing Campaign.
            Design a compelling cover image prompt for the Flux AI image generator.
            
            CRITICAL RULES:
            - Output ONLY the prompt text. Under 40 words.
            - Describe a highly relevant product environment based on the actual product.
            - TYPOGRAPHY: You MUST ask the AI to write the Product Name in the image EXACTLY ONCE.
            - THE FIX: To hide potential AI spelling errors, explicitly instruct the generator to make the text SUBTLE, SMALL, and SECONDARY.
            - SURFACE CONTEXT: Place the text on a surface that actually makes sense for the specific product category. Examples: printed on a frosted glass bottle or jar for cosmetics/skincare, engraved on a metal casing for hardware, displayed on a clean interface for software, or embossed on premium cardboard packaging. Do NOT default to a "monitor" unless it is a digital product.
            - Example format: "[Environment], [lighting], with the text '[Actual Product Name]' written subtly on [a highly relevant object/surface], 8k resolution"
            """,
            expected_output="A short, single string of text representing the image generation prompt.",
            agent=agent,
            context=[audit_task]
        )
