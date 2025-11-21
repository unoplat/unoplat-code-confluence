import { ProviderKey } from "@/types/credential-enums";

/**
 * Response from the backend when fetching configured providers
 */
export interface RepositoryProvidersResponse {
  providers: ProviderKey[];
}

/**
 * Form data structure for submitting provider credentials
 */
export interface RepositoryProviderFormData {
  provider_key: ProviderKey;
  patToken: string;
  url?: string;
}

/**
 * Provider descriptor with display metadata
 */
export interface Provider {
  provider_key: ProviderKey;
  url?: string;
  display_name: string;
}
