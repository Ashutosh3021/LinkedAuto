import json
import logging
import requests
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import Config
from database import Post, PostStatus, AIProvider, db, PostHelper
from utils import decrypt_api_key


logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    pass


class RetryableAIProviderError(AIProviderError):
    """Errors that are safe to retry (network timeouts, 5xx server errors)"""
    pass


class NonRetryableAIProviderError(AIProviderError):
    """Errors that should NOT be retried (invalid API keys, 404, etc.)"""
    pass


class AIProviderAPI:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.api_key = decrypt_api_key(provider.api_key_encrypted)
        self.base_url = provider.base_url
        self.model = provider.model_name

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
        retry=retry_if_exception_type((
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
            RetryableAIProviderError
        ))
    )
    def generate_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        if not self.api_key:
            raise NonRetryableAIProviderError(f"API key not configured for provider {self.provider.name}")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }

        try:
            logger.info(f"Sending request to {self.provider.name} at {url}")
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=60)
            
            # Log detailed response info
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            try:
                response_body = response.json()
                logger.debug(f"Response body: {response_body}")
            except Exception:
                response_body = response.text
                logger.debug(f"Response text: {response_body}")
            
            if 500 <= response.status_code < 600:
                raise RetryableAIProviderError(
                    f"Provider {self.provider.name} server error ({response.status_code}): {response_body}"
                )
            
            response.raise_for_status()
            
            if "choices" not in response_body or not response_body["choices"]:
                raise NonRetryableAIProviderError(
                    f"Invalid response from provider {self.provider.name}: {response_body}"
                )
            
            return response_body["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.Timeout as e:
            raise RetryableAIProviderError(f"Request to {self.provider.name} timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise RetryableAIProviderError(f"Connection error to {self.provider.name}") from e
        except requests.exceptions.HTTPError as e:
            # Log full details
            logger.error(f"HTTP error calling {self.provider.name}: {response.status_code}")
            logger.error(f"Response body: {response_body}")
            if 400 <= response.status_code < 500:
                raise NonRetryableAIProviderError(
                    f"Provider {self.provider.name} client error ({response.status_code}): {response_body}"
                ) from e
            else:
                raise RetryableAIProviderError(
                    f"Provider {self.provider.name} server error ({response.status_code}): {response_body}"
                ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception calling {self.provider.name}: {e}")
            raise NonRetryableAIProviderError(f"API request failed: {str(e)}") from e


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
        self.prompt_builder = PromptBuilder()

    def _get_active_provider(self) -> AIProvider:
        """Get active AI provider from DB, or fall back to env var"""
        active_provider = AIProvider.query.filter_by(is_active=True).first()
        
        if active_provider:
            return active_provider
        
        # Fallback to OpenRouter from env vars for backward compatibility
        if Config.OPENROUTER_API_KEY:
            fallback_provider = AIProvider(
                name="OpenRouter (Fallback)",
                model_name=Config.OPENROUTER_MODEL,
                api_key_encrypted="",  # Not stored in DB
                base_url=Config.OPENROUTER_BASE_URL,
                is_active=False
            )
            # We'll manually set api key instead of encrypting
            fallback_provider._api_key = Config.OPENROUTER_API_KEY
            return fallback_provider
        
        raise AIProviderError("No active AI provider configured")

    def _get_api_instance(self, provider: AIProvider) -> AIProviderAPI:
        """Get API instance, handling fallback case"""
        if hasattr(provider, '_api_key'):
            # Fallback case: use env var directly
            api = AIProviderAPI.__new__(AIProviderAPI)
            api.provider = provider
            api.api_key = provider._api_key
            api.base_url = provider.base_url
            api.model = provider.model_name
            return api
        return AIProviderAPI(provider)

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
        provider = self._get_active_provider()
        api = self._get_api_instance(provider)
        
        messages = self.prompt_builder.build_post_prompt(
            topic=topic,
            project=project,
            audience=audience,
            tone=tone,
            domains=domains,
            hashtags=hashtags,
            character_limit=character_limit
        )
        
        content = api.generate_completion(messages, max_tokens=character_limit or 1000)
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
                logger.error(f"Failed to generate post for topic '{topic}': {e}")
                continue
        
        return posts
