"""Factory for creating Pydantic AI models from configuration."""

import os
from typing import TYPE_CHECKING, Mapping, Optional, Tuple, Union

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings

from loguru import logger
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import (
    OpenAIChatModel,
    OpenAIResponsesModel,
    OpenAIResponsesModelSettings,
)
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.cohere import CohereProvider
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.fireworks import FireworksProvider
from pydantic_ai.providers.github import GitHubProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.providers.huggingface import HuggingFaceProvider
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.providers.together import TogetherProvider
from pydantic_ai.providers.vercel import VercelProvider
from pydantic_ai.providers.xai import XaiProvider
from pydantic_ai.settings import ModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.services.config.codex_openai_client import (
    create_codex_async_openai_client,
)
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.utils.retry_http_client import (
    create_retry_client,
)

# Union type for all supported Pydantic AI models
ModelType = Union[
    OpenAIChatModel,
    OpenAIResponsesModel,
    AnthropicModel,
    BedrockConverseModel,
    GoogleModel,
    GroqModel,
    MistralModel,
    CohereModel,
    HuggingFaceModel,
    XaiModel,
]


def _get_optional_extra_config_string(
    extra_config: Mapping[str, object], key: str
) -> str | None:
    """Get an optional trimmed string from provider extra_config."""
    value = extra_config.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        normalized_value = value.strip()
        return normalized_value if normalized_value else None
    raise ValueError(f"{key} in extra_config must be a string")


def _get_model_api_key_provider_key(
    metadata: Mapping[str, object] | None,
) -> str | None:
    """Return provider key associated with stored model API key."""
    if metadata is None:
        return None

    provider_key_value = metadata.get("provider_key")
    if provider_key_value is None:
        return None
    if isinstance(provider_key_value, str):
        normalized_provider_key = provider_key_value.strip()
        return normalized_provider_key if normalized_provider_key else None

    raise ValueError("provider_key in model credential metadata must be a string")


