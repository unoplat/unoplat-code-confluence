from collections.abc import Mapping
import json
from pathlib import Path

from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
    PackageManagerType,
)

T3CODE_GIT_URL = "https://github.com/pingdotgg/t3code"
<<<<<<< HEAD
T3CODE_REF = "f9019cd63f3bc409344418a662d73a8ef065f439"
=======
>>>>>>> origin/main
EXPECTED_T3CODE_CODEBASE_FOLDERS = {
    "apps/desktop",
    "apps/marketing",
    "apps/server",
    "apps/web",
<<<<<<< HEAD
    "packages/client-runtime",
=======
>>>>>>> origin/main
    "packages/contracts",
    "packages/shared",
    "scripts",
}
EXPECTED_T3CODE_PROJECT_NAMES: dict[str, str] = {
    "apps/desktop": "@t3tools/desktop",
    "apps/marketing": "@t3tools/marketing",
    "apps/server": "t3",
    "apps/web": "@t3tools/web",
<<<<<<< HEAD
    "packages/client-runtime": "@t3tools/client-runtime",
=======
>>>>>>> origin/main
    "packages/contracts": "@t3tools/contracts",
    "packages/shared": "@t3tools/shared",
    "scripts": "@t3tools/scripts",
}
EXPECTED_T3CODE_WORKSPACE_ROOTS: dict[str, str] = {
    folder: "." for folder in EXPECTED_T3CODE_CODEBASE_FOLDERS
}

NX_REACT_TEMPLATE_GIT_URL = "https://github.com/nrwl/react-template"
<<<<<<< HEAD
NX_REACT_TEMPLATE_REF = "84a433ecc37c406bed2804b59a7fcfebb613b784"
=======
>>>>>>> origin/main
EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS = {
    "apps/api",
    "apps/shop",
    "apps/shop-e2e",
    "libs/api/products",
    "libs/shared/models",
    "libs/shared/test-utils",
    "libs/shop/data",
    "libs/shop/feature-product-detail",
    "libs/shop/feature-products",
    "libs/shop/shared-ui",
}
EXPECTED_NX_REACT_TEMPLATE_PROJECT_NAMES: dict[str, str] = {
    "apps/api": "@org/api",
    "apps/shop": "@org/shop",
    "apps/shop-e2e": "@org/shop-e2e",
    "libs/api/products": "@org/api-products",
    "libs/shared/models": "@org/models",
    "libs/shared/test-utils": "@org/shared-test-utils",
    "libs/shop/data": "@org/shop-data",
    "libs/shop/feature-product-detail": "@org/shop-feature-product-detail",
    "libs/shop/feature-products": "@org/shop-feature-products",
    "libs/shop/shared-ui": "@org/shop-shared-ui",
}
EXPECTED_NX_REACT_TEMPLATE_WORKSPACE_ROOTS: dict[str, str] = {
    folder: "." for folder in EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS
}

HOPPSCOTCH_GIT_URL = "https://github.com/hoppscotch/hoppscotch"
<<<<<<< HEAD
HOPPSCOTCH_REF = "2837ef789a0e3955fbc0963f4c5a40f4fb7c3493"
=======
>>>>>>> origin/main
EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS = {
    "packages/codemirror-lang-graphql",
    "packages/hoppscotch-agent",
    "packages/hoppscotch-backend",
    "packages/hoppscotch-cli",
    "packages/hoppscotch-common",
    "packages/hoppscotch-data",
    "packages/hoppscotch-desktop",
    "packages/hoppscotch-js-sandbox",
    "packages/hoppscotch-kernel",
    "packages/hoppscotch-selfhost-web",
    "packages/hoppscotch-sh-admin",
    "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-appload",
    "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-relay",
}
EXPECTED_HOPPSCOTCH_PROJECT_NAMES: dict[str, str] = {
    "packages/codemirror-lang-graphql": "@hoppscotch/codemirror-lang-graphql",
    "packages/hoppscotch-agent": "hoppscotch-agent",
    "packages/hoppscotch-backend": "hoppscotch-backend",
    "packages/hoppscotch-cli": "@hoppscotch/cli",
    "packages/hoppscotch-common": "@hoppscotch/common",
    "packages/hoppscotch-data": "@hoppscotch/data",
    "packages/hoppscotch-desktop": "hoppscotch-desktop",
    "packages/hoppscotch-js-sandbox": "@hoppscotch/js-sandbox",
    "packages/hoppscotch-kernel": "@hoppscotch/kernel",
    "packages/hoppscotch-selfhost-web": "@hoppscotch/selfhost-web",
    "packages/hoppscotch-sh-admin": "hoppscotch-sh-admin",
    "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-appload": "@CuriousCorrelation/plugin-appload",
    "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-relay": "@CuriousCorrelation/plugin-relay",
}
EXPECTED_HOPPSCOTCH_PACKAGE_MANAGER_PROVENANCE: dict[str, PackageManagerProvenance] = {
    folder: PackageManagerProvenance.INHERITED
    for folder in EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS
}
EXPECTED_HOPPSCOTCH_PACKAGE_MANAGER_PROVENANCE.update(
    {
        "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-appload": PackageManagerProvenance.LOCAL,
        "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-relay": PackageManagerProvenance.LOCAL,
    }
)
EXPECTED_HOPPSCOTCH_WORKSPACE_ROOTS: dict[str, str | None] = {
    folder: "." for folder in EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS
}
EXPECTED_HOPPSCOTCH_WORKSPACE_ROOTS.update(
    {
        "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-appload": None,
        "packages/hoppscotch-desktop/plugin-workspace/tauri-plugin-relay": None,
    }
)

