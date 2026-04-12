#!/usr/bin/env node

import { copyFile, mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DOCS_ROOT = path.resolve(SCRIPT_DIR, "..");
const SOURCE_ROOT = path.resolve(
  DOCS_ROOT,
  "..",
  "unoplat-code-confluence-ingestion",
  "code-confluence-flow-bridge",
  "framework-definitions",
);
const TARGET_ROOT = path.resolve(DOCS_ROOT, "public", "framework-definitions");
const SCHEMA_PATH = path.resolve(
  DOCS_ROOT,
  "public",
  "schemas",
  "custom-framework-lib-schema-v4.json",
);
const DIDS_CATALOG_ROOT = path.resolve(
  DOCS_ROOT,
  "content",
  "docs",
  "supported-frameworks",
);
const CATALOG_DATA_PATH = path.resolve(DOCS_ROOT, "src", "data", "framework-catalog-data.json");
const CANONICAL_DEFINITIONS_TREE_URL =
  "https://github.com/unoplat/unoplat-code-confluence/tree/dev/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions";
const CANONICAL_DEFINITIONS_BLOB_BASE_URL =
  "https://github.com/unoplat/unoplat-code-confluence/blob/dev/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions";

const DISPLAY_NAME_OVERRIDES = {
  fastapi: "FastAPI",
  pydantic: "Pydantic",
  sqlalchemy: "SQLAlchemy",
  sqlmodel: "SQLModel",
};

function getLibraryName(fileName) {
  return fileName.replace(/\.json$/i, "");
}

function toTitleCase(value) {
  return value
    .split(/[-_\s]+/)
    .filter((token) => token.length > 0)
    .map((token) => `${token.charAt(0).toUpperCase()}${token.slice(1)}`)
    .join(" ");
}

function getDisplayName(library) {
  return DISPLAY_NAME_OVERRIDES[library] ?? toTitleCase(library);
}

async function pathExists(filePath) {
  try {
    await stat(filePath);
    return true;
  } catch {
    return false;
  }
}

function getSchemaVersionFromTitle(title) {
  const matchedVersion = title.match(/v(\d+)\b/i);
  if (!matchedVersion) {
    return "unknown";
  }

  return `v${matchedVersion[1]}`;
}

function getGeneratedAtTimestamp() {
  try {
    const output = execFileSync(
      "git",
      ["log", "-1", "--format=%cI", "--", SOURCE_ROOT],
      {
        cwd: DOCS_ROOT,
        encoding: "utf-8",
      },
    ).trim();

    if (output.length > 0) {
      return output;
    }
  } catch {
    // no-op; fallback below
  }

  return new Date(0).toISOString();
}

async function getSchemaVersion() {
  try {
    const schemaFileContent = await readFile(SCHEMA_PATH, "utf-8");
    const schema = JSON.parse(schemaFileContent);
    const schemaTitle = typeof schema.title === "string" ? schema.title : "";
    return getSchemaVersionFromTitle(schemaTitle);
  } catch {
    return "unknown";
  }
}

async function listLanguageDirectories() {
  const entries = await readdir(SOURCE_ROOT, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));
}

async function listLibraryJsonFiles(language) {
  const languagePath = path.resolve(SOURCE_ROOT, language);
  const entries = await readdir(languagePath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".json"))
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));
}

async function ensureValidSource() {
  const sourceStats = await stat(SOURCE_ROOT);
  if (!sourceStats.isDirectory()) {
    throw new Error(`Framework definitions source is not a directory: ${SOURCE_ROOT}`);
  }
}

function buildLibraryCatalogPageContent({ language, library }) {
  const displayName = getDisplayName(library);
  const definitionFilePath = `${language}/${library}.json`;
  const canonicalDefinitionUrl = `${CANONICAL_DEFINITIONS_BLOB_BASE_URL}/${definitionFilePath}`;

  return `---
title: ${displayName}
description: "Static ${displayName} feature catalog powered by DIDS framework definitions"
---

import { Callout } from 'fumadocs-ui/components/callout';
import { FrameworkFeatureCatalog } from '../../../../src/components/framework-feature-catalog';

# ${displayName} Feature Catalog (${toTitleCase(language)})

This page provides a static, contributor-friendly view of ${displayName} features currently covered by the Deterministic Interface Discovery Schema (DIDS).

<Callout type="info" title="Source of Truth">
  - Canonical definitions live in ingestion: [framework-definitions directory](${CANONICAL_DEFINITIONS_TREE_URL})
  - Canonical ${displayName} file: [framework-definitions/${definitionFilePath}](${canonicalDefinitionUrl})
  - Docs consume generated static assets from: \`/framework-definitions\`
  - Current file shown here: [\`/framework-definitions/${definitionFilePath}\`](/framework-definitions/${definitionFilePath})
</Callout>

## Why this catalog exists

This catalog makes deterministic feature coverage visible so contributors can evolve discovery rules safely.

## Current ${displayName} coverage

<FrameworkFeatureCatalog displayName="${displayName}" language="${language}" library="${library}" />

## How to update this page's data

1. Update ${displayName} definitions in ingestion source.
2. Run \`bun run sync:framework-definitions\` from \`unoplat-code-confluence-docs\`.
3. Commit both source definition changes and generated docs artifacts.
`;
}