def _is_anthropic_bedrock_model(model_name: str) -> bool:
    """Return whether model ID targets Anthropic via Bedrock."""
    normalized_name = model_name.strip().lower()
    return normalized_name.startswith("anthropic.") or ".anthropic." in normalized_name


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

        # Build model settings from model_params JSONB
        model_settings = None
        base_model_settings: ModelSettings = {}
        params = config.model_params or {}
        if params.get("temperature") is not None:
            base_model_settings["temperature"] = params["temperature"]
        if params.get("top_p") is not None:
            base_model_settings["top_p"] = params["top_p"]
        if params.get("max_tokens") is not None:
            base_model_settings["max_tokens"] = params["max_tokens"]

        # Unified thinking level. Default to 'high' when unset; pydantic-ai
        # silently drops the key on non-reasoning models via profile gating,
        # and maps closest-supported value per provider (e.g. Qwen collapses
        # to high/low). Explicit False disables thinking where supported
        # (Anthropic) and is skipped on providers that reject 'none'.
        thinking_value = params.get("thinking")
        if thinking_value is None:
            thinking_value = "high"
        base_model_settings["thinking"] = thinking_value

        if base_model_settings:
            model_settings = base_model_settings

        credentials_service = CredentialsService()

        # Get API key from credentials (will be None for providers that don't need it)
        model_api_key = await credentials_service.get_model_credential(session)

        # Create retry HTTP client based on environment settings
        retry_client = create_retry_client(settings)

        # Native providers - all support both environment variables and direct API key passing
        match config.provider_key:
            case "openai":
                if model_api_key:
                    # Use custom provider with explicit API key
                    # supports custom http client through http_client parameter
                    if retry_client:
                        provider = OpenAIProvider(
                            api_key=model_api_key, http_client=retry_client
                        )
                    else:
                        provider = OpenAIProvider(api_key=model_api_key)
                    model = OpenAIChatModel(config.model_name, provider=provider)
                else:
                    # Fall back to environment variable OPENAI_API_KEY
                    model = OpenAIChatModel(config.model_name)
                logger.info("Created OpenAI model: {}", config.model_name)

            case "codex_openai":
                codex_client = create_codex_async_openai_client(settings)
                provider = OpenAIProvider(openai_client=codex_client)
                # Codex backend requires explicit `store=false` for Responses API requests.
                codex_model_settings: OpenAIResponsesModelSettings = {
                    "openai_store": False
                }
                if params.get("temperature") is not None:
                    codex_model_settings["temperature"] = params["temperature"]
                if params.get("top_p") is not None:
                    codex_model_settings["top_p"] = params["top_p"]
                if params.get("max_tokens") is not None:
                    codex_model_settings["max_tokens"] = params["max_tokens"]
                codex_model_settings["thinking"] = thinking_value
                model_settings = codex_model_settings
                model = OpenAIResponsesModel(
                    config.model_name,
                    provider=provider,
                    settings=codex_model_settings,
                )
                logger.info(
                    "Created Codex OpenAI Responses model via OAuth transport: {}",
                    config.model_name,
                )

            case "anthropic":
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
                logger.info("Created Anthropic model: {}", config.model_name)

            case "google":
                if model_api_key:
                    # Use custom provider with explicit API key
                    provider = GoogleProvider(api_key=model_api_key)
                    model = GoogleModel(config.model_name, provider=provider)
                else:
                    # Fall back to environment variable GOOGLE_API_KEY
                    model = GoogleModel(config.model_name)
                logger.info("Created Google model: {}", config.model_name)

            case "groq":
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
                logger.info("Created Groq model: {}", config.model_name)

            case "mistral":
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
                logger.info("Created Mistral model: {}", config.model_name)

            case "cohere":
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
                logger.info("Created Cohere model: {}", config.model_name)

            case "huggingface":
                # HuggingFace inference routers default max_tokens to a small value
                # that reasoning traces (thinking="high") exhaust before the model
                # emits visible output. Apply a 16k floor when operator left it unset.
                base_model_settings.setdefault("max_tokens", 16000)
                model_settings = base_model_settings

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

            case "bedrock":
                extra_config = config.extra_config or {}
                region_name = _get_optional_extra_config_string(
                    extra_config, "region_name"
                )
                aws_access_key_id = _get_optional_extra_config_string(
                    extra_config, "aws_access_key_id"
                )
                profile_name = _get_optional_extra_config_string(
                    extra_config, "profile_name"
                )
                model_api_key_metadata = (
                    await credentials_service.get_model_credential_metadata(session)
                )
                model_api_key_provider_key = _get_model_api_key_provider_key(
                    model_api_key_metadata
                )
                model_api_key_scoped_to_bedrock = (
                    model_api_key is not None
                    and model_api_key_provider_key == "bedrock"
                )

                if aws_access_key_id and not model_api_key:
                    raise ValueError(
                        "Bedrock requires model_api_key when aws_access_key_id is configured"
                    )

                if aws_access_key_id:
                    if not model_api_key_scoped_to_bedrock:
                        raise ValueError(
                            "Bedrock requires a Bedrock-scoped secret access key when aws_access_key_id is configured"
                        )
                    assert model_api_key is not None
                    provider = BedrockProvider(
                        region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=model_api_key,
                        profile_name=profile_name,
                        base_url=config.base_url,
                    )
                else:
                    if model_api_key_scoped_to_bedrock:
                        assert model_api_key is not None
                        provider = BedrockProvider(
                            region_name=region_name,
                            profile_name=profile_name,
                            api_key=model_api_key,
                            base_url=config.base_url,
                        )
                    else:
                        if model_api_key:
                            logger.info(
                                "Ignoring persisted model_api_key scoped to provider '{}' while building Bedrock model",
                                model_api_key_provider_key
                                if model_api_key_provider_key
                                else "unknown",
                            )
                        provider = BedrockProvider(
                            region_name=region_name,
                            profile_name=profile_name,
                            base_url=config.base_url,
                        )

                bedrock_model_settings: BedrockModelSettings = {}
                if params.get("temperature") is not None:
                    bedrock_model_settings["temperature"] = params["temperature"]
                if params.get("top_p") is not None:
                    bedrock_model_settings["top_p"] = params["top_p"]
                if params.get("max_tokens") is not None:
                    bedrock_model_settings["max_tokens"] = params["max_tokens"]
                bedrock_model_settings["thinking"] = thinking_value

                if _is_anthropic_bedrock_model(config.model_name):
                    bedrock_model_settings["bedrock_cache_instructions"] = True
                    bedrock_model_settings["bedrock_cache_tool_definitions"] = True
                    bedrock_model_settings["bedrock_cache_messages"] = True

                model_settings = (
                    bedrock_model_settings if bedrock_model_settings else None
                )
                model = BedrockConverseModel(
                    config.model_name,
                    provider=provider,
                    settings=bedrock_model_settings if bedrock_model_settings else None,
                )
                logger.info("Created Bedrock model: {}", config.model_name)

            # OpenAI-compatible providers
            case "deepseek":
                if not model_api_key:
                    raise ValueError("DeepSeek requires model_api_key")
                if retry_client:
                    provider = DeepSeekProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = DeepSeekProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created DeepSeek model: {}", config.model_name)

            case "openrouter":
                if not model_api_key:
                    raise ValueError("OpenRouter requires model_api_key")
                if retry_client:
                    provider = OpenRouterProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = OpenRouterProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created OpenRouter model: {}", config.model_name)

            case "fireworks":
                if not model_api_key:
                    raise ValueError("Fireworks requires model_api_key")
                if retry_client:
                    provider = FireworksProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = FireworksProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created Fireworks model: {}", config.model_name)

            case "together":
                if not model_api_key:
                    raise ValueError("Together AI requires model_api_key")
                if retry_client:
                    provider = TogetherProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = TogetherProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created Together AI model: {}", config.model_name)

            case "github":
                # GitHub now uses unified model_api_key
                if not model_api_key:
                    raise ValueError("GitHub Models requires model_api_key")
                if retry_client:
                    provider = GitHubProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = GitHubProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created GitHub model: {}", config.model_name)

            case "vercel":
                if not model_api_key:
                    raise ValueError("Vercel requires model_api_key")
                if retry_client:
                    provider = VercelProvider(
                        api_key=model_api_key, http_client=retry_client
                    )
                else:
                    provider = VercelProvider(api_key=model_api_key)
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created Vercel model: {}", config.model_name)

            case "grok":
                if not model_api_key:
                    raise ValueError("xAI/Grok requires model_api_key")
                # XaiProvider uses native xAI SDK (gRPC-based) and does not support http_client
                provider = XaiProvider(api_key=model_api_key)
                model = XaiModel(config.model_name, provider=provider)
                logger.info("Created xAI model: {}", config.model_name)

            case "azure":
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
                model = OpenAIChatModel(config.model_name, provider=provider)
                logger.info("Created Azure OpenAI model: {}", config.model_name)

            case "ollama":
                # Ollama doesn't require API key but needs base_url
                base_url = config.base_url or "http://localhost:11434/v1"
                model = OpenAIChatModel(
                    config.model_name, provider=OpenAIProvider(base_url=base_url)
                )
                logger.info("Created Ollama model at {}: {}", base_url, config.model_name)

            case _:
                raise ValueError(f"Unknown provider: {config.provider_key}")

        return model, model_settings