BUN_RUNTIME_GIT_URL = "https://github.com/oven-sh/bun"
<<<<<<< HEAD
BUN_RUNTIME_REF = "f96981cee4a51f6fffbda73812daf9973d2597c8"
=======
>>>>>>> origin/main
EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS = {
    "bench",
    "packages/bun-debug-adapter-protocol",
    "packages/bun-error",
    "packages/bun-inspector-frontend",
    "packages/bun-inspector-protocol",
    "packages/bun-lambda",
    "packages/bun-plugin-svelte",
    "packages/bun-plugin-yaml",
    "packages/bun-release",
    "packages/bun-types",
    "packages/bun-vscode",
    "packages/bun-wasm",
    "src/bake",
    "src/create/projects/react-shadcn-spa",
    "src/init/react-app",
    "src/init/react-shadcn",
    "src/init/react-tailwind",
    "src/node-fallbacks",
}
EXPECTED_BUN_RUNTIME_PROJECT_NAMES: dict[str, str | None] = {
    "bench": "bench",
    "packages/bun-debug-adapter-protocol": "bun-debug-adapter-protocol",
    "packages/bun-error": "bun-error",
    "packages/bun-inspector-frontend": "web-inspector-bun",
    "packages/bun-inspector-protocol": "bun-inspector-protocol",
    "packages/bun-lambda": "bun-lambda",
    "packages/bun-plugin-svelte": "bun-plugin-svelte",
    "packages/bun-plugin-yaml": "bun-plugin-yaml",
    "packages/bun-release": "bun-release-action",
    "packages/bun-types": "bun-types",
    "packages/bun-vscode": "bun-vscode",
    "packages/bun-wasm": "bun-wasm",
    "src/bake": None,
    "src/create/projects/react-shadcn-spa": "react-tailwind-spa",
    "src/init/react-app": "bun-react-template",
    "src/init/react-shadcn": "bun-react-template",
    "src/init/react-tailwind": "bun-react-template",
    "src/node-fallbacks": "fallbacks",
}
EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER: dict[str, PackageManagerType] = {
    folder: PackageManagerType.BUN for folder in EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS
}
EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER.update(
    {
        "src/bake": PackageManagerType.NPM,
    }
)
EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER_PROVENANCE: dict[
    str, PackageManagerProvenance
] = {
    folder: PackageManagerProvenance.LOCAL
    for folder in EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS
}
EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER_PROVENANCE.update(
    {
        "packages/bun-types": PackageManagerProvenance.INHERITED,
    }
)
EXPECTED_BUN_RUNTIME_WORKSPACE_ROOTS: dict[str, str | None] = {
    folder: None for folder in EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS
}
EXPECTED_BUN_RUNTIME_WORKSPACE_ROOTS.update(
    {
        "packages/bun-types": ".",
    }
)

PRINTDESK_GIT_URL = "https://github.com/declanlscott/printdesk"
<<<<<<< HEAD
PRINTDESK_REF = "bebaabffa354d1a336b4300a18ca5b8deef6693d"
=======
>>>>>>> origin/main
EXPECTED_PRINTDESK_CODEBASE_FOLDERS = {
    "packages/clients/edge-proxy/frontend",
    "packages/clients/web",
    "packages/core",
    "packages/functions",
    "packages/scripts",
    "packages/ui",
    "packages/workers",
    "packages/www",
}
EXPECTED_PRINTDESK_PROJECT_NAMES: dict[str, str] = {
    "packages/clients/edge-proxy/frontend": "@printdesk/edge-proxy",
    "packages/clients/web": "@printdesk/web",
    "packages/core": "@printdesk/core",
    "packages/functions": "@printdesk/functions",
    "packages/scripts": "@printdesk/scripts",
    "packages/ui": "@printdesk/ui",
    "packages/workers": "@printdesk/workers",
    "packages/www": "@printdesk/www",
}
EXPECTED_PRINTDESK_WORKSPACE_ROOTS: dict[str, str] = {
    folder: "." for folder in EXPECTED_PRINTDESK_CODEBASE_FOLDERS
}