async function syncCatalogDocs(languageRows) {
  await mkdir(DIDS_CATALOG_ROOT, { recursive: true });

  const catalogMetaPath = path.resolve(DIDS_CATALOG_ROOT, "meta.json");
  const catalogMeta = {
    title: "Supported Frameworks",
    icon: "Library",
    defaultOpen: true,
    pages: ["index", ...languageRows.map((row) => row.language)],
  };
  await writeFile(catalogMetaPath, `${JSON.stringify(catalogMeta, null, 2)}\n`, "utf-8");

  for (const row of languageRows) {
    const languageDir = path.resolve(DIDS_CATALOG_ROOT, row.language);
    await mkdir(languageDir, { recursive: true });

    const languageMetaPath = path.resolve(languageDir, "meta.json");
    const languageMeta = {
      title: toTitleCase(row.language),
      pages: row.libraries,
    };
    await writeFile(languageMetaPath, `${JSON.stringify(languageMeta, null, 2)}\n`, "utf-8");

    for (const library of row.libraries) {
      const pagePath = path.resolve(languageDir, `${library}.mdx`);
      const alreadyExists = await pathExists(pagePath);
      if (alreadyExists) {
        continue;
      }

      const pageContent = buildLibraryCatalogPageContent({
        language: row.language,
        library,
      });
      await writeFile(pagePath, pageContent, "utf-8");
    }
  }
}

async function syncFrameworkDefinitions() {
  await ensureValidSource();

  await rm(TARGET_ROOT, { recursive: true, force: true });
  await mkdir(TARGET_ROOT, { recursive: true });

  const schemaVersion = await getSchemaVersion();
  const generatedAt = getGeneratedAtTimestamp();
  const languages = await listLanguageDirectories();
  const indexLanguages = [];
  const catalogRows = [];

  for (const language of languages) {
    const libraryFiles = await listLibraryJsonFiles(language);
    if (libraryFiles.length === 0) {
      continue;
    }

    const sourceLanguagePath = path.resolve(SOURCE_ROOT, language);
    const targetLanguagePath = path.resolve(TARGET_ROOT, language);
    await mkdir(targetLanguagePath, { recursive: true });

    const libraries = [];
    for (const fileName of libraryFiles) {
      const sourceFilePath = path.resolve(sourceLanguagePath, fileName);
      const targetFilePath = path.resolve(targetLanguagePath, fileName);

      const rawJsonContent = await readFile(sourceFilePath, "utf-8");
      const parsed = JSON.parse(rawJsonContent);
      await copyFile(sourceFilePath, targetFilePath);

      const library = getLibraryName(fileName);
      libraries.push(library);

      const libraryDefinition = parsed[language]?.[library];
      catalogRows.push({
        language,
        library,
        description: libraryDefinition?.description ?? "",
        docsUrl: libraryDefinition?.docs_url ?? "",
        catalogPath: `/docs/supported-frameworks/${language}/${library}`,
      });
    }

    indexLanguages.push({ language, libraries });
  }

  const languageIndex = {
    generated_at: generatedAt,
    schema_version: schemaVersion,
    languages: indexLanguages,
  };

  const languageIndexPath = path.resolve(TARGET_ROOT, "language-index.json");
  await writeFile(languageIndexPath, `${JSON.stringify(languageIndex, null, 2)}\n`, "utf-8");

  await mkdir(path.dirname(CATALOG_DATA_PATH), { recursive: true });
  await writeFile(CATALOG_DATA_PATH, `${JSON.stringify(catalogRows, null, 2)}\n`, "utf-8");

  await syncCatalogDocs(indexLanguages);
}

syncFrameworkDefinitions()
  .then(() => {
    console.log("Synced framework definitions to docs public/framework-definitions.");
  })
  .catch((error) => {
    console.error("Failed to sync framework definitions.");
    console.error(error);
    process.exitCode = 1;
  });
