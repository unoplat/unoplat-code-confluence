# Changelog

## [0.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-cli-v0.4.1...unoplat-code-confluence-cli-v0.5.0) (2026-06-27)


### Features

* **cli:** add repository, refresh, setup status, and readiness gating ([8805058](https://github.com/unoplat/unoplat-code-confluence/commit/880505846fef925879a716b2822c4236b5d89a13))
* **cli:** rename entry point to ucc ([c63fc09](https://github.com/unoplat/unoplat-code-confluence/commit/c63fc098b30d98238a05135c6fd4ab655c4e9578))


### Bug Fixes

* **ci:** refresh package uv lockfiles before python lock checks run ([d133163](https://github.com/unoplat/unoplat-code-confluence/commit/d13316355530d39828be6fc99554431df306b4c4))
* **cli:** replace localhost with 127.0.0.1 in default service URLs ([6c16c89](https://github.com/unoplat/unoplat-code-confluence/commit/6c16c894b93c44c370806cca2e80f6b06eb21c7b))

## [0.4.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-cli-v0.4.0...unoplat-code-confluence-cli-v0.4.1) (2026-06-16)


### Bug Fixes

* **port-preservation:** preserve hostname:port in HTTPS git URL parsers ([4ff6aaa](https://github.com/unoplat/unoplat-code-confluence/commit/4ff6aaa756de5102bf13d961df44fb37f6a818c4))

## [0.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-cli-v0.3.0...unoplat-code-confluence-cli-v0.4.0) (2026-06-11)


### Features

* **cli-and-docs:** add setup commands and fix documentation and migr… ([8ff8006](https://github.com/unoplat/unoplat-code-confluence/commit/8ff8006d277050ef00f419d2a387092cb79f70df))
* **cli-and-docs:** add setup commands and fix documentation and migrate to vite+ ([f3c4feb](https://github.com/unoplat/unoplat-code-confluence/commit/f3c4febd3aee1d321053f245be58180f99b2c062))
* **cli:** group service related commands under service like run , destroy, stop, update ([d822b31](https://github.com/unoplat/unoplat-code-confluence/commit/d822b31f7b5d643df660a5d7b59985b251c54481))


### Bug Fixes

* **check-urls:** urls need to be added for probing flow bridge ([442b9b2](https://github.com/unoplat/unoplat-code-confluence/commit/442b9b21f82e326cb72fc982a3b3e33ab9c2d718))

## [0.3.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-cli-v0.2.0...unoplat-code-confluence-cli-v0.3.0) (2026-06-08)


### Features

* **add-setup-commands:** add setup commands ([946fb01](https://github.com/unoplat/unoplat-code-confluence/commit/946fb014c8ee2bde5ed0b61d34e2f39ceff11da4))
* **add-setup-commands:** add setup commands ([77f9bb6](https://github.com/unoplat/unoplat-code-confluence/commit/77f9bb61c2afa4d8a1cad9da80886f6208a8f16f))

## [0.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-cli-v0.1.0...unoplat-code-confluence-cli-v0.2.0) (2026-06-07)


### Features

* **cli:** add dev dependency group with ruff and pyrefly ([d4d4494](https://github.com/unoplat/unoplat-code-confluence/commit/d4d4494ae7eca2489ae53a1ec0edcb026a85305e))
* **cli:** migrate runtime models from dataclasses to pydantic ([52df2c9](https://github.com/unoplat/unoplat-code-confluence/commit/52df2c94dfe9021fa6043779bd67a8182de24cac))
* **cli:** use python-on-whales for compose runtime ([6641937](https://github.com/unoplat/unoplat-code-confluence/commit/6641937d045cbd0e828c71beb4b61329bb24de6d))
* scaffold initial unoplat-code-confluence-cli ([31647d2](https://github.com/unoplat/unoplat-code-confluence/commit/31647d277b97e705f1e87d035e477b467dc5bc9a))


### Bug Fixes

* **bad-code:** fix unnecessary docker compose check and also make the cli release step reliable ([478e504](https://github.com/unoplat/unoplat-code-confluence/commit/478e50401866cd5acc7361ffb78c47fa5770a282))
