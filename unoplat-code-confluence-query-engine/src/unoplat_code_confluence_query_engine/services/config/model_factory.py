"""Factory for creating Pydantic AI models from configuration."""

import os
from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings

from loguru import logger
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.providers.cohere import CohereProvider
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.fireworks import FireworksProvider
from pydantic_ai.providers.github import GitHubProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.grok import GrokProvider
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.providers.huggingface import HuggingFaceProvider
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.providers.together import TogetherProvider
from pydantic_ai.providers.vercel import VercelProvider
from pydantic_ai.settings import ModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.utils.retry_http_client import (
    create_retry_client,
)

# Union type for all supported Pydantic AI models
ModelType = Union[
    OpenAIModel,
    AnthropicModel,
    GoogleModel,
    GroqModel,
    MistralModel,
    CohereModel,
    HuggingFaceModel,
]


class ModelFactory:
    """Factory for creating Pydantic AI models from configuration."""

    @staticmethod
    async def build(
        config: AiModelConfig,
        settings: "EnvironmentSettings",
        session: AsyncSession,
    ) -> Tuple[ModelType, Optional[ModelSettings]]:
        """Build Pydantic AI model from configuration.

        Args:
            config: AI model configuration from database
            settings: Environment settings for retry configuration
            session: Database session

        Returns:
            Tuple of (model instance, optional settings)

        Raises:
            ValueError: If provider is unknown or required credentials are missing
        """

        # Build model settings if configured
        model_settings = None
        if config.temperature or config.top_p or config.max_tokens:
            model_settings = ModelSettings(
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
            )

        credentials_service = CredentialsService()

        # Get API key from credentials (will be None for providers that don't need it)
        model_api_key = await credentials_service.get_model_credential(session)

        # Create retry HTTP client based on environment settings
        retry_client = create_retry_client(settings)

        # Native providers - all support both environment variables and direct API key passing
        if config.provider_key == "openai":
            if model_api_key:
                # Use custom provider with explicit API key
                # supports custom http client through http_client parameter
                if retry_client:
                    provider = OpenAIProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = OpenAIProvider(api_key=model_api_key)
                model = OpenAIModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable OPENAI_API_KEY
                model = OpenAIModel(config.model_name)
            logger.info(f"Created OpenAI model: {config.model_name}")

        elif config.provider_key == "anthropic":
            if model_api_key:
                # Use custom provider with explicit API key
                # supports custom http client through http_client parameter
                if retry_client:
                    provider = AnthropicProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = AnthropicProvider(api_key=model_api_key)
                model = AnthropicModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable ANTHROPIC_API_KEY
                model = AnthropicModel(config.model_name)
            logger.info(f"Created Anthropic model: {config.model_name}")

        elif config.provider_key == "google":
            if model_api_key:
                # Use custom provider with explicit API key
                provider = GoogleProvider(api_key=model_api_key)
                model = GoogleModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable GOOGLE_API_KEY
                model = GoogleModel(config.model_name)
            logger.info(f"Created Google model: {config.model_name}")

        elif config.provider_key == "groq":
            if model_api_key:
                # Use custom provider with explicit API key
                # supports custom http client through http_client parameter
                if retry_client:
                    provider = GroqProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = GroqProvider(api_key=model_api_key)
                model = GroqModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable GROQ_API_KEY
                model = GroqModel(config.model_name)
            logger.info(f"Created Groq model: {config.model_name}")

        elif config.provider_key == "mistral":
            if model_api_key:
                # Use custom provider with explicit API key
                # supports custom http client through http_client parameter
                if retry_client:
                    provider = MistralProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = MistralProvider(api_key=model_api_key)
                model = MistralModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable MISTRAL_API_KEY
                model = MistralModel(config.model_name)
            logger.info(f"Created Mistral model: {config.model_name}")

        elif config.provider_key == "cohere":
            if model_api_key:
                # Use custom provider with explicit API key
                # supports custom http client through http_client parameter
                if retry_client:
                    provider = CohereProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = CohereProvider(api_key=model_api_key)
                model = CohereModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable CO_API_KEY
                model = CohereModel(config.model_name)
            logger.info(f"Created Cohere model: {config.model_name}")

        elif config.provider_key == "huggingface":
            # Get provider_name from extra_config, default to None (uses default HF inference)
            provider_name = config.extra_config.get("provider_name")

            if model_api_key:
                # Set HF_TOKEN environment variable instead of passing API key directly
                os.environ["HF_TOKEN"] = model_api_key

                # supports custom http client through http_client parameter
                if provider_name:
                    provider = HuggingFaceProvider(provider_name=provider_name)
                    logger.info(
                        f"Created HuggingFace model with provider {provider_name}: {config.model_name}"
                    )
                else:
                    provider = HuggingFaceProvider()
                    logger.info(
                        f"Created HuggingFace model with default provider: {config.model_name}"
                    )

                model = HuggingFaceModel(config.model_name, provider=provider)
            else:
                # Fall back to environment variable HF_TOKEN
                if provider_name:
                    # Need to set provider_name even when using environment variable
                    provider = HuggingFaceProvider(provider_name=provider_name)
                    model = HuggingFaceModel(config.model_name, provider=provider)
                    logger.info(
                        f"Created HuggingFace model with provider {provider_name}: {config.model_name}"
                    )
                else:
                    model = HuggingFaceModel(config.model_name)
                    logger.info(
                        f"Created HuggingFace model with default provider: {config.model_name}"
                    )

        # OpenAI-compatible providers
        elif config.provider_key == "deepseek":
            if not model_api_key:
                raise ValueError("DeepSeek requires model_api_key")
            if retry_client:
                provider = DeepSeekProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = DeepSeekProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created DeepSeek model: {config.model_name}")

        elif config.provider_key == "openrouter":
            if not model_api_key:
                raise ValueError("OpenRouter requires model_api_key")
            if retry_client:
                provider = OpenRouterProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = OpenRouterProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created OpenRouter model: {config.model_name}")

        elif config.provider_key == "fireworks":
            if not model_api_key:
                raise ValueError("Fireworks requires model_api_key")
            if retry_client:
                provider = FireworksProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = FireworksProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created Fireworks model: {config.model_name}")

        elif config.provider_key == "together":
            if not model_api_key:
                raise ValueError("Together AI requires model_api_key")
            if retry_client:
                provider = TogetherProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = TogetherProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created Together AI model: {config.model_name}")

        elif config.provider_key == "github":
            # GitHub now uses unified model_api_key
            if not model_api_key:
                raise ValueError("GitHub Models requires model_api_key")
            if retry_client:
                provider = GitHubProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = GitHubProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created GitHub model: {config.model_name}")

        elif config.provider_key == "vercel":
            if not model_api_key:
                raise ValueError("Vercel requires model_api_key")
            if retry_client:
                provider = VercelProvider(
                    api_key=model_api_key, http_client=retry_client
                )
            else:
                provider = VercelProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created Vercel model: {config.model_name}")

        elif config.provider_key == "grok":
            if not model_api_key:
                raise ValueError("Grok requires model_api_key")
            if retry_client:
                provider = GrokProvider(api_key=model_api_key, http_client=retry_client)
            else:
                provider = GrokProvider(api_key=model_api_key)
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created Grok model: {config.model_name}")

        elif config.provider_key == "azure":
            if not model_api_key:
                raise ValueError("Azure OpenAI requires model_api_key")

            # Azure requires endpoint and api_version in extra_config
            azure_endpoint = config.extra_config.get("azure_endpoint")
            api_version = config.extra_config.get("api_version")

            if not azure_endpoint or not api_version:
                raise ValueError(
                    "Azure requires azure_endpoint and api_version in extra_config"
                )

            if retry_client:
                provider = AzureProvider(
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,
                    api_key=model_api_key,
                    http_client=retry_client,
                )
            else:
                provider = AzureProvider(
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,
                    api_key=model_api_key,
                )
            model = OpenAIModel(config.model_name, provider=provider)
            logger.info(f"Created Azure OpenAI model: {config.model_name}")

        elif config.provider_key == "ollama":
            # Ollama doesn't require API key but needs base_url
            base_url = config.base_url or "http://localhost:11434/v1"
            model = OpenAIModel(
                config.model_name, provider=OpenAIProvider(base_url=base_url)
            )
            logger.info(f"Created Ollama model at {base_url}: {config.model_name}")

        else:
            raise ValueError(f"Unknown provider: {config.provider_key}")

        return model, model_settings
