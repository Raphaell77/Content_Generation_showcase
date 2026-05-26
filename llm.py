import json
import time
from openai import OpenAI
from pydantic import BaseModel

from analysis.json_utils import read_json, write_in_json, delete_json_data
from analysis.statistics import llm_data


client = OpenAI() # zieht api key automatisch aus umgebungsvariable


# helper class for ResponseFormat
class VideoIdea(BaseModel):
    video_title: str
    hook_angle: str
    value_proposition: str # deleted format_length

# structured response format for model
class ResponseFormat(BaseModel): 
    keyword: str
    video_ideas: list[VideoIdea]


class OpenAIWrapper:
    PATH_LLM_RESPONSE = 'analysis/responses/llm_response.json'

    @staticmethod
    def build_prompt(keyword: str, llm_data: dict, all_ideas_so_far: list) -> str:
        prompt = f"""You are an elite Content Strategy Analyst and Video SEO Specialist. Your task is to analyze an Opportunity Analysis JSON file and generate highly actionable, search-driven video ideas for a professional Content Opportunity Report.

        # 1. Core Philosophy
        Your focus is STRICTLY on plannable content opportunities based on real demand, NOT fleeting viral trends, TikTok sounds, or memes. The underlying principle is:
        True Content Opportunity = High Market Demand + Weak/Mediocre Answer Coverage. 
        You must treat platforms (YouTube, IG, TikTok) merely as distribution channels; your ideas must answer fundamental, platform-agnostic search intents.

        # 2. How to Interpret the Input Data
        You will receive a JSON object containing various topics/keywords. Each topic has specific metrics and reference data:
        - Demand Score (Low/Medium/High): Indicates the level of conscious search activity and consumption of existing videos.
        - Competition Strength (Low/Medium/High): Indicates how well the topic is currently answered by existing content (Answer Coverage, Quality Level, Angle Saturation).
        - Opportunity Score (Low/Medium/High): The most critical metric. "HIGH" means there is strong demand but weak competition. Focus your best ideas on HIGH and MEDIUM opportunity topics.
        - Content Length: The required depth of explanation (e.g., "< 5min", "5-10min"). Your video ideas MUST fit this scope.
        - video_titles (top_titles_views & top_titles_views_to_subs): These are proven concepts. DO NOT copy them directly. Instead, analyze them to find the "Content Gap" or to identify which angles are currently dominating, so you can propose superior, more specific, or fresh angles.

        # 3. Task Execution
        Topic to analyze: "{keyword}"
        
        Step A: Analyze the Opportunity
        Evaluate the given scores. If a topic has a "LOW" Opportunity Score, acknowledge that the market is either saturated or lacks demand, and suggest a highly specific micro-niche or unique angle to bypass the heavy competition. If it's "HIGH", capitalize on the broad gap.

        Step B: Generate Video Ideas
        *Important*: Avoid using ideas or linguistic concepts that have been used before.
        Previous_ideas to avoid: {all_ideas_so_far}
        
        Generate exactly 2 distinct video ideas for this topic.

        # 4. Input Data for "{keyword}":
        {llm_data}
        """
        return prompt


    # ollama run <model>, ollama pull <model>, ollama list, ollama show <model>
    @staticmethod
    def generate_ideas(prompt: str) -> dict:
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                # input=prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format=ResponseFormat
            )

            parsed_data = response.choices[0].message.parsed
            return parsed_data.model_dump()
        
        except Exception as e:
            print(f"Error while generating ideas occured:\n{e}")
            return {}




class Model(OpenAIWrapper):
    @staticmethod
    def run_model(llm_data: dict) -> dict:
        all_ideas_so_far = []
        final_report_data = {}

        for keyword, data in llm_data.items():
            prompt = OpenAIWrapper.build_prompt(keyword=keyword, llm_data=data, all_ideas_so_far=all_ideas_so_far)
            generated_ideas = OpenAIWrapper.generate_ideas(prompt=prompt)

            if keyword == generated_ideas.get("keyword", ""):
                video_ideas = generated_ideas.get("video_ideas", [])
                scores = {"Demand Score": data["Demand Score"],
                          "Competition Strength": data["Competition Strength"],
                          "Opportunity Score": data["Opportunity Score"],
                          "Content Length": data["Content Length"]}
                
                final_report_data[keyword] = {"scores": scores, "video_ideas": video_ideas}
                
                for idea in video_ideas:
                    title = idea.get("video_title", "")
                    if title:
                        all_ideas_so_far.append(title)
        
        delete_json_data(OpenAIWrapper.PATH_LLM)
        write_in_json(final_report_data, OpenAIWrapper.PATH_LLM)

        return final_report_data


