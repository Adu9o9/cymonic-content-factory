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
            - NO CONVERSATIONAL FILLER: Output ONLY the final marketing text. Do not include meta-commentary (e.g., "Since this is a B2C product...").

            Generate exactly THREE distinct sections with clear Markdown headers (##):
            
            1. ## Blog Post
                - TONE DIRECTIVE: Must be highly **Professional, authoritative, and educational**.
                - Create a catchy title formatted as an H3 Markdown header (e.g., ### [Catchy Title]).
                - FORMATTING RULE: Break up the text for maximum readability. You MUST **bold** the core features, technical specifications, and key value propositions throughout the paragraphs. 
                - STRUCTURE RULE: Include at least one bulleted list highlighting the top 3 standout benefits of the product.
                - Write a comprehensive, highly engaging **500-word blog post**. Expand on the value propositions and technical specs.
               
            2. ## Social Media Strategy
                - TONE DIRECTIVE: Must be **Punchy, engaging, trendy, and scroll-stopping**.
                - HARD PLATFORM RULE: You must first classify the product as B2B or B2C.(pls note that the classification B2B or B2C need not be explicitly stated in the Source of Truth. You must infer it based on the product features and target audience and no need to print it out under social media strategy).
                                    * IF B2C (Cosmetics, personal tech, consumer goods): You are STRICTLY FORBIDDEN from using LinkedIn. You must allocate your posts across Instagram, Facebook, and X ONLY (e.g., 3 on Instagram, 2 on Facebook).
                                    * IF B2B (Enterprise software, corporate tools): You are STRICTLY FORBIDDEN from using Instagram and Facebook. You must allocate your posts across LinkedIn and X ONLY (e.g., 3 on LinkedIn, 2 on X).
                                - FORMATTING: Group your posts sequentially by platform. Use an H3 sub-header for each post indicating the platform and sequence (e.g., ### Instagram - Post 1 of 3). You MUST add a blank line between the header, the post body, and the hashtags.
                                - ANTI-FLUFF RULE: EVERY SINGLE POST must highlight a DIFFERENT specific technical spec, number, color variant, or flagship feature from the fact-sheet. Do NOT use generic phrases without backing them up with hard data. (e.g., Post 1 can be an intro/feature, Post 2 can be price/other features).Also bold the specific feature or spec you are highlighting in each post (e.g., "Experience lightning-fast performance with the new **product name** or other examples with respect to type of product").
                - **Bold** the hashtags at the bottom but same allignment as body. These hashtags must be a font size smaller than the post body (e.g., by using a blockquote or other Markdown formatting trick).
               
                        3. ## Email Teaser (A/B Testing Strategy)
                                - You must generate TWO distinct email variants for marketing to A/B test.
                                - ### Variant A: Logic & Feature-Driven
                                    * TONE: Professional, analytical, focused on ROI, technical specs, and concrete value.
                                    * 1-paragraph. Direct call-to-action. Mock URL: 'www.cymonic.com/launch'.
                                - ### Variant B: Emotion & Urgency-Driven
                                    * TONE: Punchy, FOMO-inducing (Fear Of Missing Out), focused on pain points, speed, and exclusivity.
                                    * 1-paragraph. Direct call-to-action. Mock URL: 'www.cymonic.com/launch'.
            """,
                        expected_output="A single Markdown document containing the 500-word Blog Post, a highly-technical social media strategy strictly adhering to platform rules, and TWO distinct Email Teasers (Variant A and Variant B) for A/B testing. No conversational filler.",
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
            - TYPOGRAPHY & SANITIZATION: You MUST ask the AI to write the Product Name in the image EXACTLY ONCE. However, to prevent URL parsing errors, you MUST strip out all special characters (%, +, &, #, etc.) and shorten the text to a maximum of 4 words. Use ONLY the core alphanumeric brand name.
            - THE FIX: To hide potential AI spelling errors, explicitly instruct the generator to make the text SUBTLE, SMALL, and SECONDARY.
            - SURFACE CONTEXT: Place the text on a surface that makes sense for the specific product category (e.g., printed on a frosted glass bottle for cosmetics, engraved on metal for hardware, displayed on a clean interface for software). Do NOT default to a "monitor" unless it is a digital product.
            - Example format: "[Environment], [lighting], with the text '[Shortened Alphanumeric Brand Name]' written subtly on [a highly relevant object/surface], 8k resolution"
            """,
            expected_output="A short, single string of text representing the image generation prompt.",
            agent=agent,
            context=[audit_task]
        )
