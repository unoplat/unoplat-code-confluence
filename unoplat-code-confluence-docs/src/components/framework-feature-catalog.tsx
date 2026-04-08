import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type FeatureTargetLevel = "function" | "class";

interface FeatureDefinition {
  description: string;
  absolute_paths: string[];
  target_level: FeatureTargetLevel;
  concept: string;
  locator_strategy?: string;
  construct_query?: Record<string, string>;
  startpoint?: boolean;
}

interface LibraryDefinition {
  docs_url?: string;
  description?: string;
  version?: string;
  features: Record<string, FeatureDefinition>;
}

type FrameworkDefinitionFile = Record<string, Record<string, LibraryDefinition>>;

interface FeatureRow {
  featureKey: string;
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
          throw new Error(`${label} definition is missing from static catalog payload.`);
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

        setErrorMessage(`Unknown error while loading ${label} catalog.`);
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
    if (!libraryDefinition?.features) {
      return [];
    }

    return Object.entries(libraryDefinition.features)
      .map(([featureKey, feature]) => ({
        featureKey,
        feature,
      }))
      .sort((left, right) => left.featureKey.localeCompare(right.featureKey));
  }, [libraryDefinition]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading {label} catalog...</CardTitle>
          <CardDescription>Reading static catalog asset from /framework-definitions.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (errorMessage) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Unable to load {label} catalog</CardTitle>
          <CardDescription>{errorMessage}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!libraryDefinition) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{label} catalog is empty</CardTitle>
          <CardDescription>
            No {label} features were found in the static catalog payload.
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
        <Badge variant="outline">{featureRows.length} features</Badge>
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

      <div className="overflow-x-auto rounded-lg border border-fd-border">
        <table className="w-full min-w-[980px] text-sm">
          <thead className="bg-fd-muted/50 text-left">
            <tr>
              <th className="px-3 py-2 font-semibold">feature_key</th>
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
                <td className="px-3 py-3 font-mono text-xs">{row.featureKey}</td>
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
    </div>
  );
}