APOLLO_SERVER_GIT_URL = "https://github.com/apollographql/apollo-server"
<<<<<<< HEAD
APOLLO_SERVER_REF = "64c0e1bb5d79d571bf448c35aea0b31097e6ce9d"
=======
>>>>>>> origin/main
EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS = {
    "packages/cache-control-types",
    "packages/gateway-interface",
    "packages/integration-testsuite",
    "packages/plugin-response-cache",
    "packages/server",
    "smoke-test",
}
EXPECTED_APOLLO_SERVER_PROJECT_NAMES: dict[str, str | None] = {
    "packages/cache-control-types": "@apollo/cache-control-types",
    "packages/gateway-interface": "@apollo/server-gateway-interface",
    "packages/integration-testsuite": "@apollo/server-integration-testsuite",
    "packages/plugin-response-cache": "@apollo/server-plugin-response-cache",
    "packages/server": "@apollo/server",
    "smoke-test": None,
}
EXPECTED_APOLLO_SERVER_PACKAGE_MANAGER_PROVENANCE: dict[
    str, PackageManagerProvenance
] = {
    folder: PackageManagerProvenance.INHERITED
    for folder in EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS
}
EXPECTED_APOLLO_SERVER_PACKAGE_MANAGER_PROVENANCE.update(
    {
        "smoke-test": PackageManagerProvenance.LOCAL,
    }
)
EXPECTED_APOLLO_SERVER_WORKSPACE_ROOTS: dict[str, str | None] = {
    folder: "." for folder in EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS
}
EXPECTED_APOLLO_SERVER_WORKSPACE_ROOTS.update(
    {
        "smoke-test": None,
    }
)

