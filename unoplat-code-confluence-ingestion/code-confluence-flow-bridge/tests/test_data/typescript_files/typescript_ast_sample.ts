// ============================================================================
// TypeScript AST Sample For React + Vite Codebase (No TSX)
// Aggregates common patterns from src/lib, src/hooks, and related modules.
// Used to validate Tree-sitter TypeScript queries without mixing TSX syntax.
// ============================================================================

// Side-effect imports
import 'wicg-inert';
import '@/styles/globals.css';

import axios, {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
} from 'axios';
import { createParser } from 'nuqs/server';
import { z } from 'zod';
import { create } from 'zustand';
import * as React from 'react';
import type * as ReactQuery from '@tanstack/react-query';
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import type {
  UseMutationOptions,
  UseMutationResult,
  UseQueryResult,
} from '@tanstack/react-query';

import { env } from '@/lib/env';
import { dataTableConfig } from '@/config/data-table';
import { sanitizeBranchName } from '@/lib/utils/git-validation';
import { providerCatalogSchema } from '@/features/model-config/provider-schema';

import type {
  DetectionProgress,
  GitHubRepoRequestConfiguration,
  GitHubRepoSummary,
  PaginatedResponse,
} from '@/types';
import type { ProviderFieldPrimitive } from '@/features/model-config/provider-schema';
import type { RepositoryConfig } from '@/components/custom/CodebaseForm';
import { AxiosInstance as HttpClient } from 'axios';
import { type GitHubRepoRequestConfiguration as RepoConfig, type GitHubRepoSummary as RepoSummary, sanitizeBranchName as normalizeBranch } from '@/types';

export type { DetectionProgress } from '@/types';

// ----------------------------------------------------------------------------
// API CLIENTS
// ----------------------------------------------------------------------------

const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const queryEngineClient: AxiosInstance = axios.create({
  baseURL: env.queryEngineUrl,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ApiResponse {
  success: boolean;
  message?: string;
}

export interface ApiError {
  message: string;
  statusCode?: number;
  details?: unknown;
  isAxiosError: boolean;
}

export const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiResponse>;

    return {
      message:
        axiosError.response?.data?.message ??
        axiosError.message ??
        'Unknown API error',
      statusCode: axiosError.response?.status,
      details: axiosError.response?.data,
      isAxiosError: true,
    };
  }

  return {
    message: error instanceof Error ? error.message : 'Unknown error',
    details: error,
    isAxiosError: false,
  };
};

// ----------------------------------------------------------------------------
// API OPERATIONS
// ----------------------------------------------------------------------------

export const submitGitHubToken = async (token: string): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post(
      '/ingest-token',
      null,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': undefined,
        },
      },
    );

    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

