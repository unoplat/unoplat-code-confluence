"""Catalog of available AI model providers and their configuration schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ProviderField(BaseModel):
    """Schema for a provider configuration field."""

    key: str
    label: str
    type: str  # text, password, select, number, boolean, url
    required: bool = False
    default: Any = None
    placeholder: Optional[str] = None
    help: Optional[str] = None
    enum: Optional[List[str]] = None


class ProviderSchema(BaseModel):
    """Schema for a provider's configuration."""

    provider_key: str
    display_name: str
    kind: str  # native | openai_compat
    model_field: Dict[str, Any]
    fields: List[ProviderField]

    def to_public(self) -> "ProviderSchemaPublic":
        """Return a variant without the redundant provider_key field."""

        return ProviderSchemaPublic(
            display_name=self.display_name,
            kind=self.kind,
            model_field=self.model_field,
            fields=self.fields,
        )


class ProviderSchemaPublic(BaseModel):
    """Public-facing provider schema shape without provider_key for API responses."""

    display_name: str
    kind: str
    model_field: Dict[str, Any]
    fields: List[ProviderField]


class ProviderCatalog:
    """Catalog of available AI model providers and their schemas for UI forms."""

    PROVIDERS = {
        "openai": ProviderSchema(
            provider_key="openai",
            display_name="OpenAI",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "gpt-4o",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "anthropic": ProviderSchema(
            provider_key="anthropic",
            display_name="Anthropic",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "claude-3-5-sonnet-latest",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "google": ProviderSchema(
            provider_key="google",
            display_name="Google GenAI",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "gemini-1.5-flash",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "groq": ProviderSchema(
            provider_key="groq",
            display_name="Groq",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "llama-3.3-70b-versatile",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "mistral": ProviderSchema(
            provider_key="mistral",
            display_name="Mistral",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "mistral-large-latest",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "cohere": ProviderSchema(
            provider_key="cohere",
            display_name="Cohere",
            kind="native",
            model_field={
                "label": "Model name",
                "placeholder": "command",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "huggingface": ProviderSchema(
            provider_key="huggingface",
            display_name="Hugging Face Inference",
            kind="native",
            model_field={
                "label": "Model Name",
                "placeholder": "Qwen/Qwen3-235B-A22B",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key",
                    label="HF token",
                    type="password",
                    required=True,
                ),
                ProviderField(
                    key="provider_name",
                    label="Inference provider (optional)",
                    type="select",
                    enum=[
                        "cohere",  # tested
                        "groq",  # tested
                        "fireworks-ai",
                        "together",
                        "hf-inference",
                        "nebius",
                        "novita",
                        "cerebras",
                        "fal-ai",  # tested
                        "featherless-ai",  # tested
                        "hyperbolic",
                        "nscale",
                        "publicai",
                        "sambanova",
                        "scaleway",
                        "zai-org",
                    ],
                    help="Default is 'huggingface' for Hosted HF Inference. Leave empty to use default.",
                ),
            ],
        ),
        "deepseek": ProviderSchema(
            provider_key="deepseek",
            display_name="DeepSeek ",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "deepseek-chat",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "openrouter": ProviderSchema(
            provider_key="openrouter",
            display_name="OpenRouter",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "google/gemini-2.5-pro-preview",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "fireworks": ProviderSchema(
            provider_key="fireworks",
            display_name="Fireworks",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "accounts/fireworks/models/qwq-32b",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "together": ProviderSchema(
            provider_key="together",
            display_name="Together AI",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "github": ProviderSchema(
            provider_key="github",
            display_name="GitHub Models",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "xai/grok-3-mini",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key",
                    label="GitHub PAT",
                    type="password",
                    required=True,
                    help="Requires models:read permission.",
                )
            ],
        ),
        "vercel": ProviderSchema(
            provider_key="vercel",
            display_name="Vercel AI Gateway",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "gpt-4o",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key",
                    label="Gateway key",
                    type="password",
                    required=True,
                )
            ],
        ),
        "grok": ProviderSchema(
            provider_key="grok",
            display_name="Grok / xAI",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "grok-3-mini",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                )
            ],
        ),
        "ollama": ProviderSchema(
            provider_key="ollama",
            display_name="Ollama / OpenAI",
            kind="openai_compat",
            model_field={
                "label": "Model name",
                "placeholder": "llama3.2",
                "required": True,
            },
            fields=[
                ProviderField(
                    key="base_url",
                    label="Base URL",
                    type="url",
                    placeholder="http://localhost:11434/v1",
                    required=True,
                )
            ],
        ),
        "azure": ProviderSchema(
            provider_key="azure",
            display_name="Azure OpenAI",
            kind="openai_compat",
            model_field={
                "label": "Deployment name",
                "placeholder": "my-gpt4o-deployment",
                "required": True,
                "help": "Use your Azure OpenAI deployment name as the model.",
            },
            fields=[
                ProviderField(
                    key="azure_endpoint",
                    label="Azure endpoint",
                    type="url",
                    required=True,
                ),
                ProviderField(
                    key="api_version",
                    label="API version",
                    type="select",
                    enum=["2024-02-01", "2024-06-01"],
                    required=True,
                ),
                ProviderField(
                    key="model_api_key", label="API key", type="password", required=True
                ),
            ],
        ),
    }

    @classmethod
    def get_provider(cls, provider_key: str) -> Optional[ProviderSchema]:
        """Get provider schema by key.

        Args:
            provider_key: The provider identifier

        Returns:
            ProviderSchema if found, None otherwise
        """
        return cls.PROVIDERS.get(provider_key)

    @classmethod
    def list_providers(cls) -> List[ProviderSchema]:
        """Return full provider schemas.

        Returns:
            List of ProviderSchema objects for all providers
        """
        return list(cls.PROVIDERS.values())

    @classmethod
    def list_providers_map(cls) -> Dict[str, ProviderSchemaPublic]:
        """Return provider schemas keyed by provider for faster lookups."""

        return {key: schema.to_public() for key, schema in cls.PROVIDERS.items()}

    @classmethod
    def get_provider_kind(cls, provider_key: str) -> Optional[str]:
        """Get provider kind for inference if not provided in request.

        Args:
            provider_key: The provider identifier

        Returns:
            Provider kind ('native' or 'openai_compat') if found, None otherwise
        """
        provider = cls.get_provider(provider_key)
        return provider.kind if provider else None
