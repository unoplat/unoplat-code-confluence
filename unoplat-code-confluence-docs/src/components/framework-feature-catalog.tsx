import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

type FeatureTargetLevel = "function" | "class";

interface FeatureDefinition {
  description: string;
  absolute_paths: string[];
  target_level: FeatureTargetLevel;
  concept: string;
  locator_strategy?: string;
  construct_query?: Record<string, string>;
  startpoint?: boolean;
  base_confidence?: number;
  notes?: string;
}

interface CapabilityDefinition {
  description?: string;
  operations?: Record<string, FeatureDefinition>;
}

interface LibraryDefinition {
  docs_url?: string;
  description?: string;
  version?: string;
  features?: Record<string, FeatureDefinition>;
  capabilities?: Record<string, CapabilityDefinition>;
}

type FrameworkDefinitionFile = Record<string, Record<string, LibraryDefinition>>;

interface FeatureRow {
  featureKey: string;
  capabilityKey?: string;
  operationKey?: string;
  feature: FeatureDefinition;
}

interface FrameworkFeatureCatalogProps {
  language: string;
  library: string;
  displayName?: string;
}

function formatConstructQuery(constructQuery?: Record<string, string>): string {
  if (!constructQuery) {
    return "-";
  }

  return Object.entries(constructQuery)
    .map(([key, value]) => `${key}: ${value}`)
    .join("; ");
}

function toTitleCase(value: string): string {
  return value
    .split(/[-_\s]+/)
    .filter((token) => token.length > 0)
    .map((token) => `${token.charAt(0).toUpperCase()}${token.slice(1)}`)
    .join(" ");
}

function getLibraryFromPayload(
  payload: FrameworkDefinitionFile,
  language: string,
  library: string,
): LibraryDefinition | null {
  const languageDefinitions = payload[language];
  if (!languageDefinitions) {
    return null;
  }

  return languageDefinitions[library] ?? null;
}

export function FrameworkFeatureCatalog({
  language,
  library,
  displayName,
}: FrameworkFeatureCatalogProps) {
  const normalizedLanguage = language.toLowerCase();
  const normalizedLibrary = library.toLowerCase();
  const label = displayName ?? toTitleCase(normalizedLibrary);
  const definitionPath = `/framework-definitions/${normalizedLanguage}/${normalizedLibrary}.json`;

  const [libraryDefinition, setLibraryDefinition] = useState<LibraryDefinition | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const abortController = new AbortController();

    async function loadCatalog() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const response = await fetch(definitionPath, {
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`Failed to load ${definitionPath}: ${response.status}`);
        }

        const payload = (await response.json()) as FrameworkDefinitionFile;
        const selectedLibrary = getLibraryFromPayload(
          payload,
          normalizedLanguage,
          normalizedLibrary,
        );

        if (!selectedLibrary) {
          throw new Error(`${label} definition is missing from the static framework definition payload.`);
        }

        setLibraryDefinition(selectedLibrary);
      } catch (error) {
        if (abortController.signal.aborted) {
          return;
        }

        if (error instanceof Error) {
          setErrorMessage(error.message);
          return;
        }

        setErrorMessage(`Unknown error while loading the ${label} coverage reference.`);
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    void loadCatalog();

    return () => {
      abortController.abort();
    };
  }, [definitionPath, label, normalizedLanguage, normalizedLibrary]);

  const featureRows = useMemo<FeatureRow[]>(() => {
    if (!libraryDefinition) {
      return [];
    }

    const rowsFromFeatures = Object.entries(libraryDefinition.features ?? {}).map(
      ([featureKey, feature]) => ({
        featureKey,
        operationKey: featureKey,
        feature,
      }),
    );

    const rowsFromCapabilities = Object.entries(libraryDefinition.capabilities ?? {}).flatMap(
      ([capabilityKey, capability]) =>
        Object.entries(capability.operations ?? {}).map(([operationKey, feature]) => ({
          capabilityKey,
          operationKey,
          featureKey: `${capabilityKey}.${operationKey}`,
          feature,
        })),
    );

    const rows = rowsFromCapabilities.length > 0 ? rowsFromCapabilities : rowsFromFeatures;

    return rows.sort((left, right) => left.featureKey.localeCompare(right.featureKey));
  }, [libraryDefinition]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading {label} coverage reference...</CardTitle>
          <CardDescription>Reading static framework definition asset from /framework-definitions.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (errorMessage) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Unable to load {label} coverage reference</CardTitle>
          <CardDescription>{errorMessage}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!libraryDefinition) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{label} coverage reference is empty</CardTitle>
          <CardDescription>
            No {label} definitions were found in the static framework definition payload.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (featureRows.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{label} coverage reference is empty</CardTitle>
          <CardDescription>
            No {label} definitions were found in the published framework definition payload.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant="secondary">{normalizedLanguage}</Badge>
        <Badge variant="outline">{label}</Badge>
        <Badge variant="outline">{featureRows.length} definitions</Badge>
        {libraryDefinition.docs_url ? (
          <a
            className="text-sm text-primary hover:underline"
            href={libraryDefinition.docs_url}
            rel="noopener noreferrer"
            target="_blank"
          >
            {label} docs
          </a>
        ) : null}
      </div>

      {libraryDefinition.description ? (
        <p className="text-sm text-muted-foreground">{libraryDefinition.description}</p>
      ) : null}

      <div className="space-y-4">
        <div className="overflow-x-auto pb-2">
          <table className="w-full min-w-[980px] text-sm">
            <thead className="bg-fd-muted/50 text-left">
              <tr>
                <th className="px-3 py-2 font-semibold">capability</th>
                <th className="px-3 py-2 font-semibold">operation</th>
                <th className="px-3 py-2 font-semibold">description</th>
                <th className="px-3 py-2 font-semibold">concept</th>
                <th className="px-3 py-2 font-semibold">target_level</th>
                <th className="px-3 py-2 font-semibold">startpoint</th>
                <th className="px-3 py-2 font-semibold">absolute_paths</th>
                <th className="px-3 py-2 font-semibold">construct_query</th>
              </tr>
            </thead>
            <tbody>
              {featureRows.map((row) => (
                <tr className="border-t border-fd-border align-top" key={row.featureKey}>
                  <td className="px-3 py-3 font-mono text-xs">{row.capabilityKey ?? "-"}</td>
                  <td className="px-3 py-3 font-mono text-xs">{row.operationKey ?? "-"}</td>
                  <td className="px-3 py-3 text-xs text-fd-muted-foreground">{row.feature.description}</td>
                  <td className="px-3 py-3 font-mono text-xs">{row.feature.concept}</td>
                  <td className="px-3 py-3 font-mono text-xs">{row.feature.target_level}</td>
                  <td className="px-3 py-3 text-xs">
                    {row.feature.startpoint ? (
                      <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-800 dark:bg-green-900 dark:text-green-200">
                        true
                      </span>
                    ) : (
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                        false
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-3">
                    <ul className="list-disc space-y-1 pl-4">
                      {row.feature.absolute_paths.map((absolutePath) => (
                        <li className="font-mono text-xs" key={absolutePath}>
                          {absolutePath}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className="px-3 py-3 font-mono text-xs">
                    {formatConstructQuery(row.feature.construct_query)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <Separator className="my-2" />
      </div>
    </div>
  );
}
