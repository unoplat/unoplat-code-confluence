import { create } from "zustand";
import { ProviderKey } from "@/types/credential-enums";
import { getProviderDisplayName } from "@/lib/utils/provider-utils";
import { fetchProvidersApi } from "@/lib/api/repository-provider-api";

export interface ProviderDescriptor {
  provider_key: ProviderKey;
  display_name: string;
  url?: string;
}

interface ProviderState {
  providers: ProviderDescriptor[];
  selectedProvider: ProviderKey | null;
  isLoading: boolean;
  error: string | null;
  fetchProviders: () => Promise<void>;
  addProvider: (provider: ProviderDescriptor) => void;
  selectProvider: (providerKey: ProviderKey) => void;
  hasProvider: (providerKey: ProviderKey) => boolean;
  removeProvider: (providerKey: ProviderKey) => void;
  clearError: () => void;
}

export const useProviderStore = create<ProviderState>()((set, get) => ({
  providers: [],
  selectedProvider: null,
  isLoading: false,
  error: null,

  fetchProviders: async () => {
    set({ isLoading: true, error: null });
    try {
      const providerKeys = await fetchProvidersApi();
      const providers = providerKeys.map((key) => ({
        provider_key: key,
        display_name: getProviderDisplayName(key),
      }));
      set({
        providers,
        selectedProvider: providerKeys[0] ?? null,
        isLoading: false,
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch providers";
      set({ error: message, isLoading: false });
    }
  },

  addProvider: (provider) => {
    if (get().providers.some((p) => p.provider_key === provider.provider_key)) {
      return;
    }
    set((state) => ({
      providers: [...state.providers, provider],
      selectedProvider: state.selectedProvider ?? provider.provider_key,
    }));
  },

  selectProvider: (providerKey) => set({ selectedProvider: providerKey }),

  hasProvider: (providerKey) =>
    get().providers.some((p) => p.provider_key === providerKey),

  removeProvider: (providerKey) => {
    set((state) => {
      const remaining = state.providers.filter(
        (p) => p.provider_key !== providerKey,
      );
      const selected =
        state.selectedProvider === providerKey
          ? (remaining[0]?.provider_key ?? null)
          : state.selectedProvider;
      return { providers: remaining, selectedProvider: selected };
    });
  },

  clearError: () => {
    set({ error: null });
  },
}));