export const fetchGitHubRepositories = async (
  page: number,
  perPage: number,
  filterValues?: Record<string, string | string[] | null>,
  cursor?: string,
): Promise<PaginatedResponse<GitHubRepoSummary>> => {
  try {
    const params: Record<string, string | number> = {
      page,
      per_page: perPage,
    };

    if (filterValues) {
      params.filterValues = JSON.stringify(filterValues);
    }

    if (cursor) {
      params.cursor = cursor;
    }

    const response: AxiosResponse<PaginatedResponse<GitHubRepoSummary>> =
      await apiClient.get('/repos', { params });

    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

export const submitRepositoryConfig = async (
  repositoryConfig: GitHubRepoRequestConfiguration,
): Promise<ApiResponse> => {
  try {
    const response: AxiosResponse<ApiResponse> = await apiClient.post(
      '/start-ingestion',
      repositoryConfig,
    );

    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

// ----------------------------------------------------------------------------
// MODULE FUNCTION DECLARATIONS (SYNC + ASYNC VARIANTS)
// ----------------------------------------------------------------------------

export function formatRepositoryLabel(owner: string, repo: string): string {
  return `${owner.trim().toLowerCase()}/${repo.trim().toLowerCase()}`;
}

function createRepositoryRequestFromSummary(
  summary: GitHubRepoSummary,
): GitHubRepoRequestConfiguration {
  const owner =
    (summary as { owner?: string }).owner ??
    (summary as { repository_owner?: string }).repository_owner ??
    'unknown-owner';
  const name =
    (summary as { name?: string }).name ??
    (summary as { repository_name?: string }).repository_name ??
    'unknown-repo';

  return {
    owner,
    repository: name,
    label: formatRepositoryLabel(owner, name),
  } as GitHubRepoRequestConfiguration;
}

export async function provisionRepositoryAccess(
  token: string,
  summary: GitHubRepoSummary,
): Promise<ApiResponse> {
  await submitGitHubToken(token);
  const configuration = createRepositoryRequestFromSummary(summary);
  return submitRepositoryConfig(configuration);
}

async function refreshRepositoryTokens(tokens: string[]): Promise<void> {
  for (const token of tokens) {
    await submitGitHubToken(token);
  }
}

export default function createDefaultRepositoryConfig(): RepositoryConfig {
  return {
    owner: '',
    repository: '',
    branches: [],
  } as RepositoryConfig;
}

export const pollDetectionProgress = async (
  ingestionId: string,
): Promise<DetectionProgress> => {
  try {
    const response: AxiosResponse<DetectionProgress> = await queryEngineClient.get(
      `/detection/${ingestionId}`,
    );

    return response.data;
  } catch (error: unknown) {
    throw handleApiError(error);
  }
};

// ----------------------------------------------------------------------------
// REPOSITORY STORE (zustand pattern)
// ----------------------------------------------------------------------------

interface RepositoryConfigState {
  repositoryConfigs: Record<string, RepositoryConfig>;
  selectedRepository: string | null;
  saveStatus: {
    repoName: string | null;
    success: boolean;
    hasCodebases: boolean;
  } | null;
}

interface RepositoryConfigActions {
  setRepositoryConfigs: (
    configs: Record<string, RepositoryConfig>,
  ) => void;
  upsertRepositoryConfig: (config: RepositoryConfig) => void;
  setSelectedRepository: (repoName: string | null) => void;
  setSaveStatus: (
    status: RepositoryConfigState['saveStatus'],
  ) => void;
  clearSaveStatus: () => void;
}

export const useRepositoryConfigStore = create<
  RepositoryConfigState & RepositoryConfigActions
>()((set) => ({
  repositoryConfigs: {},
  selectedRepository: null,
  saveStatus: null,

  setRepositoryConfigs: (configs) => {
    set({ repositoryConfigs: configs });
  },

  upsertRepositoryConfig: (config) => {
    set((state) => {
      const nextConfigs = {
        ...state.repositoryConfigs,
        [config.repositoryName]: config,
      };

      return {
        repositoryConfigs: nextConfigs,
        saveStatus: {
          repoName: config.repositoryName,
          success: true,
          hasCodebases: Boolean(config.codebases?.length),
        },
      };
    });
  },

  setSelectedRepository: (repoName) => {
    set({ selectedRepository: repoName });
  },

  setSaveStatus: (status) => {
    set({ saveStatus: status });
  },

  clearSaveStatus: () => {
    set({ saveStatus: null });
  },
}));

// ----------------------------------------------------------------------------
// PARSER HELPERS (nuqs + zod)
// ----------------------------------------------------------------------------

const sortingItemSchema = z.object({
  id: z.string(),
  desc: z.boolean(),
});

const filterItemSchema = z.object({
  id: z.string(),
  value: z.union([z.string(), z.array(z.string())]),
  variant: z.enum(dataTableConfig.filterVariants),
  operator: z.enum(dataTableConfig.operators),
  filterId: z.string(),
});

export type FilterItemSchema = z.infer<typeof filterItemSchema>;

export type ExtendedColumnSort<TData> = {
  id: string;
  desc: boolean;
  meta?: Partial<TData>;
};

export type ExtendedColumnFilter<TData> = FilterItemSchema & {
  appliedAt: number;
  preview?: TData;
};

export interface ProviderFieldState {
  readonly key: string;
  readonly value: ProviderFieldPrimitive | null;
}

export type ModelProviderDefinitions = ReadonlyArray<
  z.infer<typeof providerCatalogSchema>['providers'][number]
>;

export enum PollingStatus {
  Idle = 'idle',
  Running = 'running',
  Completed = 'completed',
  Error = 'error',
}

const enum FeatureFlag {
  Chat = 'feature-chat',
  Analytics = 'feature-analytics',
}

export type PollingJob = {
  id: string;
  status: PollingStatus;
  progress: number;
  lastUpdated: string;
};

const detectionStateWeights: Record<DetectionProgress['state'], number> = {
  initializing: 10,
  cloning: 40,
  analyzing: 80,
  complete: 100,
};

const resolvePollingStatus = (state: DetectionProgress['state']): PollingStatus =>
  state === 'complete' ? PollingStatus.Completed : PollingStatus.Running;

export const createPollingJob = (
  id: string,
  status: PollingStatus,
  progress: number,
): PollingJob => ({
  id,
  status,
  progress,
  lastUpdated: new Date().toISOString(),
});

export const ensureRepoKey = (owner: string, repo: string): string => {
  const slug = `${owner}/${repo}`;
  return sanitizeBranchName(slug);
};

// ----------------------------------------------------------------------------
// DATA TABLE PARSERS (nuqs + zod)
// ----------------------------------------------------------------------------

export const getSortingStateParser = <TData>(
  columnIds?: string[] | Set<string>,
) => {
  const validKeys =
    columnIds instanceof Set
      ? columnIds
      : columnIds
        ? new Set(columnIds)
        : null;

  return createParser({
    parse: (value) => {
      try {
        const parsed = JSON.parse(value);
        const result = z.array(sortingItemSchema).safeParse(parsed);

        if (!result.success) return null;

        if (validKeys && result.data.some((item) => !validKeys.has(item.id))) {
          return null;
        }

        return result.data as ExtendedColumnSort<TData>[];
      } catch {
        return null;
      }
    },
    serialize: (value) => JSON.stringify(value),
    eq: (a, b) =>
      a.length === b.length &&
      a.every(
        (item, index) =>
          item.id === b[index]?.id && item.desc === b[index]?.desc,
      ),
  });
};

export const getFiltersStateParser = <TData>(
  columnIds?: string[] | Set<string>,
) => {
  const validKeys =
    columnIds instanceof Set
      ? columnIds
      : columnIds
        ? new Set(columnIds)
        : null;

  return createParser({
    parse: (value) => {
      try {
        const parsed = JSON.parse(value);
        const result = z.array(filterItemSchema).safeParse(parsed);

        if (!result.success) return null;

        if (validKeys && result.data.some((item) => !validKeys.has(item.id))) {
          return null;
        }

        return result.data as ExtendedColumnFilter<TData>[];
      } catch {
        return null;
      }
    },
    serialize: (value) => JSON.stringify(value),
    eq: (a, b) =>
      a.length === b.length &&
      a.every(
        (filter, index) =>
          filter.id === b[index]?.id &&
          filter.value === b[index]?.value &&
          filter.variant === b[index]?.variant &&
          filter.operator === b[index]?.operator,
      ),
  });
};

// ----------------------------------------------------------------------------
// CUSTOM HOOKS (no JSX)
// ----------------------------------------------------------------------------

export const useRepositoryPolling = (): UseMutationResult<
  PollingJob,
  ApiError,
  string
> => {
  const queryClient = useQueryClient();

  const options: UseMutationOptions<PollingJob, ApiError, string> = {
    mutationFn: async (ingestionId: string) => {
      const detection = await pollDetectionProgress(ingestionId);
      const status = resolvePollingStatus(detection.state);
      const progress = detectionStateWeights[detection.state] ?? 0;

      return createPollingJob(ingestionId, status, progress);
    },
    onSuccess: (job) => {
      queryClient.setQueryData(['detection', job.id], job);
    },
  };

  return useMutation(options);
};

export const useModelConfig = (): UseQueryResult<
  ModelProviderDefinitions | null,
  ApiError
> => {
  return useQuery({
    queryKey: ['model-config'],
    queryFn: async () => {
      const response = await apiClient.get('/model-config');
      return response.data as ModelProviderDefinitions | null;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 3,
    retryDelay: (attemptIndex) =>
      Math.min(1000 * 2 ** attemptIndex, 30_000),
  });
};

// ----------------------------------------------------------------------------
// CLASSES AND DECORATORS
// ----------------------------------------------------------------------------

function logInvocation(
  _target: object,
  propertyKey: string,
  descriptor: PropertyDescriptor,
) {
  const original = descriptor.value as (...args: unknown[]) => unknown;

  descriptor.value = function (...args: unknown[]) {
    console.info(`[api] ${propertyKey}`, ...args);
    return original.apply(this, args);
  };
}

class RepositoryCache {
  #cache = new Map<string, PollingJob>();

  get(id: string): PollingJob | undefined {
    return this.#cache.get(id);
  }

  set(job: PollingJob) {
    this.#cache.set(job.id, job);
  }

  clear() {
    this.#cache.clear();
  }
}

class InstrumentedFetcher extends RepositoryCache {
  @logInvocation
  async fetchJob(id: string): Promise<PollingJob | undefined> {
    if (!this.get(id)) {
      const detection = await pollDetectionProgress(id);
      const status = resolvePollingStatus(detection.state);
      const progress = detectionStateWeights[detection.state] ?? 0;
      this.set(createPollingJob(id, status, progress));
    }

    return this.get(id);
  }
}

export const repositoryCache = new InstrumentedFetcher();

// Abstract class with decorator, extends, and implements for heritage testing
interface Auditable {
  createdAt: Date;
  updatedAt: Date;
  auditLog(): void;
}

interface Serializable {
  toJSON(): Record<string, unknown>;
}

interface Loggable {
  log(message: string): void;
}

interface Base {
  id: string;
}

function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
abstract class BaseRepository<T> extends RepositoryCache implements Auditable {
  createdAt: Date = new Date();
  updatedAt: Date = new Date();

  abstract find(id: string): Promise<T | undefined>;
  abstract save(entity: T): Promise<void>;
  abstract delete(id: string): Promise<boolean>;

  auditLog(): void {
    console.log(`[Audit] Repository accessed at ${this.updatedAt}`);
  }

  protected updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}

export class ApiResource<T extends Base> implements Serializable, Loggable {
  static readonly API_VERSION = 'v1';
  static cache = new Map<string, unknown>();

  readonly resourceType: string;
  private data: T;

  constructor(resourceType: string, data: T) {
    this.resourceType = resourceType;
    this.data = data;
  }

  public async fetch(): Promise<T> {
    return this.data;
  }

  public get id(): string {
    return this.data.id;
  }

  private set id(value: string) {
    this.data.id = value;
  }

  toJSON(): Record<string, unknown> {
    return { resourceType: this.resourceType, data: this.data };
  }

  log(message: string): void {
    console.log(`[${this.resourceType}] ${message}`);
  }

  protected validate(): boolean {
    return Boolean(this.data.id);
  }

  static async refreshAll(): Promise<void> {
    this.cache.clear();
  }
}

export default class DefaultWorker {
  private taskQueue: string[] = [];

  async processNext(): Promise<string | undefined> {
    return this.taskQueue.shift();
  }
}

class ComprehensiveModifiers {
  public publicField: string = 'public';
  protected protectedField: number = 42;
  private privateField: boolean = true;
  readonly readonlyField: Date = new Date();
  static readonly STATIC_READONLY = 'constant';
  static staticMutable = 0;

  public constructor(initial: string) {
    this.publicField = initial;
  }

  public async publicAsyncMethod(): Promise<void> {
    await Promise.resolve();
  }

  protected get protectedGetter(): number {
    return this.protectedField;
  }

  private set privateSetter(value: boolean) {
    this.privateField = value;
  }

  static incrementStatic(): void {
    this.staticMutable++;
  }
}

function paramLog(target: any, propertyKey: string, parameterIndex: number) {
  console.log(`Param decorator: ${propertyKey}[${parameterIndex}]`);
}

class ParameterDecoratorExample {
  processData(@paramLog id: string, @paramLog data: unknown): void {
    console.log(id, data);
  }
}

class RepositoryMaintenance extends InstrumentedFetcher {
  static maintenanceRuns = 0;

  static purgeCache(): void {
    repositoryCache.clear();
    this.maintenanceRuns += 1;
  }

  static async hydrateAll(ids: readonly string[]): Promise<void> {
    await Promise.all(ids.map((id) => repositoryCache.fetchJob(id)));
    this.maintenanceRuns += ids.length;
  }

  @logInvocation
  static async rebuildIndexes(indexes: readonly string[]): Promise<void> {
    for (const indexName of indexes) {
      console.debug(`[maintenance] rebuilding index ${indexName}`);
    }

    this.maintenanceRuns += indexes.length;
  }

  async refreshJob(id: string): Promise<PollingJob | undefined> {
    RepositoryMaintenance.maintenanceRuns += 1;
    return this.fetchJob(id);
  }

  processJob = async (id: string): Promise<PollingJob | undefined> => {
    return this.fetchJob(id);
  };
}

class RepositoryWorker {
  constructor(private readonly maintenance: RepositoryMaintenance) {}

  processJob = async (id: string): Promise<PollingJob | undefined> => {
    return this.maintenance.refreshJob(id);
  };

  async schedule(ids: readonly string[]): Promise<void> {
    await RepositoryMaintenance.hydrateAll(ids);
  }
}

export const repositoryMaintenance = new RepositoryMaintenance();
export const repositoryWorker = new RepositoryWorker(repositoryMaintenance);

// Global var declarations for variable_declaration testing
var globalCounter = 0;
var legacyFlag: boolean;
var deprecatedConfig: Record<string, unknown> | undefined;

// ----------------------------------------------------------------------------
// ADDITIONAL FUNCTION PATTERNS FOR COMPONENT SIGNATURE TESTING
// ----------------------------------------------------------------------------

// Variable binding with type annotation (arrow function)
type HandlerFn = (id: string) => Promise<void>;
const typedHandler: HandlerFn = async (id: string) => {
  console.log(`Handling ${id}`);
};

// var binding with arrow function
var legacyHandler = async (message: string): Promise<boolean> => {
  return message.length > 0;
};

var simpleLegacyFn = (x: number) => x * 2;

// Function expressions (const/let bindings)
const anonymousFn = function (input: string): string {
  return input.toUpperCase();
};

const namedFunctionExpr = function processData(data: unknown[]): number {
  return data.length;
};

let asyncFunctionExpr = async function validateInput(
  value: string,
): Promise<boolean> {
  return value.trim().length > 0;
};

// Function expressions (var bindings)
var oldStyleFn = function (a: number, b: number): number {
  return a + b;
};

var namedOldStyleFn = function computeSum(nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0);
};

// Generator functions
function* simpleGenerator(): Generator<number, void, unknown> {
  yield 1;
  yield 2;
  yield 3;
}

export function* exportedGenerator<T>(
  items: T[],
): Generator<T, void, unknown> {
  for (const item of items) {
    yield item;
  }
}

async function* asyncGenerator(
  count: number,
): AsyncGenerator<number, void, unknown> {
  for (let i = 0; i < count; i++) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    yield i;
  }
}

export async function* exportedAsyncGen(): AsyncGenerator<
  string,
  void,
  unknown
> {
  yield 'first';
  yield 'second';
}

// ----------------------------------------------------------------------------
// DYNAMIC IMPORTS & ENVIRONMENT HELPERS
// ----------------------------------------------------------------------------

export const loadProviderCatalog = async () => {
  const module = await import('virtual:env-safe');
  return module.safeEnv;
};

export const loadFeatureFlags = async () => {
  const { safeEnv } = await import('virtual:env-safe');
  return {
    chat: safeEnv[FeatureFlag.Chat] === 'enabled',
    analytics: safeEnv[FeatureFlag.Analytics] === 'enabled',
  };
};

// ----------------------------------------------------------------------------
// DECLARATIONS, NAMESPACES, AND TYPE ASSERTIONS
// ----------------------------------------------------------------------------

declare module 'virtual:env-safe' {
  export const safeEnv: Record<string, string>;
}

declare global {
  interface ImportMetaEnv {
    readonly VITE_APP_VERSION?: string;
    readonly VITE_FEATURE_CHAT?: 'enabled' | 'disabled';
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export namespace Diagnostics {
  export const record = (event: string, payload: Record<string, unknown>) => {
    console.debug(`[diagnostics] ${event}`, payload);
  };
}

const forcedFlags =
  (window as unknown as { __APP_FLAGS__?: Record<string, boolean> })
    .__APP_FLAGS__ ?? {};

export const featureFlagFromWindow = (key: string): boolean =>
  Boolean(forcedFlags[key]);

// ----------------------------------------------------------------------------
// MODULE SIDE EFFECT (ensures bootstrap still parses without TSX)
// ----------------------------------------------------------------------------

const bootstrap = () => {
  if (import.meta.env.DEV) {
    console.info('Bootstrap completed');
  }
};

void loadFeatureFlags().then(bootstrap);
