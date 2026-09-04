import streamlit as st
import time
from google import genai
from google.genai import types

@st.cache_resource
def get_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

def safe_generate(prompt, config=None):
    client = get_client()
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config=config,
            )
            return response.text

        except Exception as e:
            print(f"Gemini Error: {e}")

            if attempt < 2:
                time.sleep(2 * (2 ** attempt))   # 1s, 2s
            else:
                return "⚠️ AI service is temporarily unavailable. Please try again."


def generate_causes(analysis_data):
    prompt = f"""
You are UrbanHeat AI, an Urban Heat Island analysis expert.

Analysis Results:
{analysis_data}

Task:
Identify the main reasons behind the observed urban heat conditions.

Rules:
- Return exactly 4 bullet points in this manner:
    - 1st point
    - 2nd point
    - 3rd point
    - 4th point
- Use simple English.
- Explain the causes, not the solutions.
- Base every point ONLY on the provided analysis.
- Never invent facts.
- Mention temperatures, risk levels or affected regions only when they strengthen the explanation.
- Replace technical terms with simple language:
  - NDVI → vegetation
  - NDBI → buildings and roads
  - NDWI → water bodies
- Do not use headings.
- Keep each bullet under 20 words.
- Avoid repeating the same idea.
"""
    return safe_generate(prompt)

def generate_recommendations(analysis_data):
    prompt = f"""
You are UrbanHeat AI, an urban planning expert.

Analysis Results:
{analysis_data}

Task:
Generate exactly 3 practical recommendations based on the analysis.

Rules:
- Every recommendation must be supported by the analysis.
- Prioritize the highest-risk areas first whenever possible.
- Mention affected regions if available.
- Explain briefly why each recommendation is useful.
- Do not invent information.
- Use simple English.
- Keep each recommendation under 25 words.
- Convert technical metrics (NDVI, NDWI, NDBI) into plain language such as vegetation, buildings, and water availability unless the user explicitly asks for the scientific values.
- Format exactly like this:

1. Recommendation

2. Recommendation

3. Recommendation
"""

    return safe_generate(prompt)


def ask_planning_assistant(analysis_data, question):
    prompt = f"""
You are UrbanHeat AI, an AI assistant for urban heat planning.

Analysis Results:
{analysis_data}

User Question:
{question}

Your Role:
Help users understand the analysis and make planning decisions.

Rules:
- Answer ONLY using the provided analysis.
- Never invent values or facts.
- If the answer is not directly available in the analysis, provide best-practice recommendations and relate them back to the analysis whenever possible
- Respond as an urban planning expert, not as a weather assistant.
- Use actual temperatures, risk levels, percentages and regions whenever relevant.
- Explain technical findings in simple English.
- Mention the highest-risk area when discussing mitigation or priorities.
- Give practical planning advice only when appropriate.
- Keep answers between 40 and 80 words.
- Use no more than two short paragraphs.
- Convert technical metrics (NDVI, NDWI, NDBI) into plain language such as vegetation, buildings, and water availability unless the user explicitly asks for the scientific values.
- Never mention being an AI language model.
"""

    return safe_generate(
    prompt,
    types.GenerateContentConfig(
        max_output_tokens=120,
        temperature=0.2,
    ),
)

def generate_suggested_questions(analysis_data):

    prompt = f"""
You are UrbanHeat AI.

Based on the following Urban Heat analysis:

{analysis_data}

Generate exactly 4 planning-related questions.

Rules:
- Maximum 6 words.
- Use simple English.
- Focus on urban planning.
- Never ask about today's weather.
- Never ask for unavailable information.
- Examples:
Which area needs attention first?
What is causing the heat?
How can this area become cooler?
What should be done first?

Return only the questions.
"""

    return safe_generate(prompt)

def compare_cities_ai(city1, city2, metrics):
    prompt = f"""
You are UrbanHeat AI.

Compare these two cities using the provided analysis.

City 1: {city1}
City 2: {city2}

Analysis:
{metrics}

Instructions:
- Decide which city is hotter and explain why.
- Decide which city has better vegetation.
- Decide which city should be prioritized for Urban Heat mitigation.
- Give one short recommendation.
- Use ONLY the provided values.
- Use simple English.
- Keep the response under 120 words.
- Format exactly as:

🔥 Hotter City:
...

🌿 Greener City:
...

⚠ Priority City:
...

💡 Recommendation:
...
"""

    return safe_generate(prompt)