import { useEffect, useMemo, useState } from "react";

interface LanguageEntry {
  language: string;
  libraries: string[];
}

interface LanguageIndex {
  generated_at: string;
  schema_version: string;
  languages: LanguageEntry[];
}

interface LanguageRow {
  language: string;
  libraries: string[];
}

const LANGUAGE_INDEX_PATH = "/framework-definitions/language-index.json";

export function FrameworkCatalogSummary() {
  const [languageIndex, setLanguageIndex] = useState<LanguageIndex | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const abortController = new AbortController();

    async function loadLanguageIndex() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const response = await fetch(LANGUAGE_INDEX_PATH, {
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`Failed to load ${LANGUAGE_INDEX_PATH}: ${response.status}`);
        }

        const payload = (await response.json()) as LanguageIndex;
        setLanguageIndex(payload);
      } catch (error) {
        if (abortController.signal.aborted) {
          return;
        }

        if (error instanceof Error) {
          setErrorMessage(error.message);
          return;
        }

        setErrorMessage("Unknown error while loading framework catalog index.");
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    void loadLanguageIndex();

    return () => {
      abortController.abort();
    };
  }, []);

  const rows = useMemo<LanguageRow[]>(() => {
    if (!languageIndex) {
      return [];
    }

    return [...languageIndex.languages]
      .map((entry) => ({
        language: entry.language,
        libraries: [...entry.libraries].sort((left, right) => left.localeCompare(right)),
      }))
      .sort((left, right) => left.language.localeCompare(right.language));
  }, [languageIndex]);

  if (isLoading) {
    return <p className="text-sm text-fd-muted-foreground">Loading framework catalog index...</p>;
  }

  if (errorMessage) {
    return <p className="text-sm text-red-700 dark:text-red-300">{errorMessage}</p>;
  }

  if (!languageIndex || rows.length === 0) {
    return <p className="text-sm text-fd-muted-foreground">No frameworks are currently listed in the catalog index.</p>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-fd-muted-foreground">
        Generated from <code>{LANGUAGE_INDEX_PATH}</code> ({languageIndex.schema_version}).
      </p>
      <div className="overflow-x-auto rounded-lg border border-fd-border">
        <table className="w-full min-w-[760px] text-sm">
          <thead className="bg-fd-muted/50 text-left">
            <tr>
              <th className="px-3 py-2 font-semibold">Programming language</th>
              <th className="px-3 py-2 font-semibold">Frameworks supported</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr className="border-t border-fd-border align-top" key={row.language}>
                <td className="px-3 py-3 font-mono text-xs">{row.language}</td>
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-2">
                    {row.libraries.map((library) => {
                      const docsCatalogPath =
                        `/docs/contribution/custom-framework-schema/catalog/${row.language}/${library}`;

                      return (
                        <a
                          className="inline-flex items-center rounded-full border border-fd-border bg-fd-card px-2.5 py-1 font-mono text-xs hover:bg-fd-accent"
                          href={docsCatalogPath}
                          key={`${row.language}-${library}`}
                        >
                          {library}
                        </a>
                      );
                    })}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
