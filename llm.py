import json
import requests
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import Config
from models import Post, PostStatus
from database import PostHelper


class OpenRouterError(Exception):
    pass


class OpenRouterAPI:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.OPENROUTER_MODEL

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/linkedin-automation",
            "X-Title": "LinkedIn Automation Tool"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, OpenRouterError))
    )
    def generate_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise OpenRouterError("Invalid response from OpenRouter")
            
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            raise OpenRouterError(f"API request failed: {str(e)}") from e


class PromptBuilder:
    @staticmethod
    def build_post_prompt(
        topic: str,
        project: Optional[str] = None,
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        domains: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        character_limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        system_prompt = """You are an expert LinkedIn content creator. Generate engaging, professional LinkedIn posts that are:
- Concise and easy to read
- Actionable and valuable
- Well-structured with clear sections
- Written in a conversational but professional tone
- Free of excessive jargon"""

        user_prompt_parts = [f"Topic: {topic}"]
        
        if project:
            user_prompt_parts.append(f"Project Context: {project}")
        if audience:
            user_prompt_parts.append(f"Target Audience: {audience}")
        if tone:
            user_prompt_parts.append(f"Tone: {tone}")
        if domains and domains:
            user_prompt_parts.append(f"Domains: {', '.join(domains)}")
        if character_limit:
            user_prompt_parts.append(f"Character Limit: {character_limit} characters")

        user_prompt = "\n".join(user_prompt_parts)
        user_prompt += "\n\nGenerate a LinkedIn post about this topic. "
        
        if hashtags and hashtags:
            user_prompt += f"Include these hashtags: {', '.join(hashtags)}. "
        else:
            user_prompt += "Include relevant hashtags. "
            
        user_prompt += "Do not include any additional explanations or comments - just the post content."

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


class PostGenerator:
    def __init__(self):
        self.api = OpenRouterAPI()
        self.prompt_builder = PromptBuilder()

    def generate_single_post(
        self,
        topic: str,
        title: Optional[str] = None,
        project: Optional[str] = None,
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        domains: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        character_limit: Optional[int] = None
    ) -> Post:
        messages = self.prompt_builder.build_post_prompt(
            topic=topic,
            project=project,
            audience=audience,
            tone=tone,
            domains=domains,
            hashtags=hashtags,
            character_limit=character_limit
        )
        
        content = self.api.generate_completion(messages, max_tokens=character_limit or 1000)
        post_title = title or topic
        
        post = PostHelper.create(
            Post,
            title=post_title,
            content=content,
            status=PostStatus.DRAFT
        )
        
        return post

    def generate_batch_posts(
        self,
        topics: List[str],
        project: Optional[str] = None,
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        domains: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        character_limit: Optional[int] = None
    ) -> List[Post]:
        posts = []
        
        for topic in topics:
            try:
                post = self.generate_single_post(
                    topic=topic,
                    project=project,
                    audience=audience,
                    tone=tone,
                    domains=domains,
                    hashtags=hashtags,
                    character_limit=character_limit
                )
                posts.append(post)
            except Exception as e:
                print(f"Failed to generate post for topic '{topic}': {e}")
                continue
        
        return posts