SOCKETIO_GIT_URL = "https://github.com/socketio/socket.io"
<<<<<<< HEAD
SOCKETIO_REF = "4f7edb46ecff64f523ef14a1aa560fae9d7f431c"
=======
>>>>>>> origin/main
EXPECTED_SOCKETIO_CODEBASE_FOLDERS = {
    # Workspace members (from explicit paths in root package.json "workspaces")
    "packages/engine.io",
    "packages/engine.io-client",
    "packages/engine.io-parser",
    "packages/socket.io",
    "packages/socket.io-adapter",
    "packages/socket.io-client",
    "packages/socket.io-cluster-adapter",
    "packages/socket.io-cluster-engine",
    "packages/socket.io-parser",
    "packages/socket.io-postgres-emitter",
    "packages/socket.io-redis-streams-emitter",
    # Standalone TypeScript example projects (LOCAL provenance)
    "examples/ReactNativeExample",
    "examples/angular-todomvc",
    "examples/basic-crud-application/angular-client",
    "examples/basic-crud-application/server",
    "examples/express-session-example/ts",
    "examples/nestjs-example",
    "examples/nuxt-example",
    "examples/passport-example/ts",
    "examples/passport-jwt-example/ts",
    "examples/typescript-client-example/cjs",
    "examples/typescript-client-example/esm",
    "examples/typescript-example/cjs",
    "examples/typescript-example/esm",
}
EXPECTED_SOCKETIO_PROJECT_NAMES: dict[str, str] = {
    "packages/engine.io": "engine.io",
    "packages/engine.io-client": "engine.io-client",
    "packages/engine.io-parser": "engine.io-parser",
    "packages/socket.io": "socket.io",
    "packages/socket.io-adapter": "socket.io-adapter",
    "packages/socket.io-client": "socket.io-client",
    "packages/socket.io-cluster-adapter": "@socket.io/cluster-adapter",
    "packages/socket.io-cluster-engine": "@socket.io/cluster-engine",
    "packages/socket.io-parser": "socket.io-parser",
    "packages/socket.io-postgres-emitter": "@socket.io/postgres-emitter",
    "packages/socket.io-redis-streams-emitter": "@socket.io/redis-streams-emitter",
    "examples/ReactNativeExample": "ReactNativeExample",
    "examples/angular-todomvc": "angular-todomvc",
    "examples/basic-crud-application/angular-client": "angular-client",
    "examples/basic-crud-application/server": "basic-crud-server",
    "examples/express-session-example/ts": "express-session-example",
    "examples/nestjs-example": "nestjs-example",
    "examples/nuxt-example": "nuxt-app",
    "examples/passport-example/ts": "passport-example",
    "examples/passport-jwt-example/ts": "passport-jwt-example",
    "examples/typescript-client-example/cjs": "typescript-client-example-cjs",
    "examples/typescript-client-example/esm": "typescript-client-example-esm",
    "examples/typescript-example/cjs": "typescript-example",
    "examples/typescript-example/esm": "typescript-example",
}
EXPECTED_SOCKETIO_PACKAGE_MANAGER: dict[str, PackageManagerType] = {
    folder: PackageManagerType.NPM for folder in EXPECTED_SOCKETIO_CODEBASE_FOLDERS
}
EXPECTED_SOCKETIO_PACKAGE_MANAGER.update(
    {
        "examples/ReactNativeExample": PackageManagerType.YARN,
    }
)
EXPECTED_SOCKETIO_PACKAGE_MANAGER_PROVENANCE: dict[
    str, PackageManagerProvenance
] = {
    folder: PackageManagerProvenance.INHERITED
    for folder in EXPECTED_SOCKETIO_CODEBASE_FOLDERS
}
EXPECTED_SOCKETIO_PACKAGE_MANAGER_PROVENANCE.update(
    {
        # Local override: has its own package-lock.json
        "packages/socket.io-cluster-adapter": PackageManagerProvenance.LOCAL,
        # All standalone examples have LOCAL provenance
        "examples/ReactNativeExample": PackageManagerProvenance.LOCAL,
        "examples/angular-todomvc": PackageManagerProvenance.LOCAL,
        "examples/basic-crud-application/angular-client": PackageManagerProvenance.LOCAL,
        "examples/basic-crud-application/server": PackageManagerProvenance.LOCAL,
        "examples/express-session-example/ts": PackageManagerProvenance.LOCAL,
        "examples/nestjs-example": PackageManagerProvenance.LOCAL,
        "examples/nuxt-example": PackageManagerProvenance.LOCAL,
        "examples/passport-example/ts": PackageManagerProvenance.LOCAL,
        "examples/passport-jwt-example/ts": PackageManagerProvenance.LOCAL,
        "examples/typescript-client-example/cjs": PackageManagerProvenance.LOCAL,
        "examples/typescript-client-example/esm": PackageManagerProvenance.LOCAL,
        "examples/typescript-example/cjs": PackageManagerProvenance.LOCAL,
        "examples/typescript-example/esm": PackageManagerProvenance.LOCAL,
    }
)
EXPECTED_SOCKETIO_WORKSPACE_ROOTS: dict[str, str | None] = {
    folder: "." for folder in EXPECTED_SOCKETIO_CODEBASE_FOLDERS
}
EXPECTED_SOCKETIO_WORKSPACE_ROOTS.update(
    {
        # Local override: detected as standalone
        "packages/socket.io-cluster-adapter": None,
        # All standalone examples have no workspace root
        "examples/ReactNativeExample": None,
        "examples/angular-todomvc": None,
        "examples/basic-crud-application/angular-client": None,
        "examples/basic-crud-application/server": None,
        "examples/express-session-example/ts": None,
        "examples/nestjs-example": None,
        "examples/nuxt-example": None,
        "examples/passport-example/ts": None,
        "examples/passport-jwt-example/ts": None,
        "examples/typescript-client-example/cjs": None,
        "examples/typescript-client-example/esm": None,
        "examples/typescript-example/cjs": None,
        "examples/typescript-example/esm": None,
    }
)

STANDALONE_FIXTURE_DIR = (
    Path(__file__).resolve().parents[3] / "test_data" / "standalone_ts_project"
)
PNPM_WORKSPACE_FIXTURE_DIR = (
    Path(__file__).resolve().parents[3] / "test_data" / "pnpm_workspace_test"
)


def format_detected_codebases(detected_codebases: list[CodebaseConfig]) -> list[str]:
    formatted_codebases: list[str] = []
    for codebase in detected_codebases:
        metadata = codebase.programming_language_metadata
        formatted_codebases.append(
            (
                f"{codebase.codebase_folder} | "
                f"package_manager={metadata.package_manager} | "
                f"package_manager_provenance={metadata.package_manager_provenance} | "
                f"workspace_root={metadata.workspace_root} | "
                f"workspace_orchestrator={metadata.workspace_orchestrator} | "
                f"workspace_orchestrator_config_path={metadata.workspace_orchestrator_config_path} | "
                f"manifest_path={metadata.manifest_path} | "
                f"project_name={metadata.project_name}"
            )
        )
    return sorted(formatted_codebases)


def map_codebases_by_folder(
    detected_codebases: list[CodebaseConfig],
) -> dict[str, CodebaseConfig]:
    return {codebase.codebase_folder: codebase for codebase in detected_codebases}


def write_package_json(file_path: Path, package_data: Mapping[str, object]) -> None:
    file_path.write_text(json.dumps(package_data))
