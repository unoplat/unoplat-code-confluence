# Changelog

## [1.34.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.34.0...unoplat-code-confluence-frontend-v1.34.1) (2025-11-22)


### Bug Fixes

* Extract axios clients to shared module and reduce staletime and fetchonMount for jobStatusDialog ([083ff01](https://github.com/unoplat/unoplat-code-confluence/commit/083ff01d8c4b1c848f7efca01ef5ea72ed2fb3c7))
* Extract axios clients to shared module and reduce staletime and fetchonMount for jobStatusDialog ([e9524b2](https://github.com/unoplat/unoplat-code-confluence/commit/e9524b2c78bb0e3e23acf71a48a73b4b416fb14d))

## [1.34.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.33.0...unoplat-code-confluence-frontend-v1.34.0) (2025-11-21)


### Features

* support more repository providers starting with github enterprise. Improved Frontend Architecture and onboarding and some bugs squashed ([0974c76](https://github.com/unoplat/unoplat-code-confluence/commit/0974c76fe9df68b86fb1b180db1b41e04a16c9dd))

## [1.33.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.32.0...unoplat-code-confluence-frontend-v1.33.0) (2025-11-21)


### Features

* **fixes:** fix ai slop by removing unnecessary useeffects usestate etc and update latest nuqs to integrate with tanstack router and also update table component for repository management  to dice ui for better abstraction and manageability ([a453cb5](https://github.com/unoplat/unoplat-code-confluence/commit/a453cb5f66609ae9cb599621d2289dbf601a63c6))
* **settings:** Refactor provider token management UI ([595c6dc](https://github.com/unoplat/unoplat-code-confluence/commit/595c6dca11a306e36a75b3a0ff6be8808ce02c3a))


### Bug Fixes

* **repository-table:** Refactor data fetching (useInfiniteQuery) and pagination logic for better reliability and performance ([19ebd60](https://github.com/unoplat/unoplat-code-confluence/commit/19ebd60a6e7640f78cd016e6122335e772f009d1))
* **ui:** Update component styles and imports to fix regression issues ([b0433b3](https://github.com/unoplat/unoplat-code-confluence/commit/b0433b3245525676c70b539594c5d0334e64978f))

## [1.32.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.31.0...unoplat-code-confluence-frontend-v1.32.0) (2025-11-18)


### Features

* **endpoint-updates:** Refactor repository configuration and credential types and api endpoints as per backend ([4278d2d](https://github.com/unoplat/unoplat-code-confluence/commit/4278d2de7b492b9bee82361daf60203d696b0701))
* **endpoint-updates:** Refactor repository configuration and credential types and api endpoints as per backend ([6469582](https://github.com/unoplat/unoplat-code-confluence/commit/6469582bd0be1f7ddee9d7c1143646653f6dbc7e))


### Bug Fixes

* **ui:** card and button component variants/properties ([7d32bcd](https://github.com/unoplat/unoplat-code-confluence/commit/7d32bcdacc2efeac963854e15410aebf80a2b571))

## [1.31.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.30.3...unoplat-code-confluence-frontend-v1.31.0) (2025-11-03)


### Features

* **agents:** Add usage statistics tracking and display ([97f7977](https://github.com/unoplat/unoplat-code-confluence/commit/97f797746d406712a272265f8ed00de92df1474e))
* **code:** allow sections of agents.md per codebase to be collapsed and copied ([859bbc7](https://github.com/unoplat/unoplat-code-confluence/commit/859bbc734789996aa1c1b8cabb88c4c5fd15ffa8))

## [1.30.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.30.2...unoplat-code-confluence-frontend-v1.30.3) (2025-10-30)


### Bug Fixes

* migrate to Bun for package management, vite v7 for build , dev server, upgraded to tailwind v4 and updated shadcn and custom components based on migration, upgraded typescript, moved shadcn custom registry to its own repository, streamline frontend architecture, removed manual codebase detection step, removed local github repository support, introduced eslint and prettier with non conflicting rules for linting and formatting for better agentic experience ([d409c41](https://github.com/unoplat/unoplat-code-confluence/commit/d409c416afad86ba4acb270c39fbb32105ed5f4f))

## [1.30.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.30.1...unoplat-code-confluence-frontend-v1.30.2) (2025-10-23)


### Bug Fixes

* **parser:** Refactor GenericCodebaseParser to focus on file insertion ([be17754](https://github.com/unoplat/unoplat-code-confluence/commit/be17754ab8a80b276820b205e37f0c9859e2b6b2))
* **parser:** Refactor parser to focus on file insertion ([c0bd597](https://github.com/unoplat/unoplat-code-confluence/commit/c0bd5974bbe8298b1a8e9a6931bf0eae850c1cca))

## [1.30.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.30.0...unoplat-code-confluence-frontend-v1.30.1) (2025-10-17)


### Bug Fixes

* **codebase-form:** Auto-update package manager on language change ([963cb31](https://github.com/unoplat/unoplat-code-confluence/commit/963cb31b817a0f85b51a72f030bbb8921a22b5c2))
* **codebase-form:** Dynamically render language package managers ([50d7102](https://github.com/unoplat/unoplat-code-confluence/commit/50d71027cfbc6bd00e6608cf3ab3e2b02f8611f2))
* **codebase-form:** Dynamically render language package managers ([8e4ddf7](https://github.com/unoplat/unoplat-code-confluence/commit/8e4ddf71bc5912de8a405b5d44186d257f44dd97))

## [1.30.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.29.3...unoplat-code-confluence-frontend-v1.30.0) (2025-10-04)


### Features

* **package-manager:** Add TypeScript package manager detection ([9cff38b](https://github.com/unoplat/unoplat-code-confluence/commit/9cff38bbf0349556a714402b3cfe7bc371c3a2fb))
* **package-manager:** Add TypeScript package manager detection ([ab4d9a5](https://github.com/unoplat/unoplat-code-confluence/commit/ab4d9a55dbdb05122631b24672df235736508a4d))

## [1.29.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.29.2...unoplat-code-confluence-frontend-v1.29.3) (2025-10-01)


### Bug Fixes

* **model-router:** do not allow agent md functionality without model provider setup and fix bug for model provider not invalidating tanstack query cache resulting in old data post update ([26d890e](https://github.com/unoplat/unoplat-code-confluence/commit/26d890edb3757a7f81b2427953e0511e77debfee))
* **model-router:** do not allow agent md functionality without model provider setup and fix bug for model provider not invalidating tanstack query cache resulting in old data post update ([ac595fd](https://github.com/unoplat/unoplat-code-confluence/commit/ac595fdac197cf5df57617078a6404b89ac9f60b))

## [1.29.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.29.1...unoplat-code-confluence-frontend-v1.29.2) (2025-09-30)


### Bug Fixes

* **vite-env:** pick env as per environment ([1c76fba](https://github.com/unoplat/unoplat-code-confluence/commit/1c76fbae99ff568e09a35a9315c9d93b8f380029))

## [1.29.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.29.0...unoplat-code-confluence-frontend-v1.29.1) (2025-09-29)


### Bug Fixes

* **AppSidebar:** Improve sidebar responsiveness ([2c0230b](https://github.com/unoplat/unoplat-code-confluence/commit/2c0230ba259e1c2c92da16553944478f71d41abc))
* **model-config:** add required validation to schema generator ([38ab5cb](https://github.com/unoplat/unoplat-code-confluence/commit/38ab5cbc3875ac95cc5b65bd6fbe47bab98fa35e))
* **model-config:** add required validation to schema generator ([cc2a400](https://github.com/unoplat/unoplat-code-confluence/commit/cc2a40094c1975fccbaba83a4c91d8e0c173ee61))
* **schema-generator:** add model field validation ([a821960](https://github.com/unoplat/unoplat-code-confluence/commit/a821960792591a90013068e4477aa9fd0694c16c))
* **schema-generator:** Implement schema generation ([2c0230b](https://github.com/unoplat/unoplat-code-confluence/commit/2c0230ba259e1c2c92da16553944478f71d41abc))
* **schema-generator:** Improve handling of required string fields ([21a5f18](https://github.com/unoplat/unoplat-code-confluence/commit/21a5f18208cb548b53615eed70830e2a981d0ec5))

## [1.29.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.28.0...unoplat-code-confluence-frontend-v1.29.0) (2025-09-29)


### Features

* **provider-schema:** enable multiple model providers configuration and minor ux changes ([b668b6e](https://github.com/unoplat/unoplat-code-confluence/commit/b668b6e1311f44e38f99408238ea0e6419da6f72))

## [1.28.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.27.0...unoplat-code-confluence-frontend-v1.28.0) (2025-09-26)


### Features

* **ui-optimistic-realtime-updates:** enable real time sync between frontend and backend ([b220132](https://github.com/unoplat/unoplat-code-confluence/commit/b220132e74a693febb56d99a199c54d3e9ca9d60))
* **ui-optimistic-realtime-updates:** enable real time sync between frontend and backend ([629e453](https://github.com/unoplat/unoplat-code-confluence/commit/629e453dd4e84bb118cc4ee67da45380c8479f34))

## [1.27.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.26.1...unoplat-code-confluence-frontend-v1.27.0) (2025-09-17)


### Features

* **agents:** add support for existing agent snapshot ([d0be956](https://github.com/unoplat/unoplat-code-confluence/commit/d0be956e9583c8a706d2a2d5604e11957c2b4df9))
* **agents:** add support for existing agent snapshot ([a6ccf7a](https://github.com/unoplat/unoplat-code-confluence/commit/a6ccf7aa1e00c88eaec71064e7431d1b6e2ae01f))

## [1.26.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.26.0...unoplat-code-confluence-frontend-v1.26.1) (2025-09-16)


### Bug Fixes

* **agent-tracking-generation:** fix agent progress tracking and display ([f54c713](https://github.com/unoplat/unoplat-code-confluence/commit/f54c713e8beb8a64d26b4adbdacc87c07f2dcb6a))
* **agent-tracking-generation:** fix agent progress tracking and display ([e6e7d7c](https://github.com/unoplat/unoplat-code-confluence/commit/e6e7d7cfe1f405210cd47539a395a5ffaf72c2a2))

## [1.26.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.25.1...unoplat-code-confluence-frontend-v1.26.0) (2025-09-15)


### Features

* **package:** add Agents.md first draft with help of @mdxeditor/editor and @radix-ui/react-progress, @radix-ui/react-scroll-area, @tailwindcss/typography and sse client handling ([47c1041](https://github.com/unoplat/unoplat-code-confluence/commit/47c1041a813fdef2efc0d929af7562e891119538))
* **package:** add Agents.md first draft with help of @mdxeditor/editor and @radix-ui/react-progress, @radix-ui/react-scroll-area, @tailwindcss/typography and sse client handling ([9890e54](https://github.com/unoplat/unoplat-code-confluence/commit/9890e54b1648b0353dd390a58c319deeac06dd7c))

## [1.25.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.25.0...unoplat-code-confluence-frontend-v1.25.1) (2025-08-09)


### Bug Fixes

* docker security posture update , regression fixes for delete/refresh endpoints, update volume mount directory to sync across macos/linux ([96981da](https://github.com/unoplat/unoplat-code-confluence/commit/96981da0ca1df987eecd1c773a2cee8640087192))
* docker security posture update , regression fixes for delete/refresh endpoints, update volume mount directory to sync across macos/linux ([d4ff81c](https://github.com/unoplat/unoplat-code-confluence/commit/d4ff81c7dd3dc9b43022617eafbf4e011da219d5))

## [1.25.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.24.3...unoplat-code-confluence-frontend-v1.25.0) (2025-07-02)


### Features

* **IngestedRepositoriesDataTable:** improve data fetching ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* local folder support ([ac56073](https://github.com/unoplat/unoplat-code-confluence/commit/ac56073502515c73208cc3e1122ab676aa0ed7e6))
* local git support ([5959c0d](https://github.com/unoplat/unoplat-code-confluence/commit/5959c0ddd0f177ad402e595a61c068b1506b4c05))
* **local-docker-compose.yml:** add repositories volume mount ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **SubmittedJobsDataTable:** improve data fetching ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **tanstack-table.d.ts:** add custom column and table meta ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))


### Bug Fixes

* **Taskfile.yml:** run pytest with test group ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))
* **test_start_ingestion.py:** handle local repository paths ([396e036](https://github.com/unoplat/unoplat-code-confluence/commit/396e036111fd8474cf9a35a017709f3e73840bec))

## [1.24.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.24.2...unoplat-code-confluence-frontend-v1.24.3) (2025-06-21)


### Bug Fixes

* refetch to 5s and fix ports ([e777453](https://github.com/unoplat/unoplat-code-confluence/commit/e777453e8d668fd7061b0abf3baa3a0ca8a4b14d))
* refetch to 5s and fix ports ([c47d43a](https://github.com/unoplat/unoplat-code-confluence/commit/c47d43a2ab9a58d091677b515ce78333e64bffb5))

## [1.24.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.24.1...unoplat-code-confluence-frontend-v1.24.2) (2025-06-21)


### Bug Fixes

* change the dotted path to full path for packages too ([b6277e0](https://github.com/unoplat/unoplat-code-confluence/commit/b6277e0b2a5247080feace1a6becc24225813a91))

## [1.24.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.24.0...unoplat-code-confluence-frontend-v1.24.1) (2025-06-20)


### Bug Fixes

* git pull explicit no rebase ([dfbbc26](https://github.com/unoplat/unoplat-code-confluence/commit/dfbbc26be5fc790127fb5b731568fa05f119bf9d))

## [1.24.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.23.1...unoplat-code-confluence-frontend-v1.24.0) (2025-06-18)


### Features

* add ui/ux for codebase auto detection ([55d5178](https://github.com/unoplat/unoplat-code-confluence/commit/55d5178dd172c97aed00607f45384e75f751ffb8))
* help in github token generation ([03393dc](https://github.com/unoplat/unoplat-code-confluence/commit/03393dcc3efcb11c5c25befa86585e2f9c332dce))
* refresh changes and bugs fix ([8e0230a](https://github.com/unoplat/unoplat-code-confluence/commit/8e0230acfc162ca9eec8f4495cab102224a68472))
* **revamp:** complete revamp to shift to tree sitter for core symbol extraction for queries and sse endpoint for auto codebase detection ([c3c6f89](https://github.com/unoplat/unoplat-code-confluence/commit/c3c6f89064c63ecca6e6314a70348b8780d1b6ee))
* **revamp:** complete revamp to shift to tree sitter for core symbol extraction for queries and sse endpoint for auto codebase detection ([5130bc7](https://github.com/unoplat/unoplat-code-confluence/commit/5130bc7a2f18f4dbbb10c30d5750b54149258e44))
* support repository operations including deletion ([f68e03d](https://github.com/unoplat/unoplat-code-confluence/commit/f68e03d14cbcd413062f4f45863fbf1af686153f))


### Bug Fixes

* removed unnecessary description ([4a8cf77](https://github.com/unoplat/unoplat-code-confluence/commit/4a8cf7747e81f1e5c58ca686c5d53feae6835091))
* squashed bugs ([7ac7d05](https://github.com/unoplat/unoplat-code-confluence/commit/7ac7d058ee8ee8b2170912e91f10a80376567d73))
* vite config (skipping auto code split) ([d970775](https://github.com/unoplat/unoplat-code-confluence/commit/d97077509d851e0000ccb39581d86843e0883e7e))

## [1.23.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.23.0...unoplat-code-confluence-frontend-v1.23.1) (2025-05-28)


### Bug Fixes

* remove unused React import from ModeToggle component ([acbabda](https://github.com/unoplat/unoplat-code-confluence/commit/acbabda735bbfab1ce7d91cafedf30e345a0d14f))
* remove unused React import from ModeToggle component ([b90c677](https://github.com/unoplat/unoplat-code-confluence/commit/b90c677a84f02ba9e73e2e3f57847a4ebda78d18))

## [1.23.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.22.0...unoplat-code-confluence-frontend-v1.23.0) (2025-05-28)


### Features

* **ui:** UI overhaul with new design system and support dark/lig ([4b344f5](https://github.com/unoplat/unoplat-code-confluence/commit/4b344f5c85f94f6b062ea0dfd21e66ebcc38a056))
* **ui:** UI overhaul with new design system and support dark/lig ([0bbb67a](https://github.com/unoplat/unoplat-code-confluence/commit/0bbb67ae62472e66c9c9484ac93bad0717123fcc))

## [1.22.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.21.1...unoplat-code-confluence-frontend-v1.22.0) (2025-05-28)


### Features

* **registry:** add self hostable registry ([fbc2fae](https://github.com/unoplat/unoplat-code-confluence/commit/fbc2fae59760fed9f89112d1a499470fe031b686))
* **registry:** add self hostable registry ([2b45d62](https://github.com/unoplat/unoplat-code-confluence/commit/2b45d6206b44e4c368e960a364dcb6242e0af063))

## [1.21.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.21.0...unoplat-code-confluence-frontend-v1.21.1) (2025-05-27)


### Bug Fixes

* change default package_manager to auto-detect ([bfb393b](https://github.com/unoplat/unoplat-code-confluence/commit/bfb393bef674493eab2d5ed292c9f301e09ef0cd))

## [1.21.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.20.0...unoplat-code-confluence-frontend-v1.21.0) (2025-05-26)


### Features

* **package-manager:** add automatic package manager detection ([0aa88bd](https://github.com/unoplat/unoplat-code-confluence/commit/0aa88bd65d46c1a3df35c6bf02d769c2a5548585))
* **package-manager:** add automatic package manager detection ([470b352](https://github.com/unoplat/unoplat-code-confluence/commit/470b3528206208a730f63b537ca252220991e0b7))

## [1.20.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.19.3...unoplat-code-confluence-frontend-v1.20.0) (2025-05-17)


### Features

* **issue-tracking:** add GitHub issue creation endpoint ([eaa7147](https://github.com/unoplat/unoplat-code-confluence/commit/eaa71471008c90fbe14f91a62704c4719d506cb3))
* **job-status-table:** add job status data table columns component ([42ae4a1](https://github.com/unoplat/unoplat-code-confluence/commit/42ae4a18522cfafeaf3f84f0a2553b6868ad9230))
* refactor GitHub repo models and add child workflow DB activity ([ee07cb3](https://github.com/unoplat/unoplat-code-confluence/commit/ee07cb3c72e8a36d96d46f888c231ea85fb1777d))


### Bug Fixes

* **db:** enhance error context and improve UI button styles ([d4d8003](https://github.com/unoplat/unoplat-code-confluence/commit/d4d8003636766df29005ca897e43e4c374a1a17b))

## [1.19.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.19.2...unoplat-code-confluence-frontend-v1.19.3) (2025-04-25)


### Bug Fixes

* **env:** update default knowledgeGraphUrl port to 7474 ([968ebd0](https://github.com/unoplat/unoplat-code-confluence/commit/968ebd00cd8de6b8fe9a7f67c4504354103799b3))
* **env:** update default knowledgeGraphUrl port to 7474 ([9e2337a](https://github.com/unoplat/unoplat-code-confluence/commit/9e2337a653861461bf43b59d7b355704e8bdb43a))

## [1.19.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.19.1...unoplat-code-confluence-frontend-v1.19.2) (2025-04-24)


### Bug Fixes

* **env:** update default API URLs to localhost ([d165f18](https://github.com/unoplat/unoplat-code-confluence/commit/d165f18d2f826770938ffadbebe4a1fff39040be))
* **env:** update default API URLs to localhost ([ff8c8df](https://github.com/unoplat/unoplat-code-confluence/commit/ff8c8df149ed4de4d97809ef50e51b130607e307))

## [1.19.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.19.0...unoplat-code-confluence-frontend-v1.19.1) (2025-04-24)


### Bug Fixes

* **env:** update default backend service URLs ([510165d](https://github.com/unoplat/unoplat-code-confluence/commit/510165df15d7155764764cc67a421ba3f7e66604))
* **env:** update default backend service URLs ([421d79e](https://github.com/unoplat/unoplat-code-confluence/commit/421d79e640270a840e829a6162106acecb4f90de))

## [1.19.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.18.1...unoplat-code-confluence-frontend-v1.19.0) (2025-04-23)


### Features

* **codebaseform:** lock root repo checkbox when folder is "." ([2e30bfa](https://github.com/unoplat/unoplat-code-confluence/commit/2e30bfa39201cb1c70961ac1cd375920e6ab3852))
* **codebaseform:** lock root repo checkbox when folder is "." ([f205f0f](https://github.com/unoplat/unoplat-code-confluence/commit/f205f0f2bbf064665bb7b520edf8517e5294c7e3))

## [1.18.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.18.0...unoplat-code-confluence-frontend-v1.18.1) (2025-04-23)


### Bug Fixes

* **app:** remove GitHubTokenPopup and update tooltip dependency ([cb3cc86](https://github.com/unoplat/unoplat-code-confluence/commit/cb3cc86654b1a455a70f438d35facc671c3ca01e))
* **app:** remove GitHubTokenPopup and update tooltip dependency ([6d843a5](https://github.com/unoplat/unoplat-code-confluence/commit/6d843a50df39f03cb119e4e68615a58981b945de))

## [1.18.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.17.0...unoplat-code-confluence-frontend-v1.18.0) (2025-04-22)


### Features

* **codebaseform:** add root repository checkbox for codebase folder ([6f3e7b4](https://github.com/unoplat/unoplat-code-confluence/commit/6f3e7b45b7770b31dea23a8c83b38ad4e2bc2363))
* **codebaseform:** add root repository checkbox for codebase folder ([a84d733](https://github.com/unoplat/unoplat-code-confluence/commit/a84d7336688b55c82d3aeed6f5d4675494598b84))

## [1.17.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.16.1...unoplat-code-confluence-frontend-v1.17.0) (2025-04-22)


### Features

* **ui:** improve and update dependencies ([8591e0c](https://github.com/unoplat/unoplat-code-confluence/commit/8591e0c1acc6f0d714d00e2b3aa21b2fa90f04f5))
* **ui:** improve and update dependencies ([c3c5b64](https://github.com/unoplat/unoplat-code-confluence/commit/c3c5b64ff3ecf3ebb3f14b48867f6a7a077c9263))

## [1.16.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.16.0...unoplat-code-confluence-frontend-v1.16.1) (2025-04-22)


### Bug Fixes

* **app:** skip global token popup on onboarding page ([994e9a5](https://github.com/unoplat/unoplat-code-confluence/commit/994e9a53838a69577c068b4623688769785ce4fd))
* **app:** skip global token popup on onboarding page ([77cca60](https://github.com/unoplat/unoplat-code-confluence/commit/77cca60792a18f592b36f4a811b5ac50e4c29edc))

## [1.16.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.15.0...unoplat-code-confluence-frontend-v1.16.0) (2025-04-21)


### Features

* **developer:** add developer mode route and state management ([69432db](https://github.com/unoplat/unoplat-code-confluence/commit/69432db2bdf528153dd084d6557341195838499a))
* **sidebar:** add Unoplat Connect collapsible group with social links ([ba24b58](https://github.com/unoplat/unoplat-code-confluence/commit/ba24b580802f3f077449c9855534bc5bde953a56))
* **sidebar:** add Unoplat Connect collapsible group with social links ([70749d6](https://github.com/unoplat/unoplat-code-confluence/commit/70749d6a74795188fdafaf359a94370b59c503ce))

## [1.15.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.14.0...unoplat-code-confluence-frontend-v1.15.0) (2025-04-21)


### Features

* **sidebar:** add collapsible groups for workspace and settings ([2e4232d](https://github.com/unoplat/unoplat-code-confluence/commit/2e4232dea3c200182e5caf5cec3aefb97869cf8d))
* **sidebar:** add collapsible groups for workspace and settings ([9f18826](https://github.com/unoplat/unoplat-code-confluence/commit/9f18826085a9baef3c7ea88147ba3d61dac203f2))

## [1.14.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.13.0...unoplat-code-confluence-frontend-v1.14.0) (2025-04-21)


### Features

* **settings:** use mutation isPending state for delete token UI ([2272f28](https://github.com/unoplat/unoplat-code-confluence/commit/2272f28ac1a486dc43ef07fbd43b1387a35bc5d2))
* **settings:** use mutation isPending state for delete token UI ([3f50dcb](https://github.com/unoplat/unoplat-code-confluence/commit/3f50dcbbe3eed2898aba0061e75205bd8001e5bf))

## [1.13.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.12.0...unoplat-code-confluence-frontend-v1.13.0) (2025-04-21)


### Features

* **codebase:** add removable codebase forms when creating config ([0d0f4d9](https://github.com/unoplat/unoplat-code-confluence/commit/0d0f4d95bf114f5470fa5b2b2a01aac046648e4d))
* **codebase:** add removable codebase forms when creating config ([bd4d7f2](https://github.com/unoplat/unoplat-code-confluence/commit/bd4d7f20e18c6197df967f31e1b66e78ae39e612))

## [1.12.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.11.0...unoplat-code-confluence-frontend-v1.12.0) (2025-04-21)


### Features

* **settings:** sidebar perfection ([c4bc34b](https://github.com/unoplat/unoplat-code-confluence/commit/c4bc34b6cce9dae065364e213960c57c612bbb68))


### Bug Fixes

* github token close properly ([dab6b78](https://github.com/unoplat/unoplat-code-confluence/commit/dab6b78368e522f05b7a6de6db346b85b5c098b1))
* github token close properly ([cd8fc79](https://github.com/unoplat/unoplat-code-confluence/commit/cd8fc7990ca06f878597dc716d245cf3592fe427))

## [1.11.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.10.1...unoplat-code-confluence-frontend-v1.11.0) (2025-04-17)


### Features

* **api:** add repository config CRUD endpoints and types ([886a90c](https://github.com/unoplat/unoplat-code-confluence/commit/886a90c77424f0ed49d86493ce833afcdbffd190))
* **api:** add repository config CRUD endpoints and types ([c412180](https://github.com/unoplat/unoplat-code-confluence/commit/c412180a357b7ac8645fe2e50017e99120761ac3))

## [1.10.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.10.0...unoplat-code-confluence-frontend-v1.10.1) (2025-04-13)


### Bug Fixes

* fixed multiple titles in github token popup and improved overall design ([dd3d475](https://github.com/unoplat/unoplat-code-confluence/commit/dd3d47575f1d7364adfa948abf433a0685d4de14))
* fixed multiple titles in github token popup and improved overall design ([8469fc6](https://github.com/unoplat/unoplat-code-confluence/commit/8469fc6ed6a2fd2c4978c4dd33a40e87b594cf02))

## [1.10.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.9.0...unoplat-code-confluence-frontend-v1.10.0) (2025-04-13)


### Features

* enable boundary detection and automatically prefetch next page ([74a5062](https://github.com/unoplat/unoplat-code-confluence/commit/74a50628955877a87046cd97a40715b01173db3f))
* focus on search automatically ([b51592e](https://github.com/unoplat/unoplat-code-confluence/commit/b51592e61fdad1957b2e7b9cf26469b561f60e01))

## [1.9.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.8.3...unoplat-code-confluence-frontend-v1.9.0) (2025-04-10)


### Features

* update repository filtering and pagination logic ([36dc786](https://github.com/unoplat/unoplat-code-confluence/commit/36dc78666d4074dc36f319674515a43670e8c3ea))
* update repository filtering and pagination logic ([d14e59f](https://github.com/unoplat/unoplat-code-confluence/commit/d14e59fd465cf849d6c491a1fd854ddb4d403b65))

## [1.8.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.8.2...unoplat-code-confluence-frontend-v1.8.3) (2025-04-09)


### Bug Fixes

* regression fixes and toast notifications ([19efdfc](https://github.com/unoplat/unoplat-code-confluence/commit/19efdfc1e147ce0e5cdc90115e63daeb4f7f5db9))
* regression fixes and toast notifications ([2c07b9f](https://github.com/unoplat/unoplat-code-confluence/commit/2c07b9f180c5b89a190e1c73c1488a4a83923a85))
* remove unused import ([07e37ba](https://github.com/unoplat/unoplat-code-confluence/commit/07e37bac4f4be75150e6d6fda5e68e62d8e272c6))

## [1.8.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.8.1...unoplat-code-confluence-frontend-v1.8.2) (2025-04-09)


### Bug Fixes

* github token popup ([2c3c99d](https://github.com/unoplat/unoplat-code-confluence/commit/2c3c99da6f1c6e8f47f62fdf65b3ecfff23c5885))
* github token popup ([ea8d353](https://github.com/unoplat/unoplat-code-confluence/commit/ea8d353b1e549b4b0fc64608d99d469ffa8d66c8))

## [1.8.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.8.0...unoplat-code-confluence-frontend-v1.8.1) (2025-04-09)


### Bug Fixes

* fix docker file and remove unused file ([932980c](https://github.com/unoplat/unoplat-code-confluence/commit/932980c3760bb3529fa878bca46979042df90a95))
* fix docker file and remove unused file ([1d0fa8f](https://github.com/unoplat/unoplat-code-confluence/commit/1d0fa8fee0cdf13b75e26fe0e8779e897e113fb6))

## [1.8.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.7.0...unoplat-code-confluence-frontend-v1.8.0) (2025-04-08)


### Features

* migrate to dice ui data table + router  + query ([c961b7a](https://github.com/unoplat/unoplat-code-confluence/commit/c961b7a49d8a7f0448d76efc36764cc8fbcdd8d2))
* migrate to dice ui data table + router  + query ([9eae225](https://github.com/unoplat/unoplat-code-confluence/commit/9eae2255881913201cad76cdb598fc84b3cf27b6))

## [1.7.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.6.1...unoplat-code-confluence-frontend-v1.7.0) (2025-04-07)


### Features

* update Radix UI components and add data table options ([c69b324](https://github.com/unoplat/unoplat-code-confluence/commit/c69b324df0766d1dfe6bb25d087dc66d3446e713))
* update Radix UI components and add data table options ([a6853b2](https://github.com/unoplat/unoplat-code-confluence/commit/a6853b2ee15fa0cf8123b91e59461896120f731e))

## [1.6.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.6.0...unoplat-code-confluence-frontend-v1.6.1) (2025-04-02)


### Bug Fixes

* backend state managemnt to share state cross-device/sessions ([b43cfe9](https://github.com/unoplat/unoplat-code-confluence/commit/b43cfe9815f0d20212c771381b613c61c7614704))
* backend state managemnt to share state cross-device/sessions ([9cef39c](https://github.com/unoplat/unoplat-code-confluence/commit/9cef39c0728671df3261d0edab27be54f7dc3330))

## [1.6.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.5.0...unoplat-code-confluence-frontend-v1.6.0) (2025-04-02)


### Features

* enhanced app name typography and improved icons for sidebar navigation ([0c73525](https://github.com/unoplat/unoplat-code-confluence/commit/0c7352504814ffb3948b382a0159388f3c90fb8b))

## [1.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.4.0...unoplat-code-confluence-frontend-v1.5.0) (2025-04-01)


### Features

* search focus post loading repos ([db4a929](https://github.com/unoplat/unoplat-code-confluence/commit/db4a929016551429a31b7781749978fb4c795c47))
* search focus post loading repos ([d2904f7](https://github.com/unoplat/unoplat-code-confluence/commit/d2904f77a3eb3f9f85b1fa0868945d67506653e8))

## [1.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.3.0...unoplat-code-confluence-frontend-v1.4.0) (2025-04-01)


### Features

* added delete token option and changes to github token auth ([2520757](https://github.com/unoplat/unoplat-code-confluence/commit/252075781258da63eb698e990dfe8e38fc6ff27c))
* added delete token option and changes to github token auth ([821dea3](https://github.com/unoplat/unoplat-code-confluence/commit/821dea3a8a74217d30dd7b732c5fad1a65bc3539))


### Bug Fixes

* add a flag to false when user deletes the token ([3c6ee18](https://github.com/unoplat/unoplat-code-confluence/commit/3c6ee18725094bb7d3e9cbc1719f4961a6a6a43e))

## [1.3.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.2.0...unoplat-code-confluence-frontend-v1.3.0) (2025-04-01)


### Features

* enhance onboarding page and repository table ([af2767b](https://github.com/unoplat/unoplat-code-confluence/commit/af2767b5418571c74082e2529501188048cf2e21))
* enhance onboarding page and repository table ([9e9e5b8](https://github.com/unoplat/unoplat-code-confluence/commit/9e9e5b85d40e0bca91cc121f8f3eed8722bcb23f))

## [1.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.1.0...unoplat-code-confluence-frontend-v1.2.0) (2025-04-01)


### Features

* add Tailwind CSS and PostCSS support ([45eabb2](https://github.com/unoplat/unoplat-code-confluence/commit/45eabb2f1381e2965ccf59ff5ae690bcd0c38d03))
* added git token acceptance and onboarding/settings screens ([9401425](https://github.com/unoplat/unoplat-code-confluence/commit/9401425ba0795805a6d634ee11a855008c08c2e8))
* added git token acceptance and onboarding/settings screens ([114802d](https://github.com/unoplat/unoplat-code-confluence/commit/114802d8659171d9a192e2429409aa325b831be2))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([db51f81](https://github.com/unoplat/unoplat-code-confluence/commit/db51f81269dd1a842782597dec274e6b80ecb683))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([0fc7618](https://github.com/unoplat/unoplat-code-confluence/commit/0fc761826125c9ae5aa0c8a47cbd09ef4125129c))
* update dependencies and add nested function detection ([17ceb7c](https://github.com/unoplat/unoplat-code-confluence/commit/17ceb7c0b176caf71da66b5ce0b0e45ef7e6a63e))
* update dependencies and add nested function detection ([f5adfe2](https://github.com/unoplat/unoplat-code-confluence/commit/f5adfe2eff9efafc92dfd72d97025e52392d6777))


### Bug Fixes

* improved error messages ([f91b32f](https://github.com/unoplat/unoplat-code-confluence/commit/f91b32f22b0963777236769490363b3a644ffa1c))
* improved error messages ([31f26e0](https://github.com/unoplat/unoplat-code-confluence/commit/31f26e0704955d34f5bfb934791e40f8230f0e4d))

## [1.1.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-frontend-v1.0.0...unoplat-code-confluence-frontend-v1.1.0) (2025-03-31)


### Features

* added git token acceptance and onboarding/settings screens ([9401425](https://github.com/unoplat/unoplat-code-confluence/commit/9401425ba0795805a6d634ee11a855008c08c2e8))
* added git token acceptance and onboarding/settings screens ([114802d](https://github.com/unoplat/unoplat-code-confluence/commit/114802d8659171d9a192e2429409aa325b831be2))

## 1.0.0 (2025-03-31)


### Features

* add Tailwind CSS and PostCSS support ([45eabb2](https://github.com/unoplat/unoplat-code-confluence/commit/45eabb2f1381e2965ccf59ff5ae690bcd0c38d03))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([db51f81](https://github.com/unoplat/unoplat-code-confluence/commit/db51f81269dd1a842782597dec274e6b80ecb683))
* **docker:** add PostgreSQL and Elasticsearch and Frontend related services ([0fc7618](https://github.com/unoplat/unoplat-code-confluence/commit/0fc761826125c9ae5aa0c8a47cbd09ef4125129c))
* update dependencies and add nested function detection ([17ceb7c](https://github.com/unoplat/unoplat-code-confluence/commit/17ceb7c0b176caf71da66b5ce0b0e45ef7e6a63e))
* update dependencies and add nested function detection ([f5adfe2](https://github.com/unoplat/unoplat-code-confluence/commit/f5adfe2eff9efafc92dfd72d97025e52392d6777))
