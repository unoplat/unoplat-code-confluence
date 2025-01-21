# Changelog

## [0.10.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.9.2...unoplat-code-confluence-commons-v0.10.0) (2025-01-21)


### Features

* added comments based description to improve summarisation and query ([513c38f](https://github.com/unoplat/unoplat-code-confluence/commit/513c38fa0884b3f1a4226d82d35e39a1dc4b7932))
* added common lib for ingestion and query utility ([f5058fb](https://github.com/unoplat/unoplat-code-confluence/commit/f5058fbcdd03f634567e8bb196ff20e0cd36d368))
* added extensible rich schema for neomodel ([2a8427e](https://github.com/unoplat/unoplat-code-confluence/commit/2a8427e7eb5dc349398d1de9edf4d7e4702841b0))
* added qualified names to repository and codebase for uniqueness ([b2272e7](https://github.com/unoplat/unoplat-code-confluence/commit/b2272e7e07cae25404ad329a9416bd1e3d313792))
* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* added vector indexes and moved vector properties to sub classes to maintain distinction ([899f103](https://github.com/unoplat/unoplat-code-confluence/commit/899f103d9c0e44bf29a7f2aca05c0a0e268f4a84))
* enhanced data models from python ([6288f3d](https://github.com/unoplat/unoplat-code-confluence/commit/6288f3d1b0ca68f8ee38f685102b8e22fd366aad))
* made models completely async and added async pytest with testcontainers ([2432a37](https://github.com/unoplat/unoplat-code-confluence/commit/2432a37e09f367e9adc4948fb10c1150746aa303))
* moved to async nodes and relationships ([1c207c4](https://github.com/unoplat/unoplat-code-confluence/commit/1c207c4e48ba6f8ba3e831c881255f93f7c0638f))
* neomodel schema updated with newer ingestion schema ([2964ca2](https://github.com/unoplat/unoplat-code-confluence/commit/2964ca2b6b6808473fc2e4873c1c15ba809708ff))


### Bug Fixes

* add float type to array property to hold vector indexes properly ([27d6d1b](https://github.com/unoplat/unoplat-code-confluence/commit/27d6d1b5d9af9926060c2769505b447542ac114d))
* added poetry related files ([60a32dd](https://github.com/unoplat/unoplat-code-confluence/commit/60a32dd45b03a41c1e1fc633a1472f92437ef67e))
* added README for poetry ([8f215ba](https://github.com/unoplat/unoplat-code-confluence/commit/8f215babc07e3e4049935635a108e350809f65cd))
* circular imports in models ([2b046d7](https://github.com/unoplat/unoplat-code-confluence/commit/2b046d7ad8e6cf7bf82577aff1d3a16516f76963))
* enable bidirectional cardinality ([4415bb0](https://github.com/unoplat/unoplat-code-confluence/commit/4415bb0ba60fd7eced738b217e2d6c565f646d92))
* fix schema not handling local path of codebase node in neo4j ([9d5e7d2](https://github.com/unoplat/unoplat-code-confluence/commit/9d5e7d2bd6cd2d24505ec2cc6e0febd58875191a))
* import issues ([5be2854](https://github.com/unoplat/unoplat-code-confluence/commit/5be285468aac53f049e7376db90a604ba5ba2ac1))
* increase version of pytest asyncio to be compatible with parent project ingestion ([af7deef](https://github.com/unoplat/unoplat-code-confluence/commit/af7deef64a7e13cdff5a9106cbe18c364118a4d7))
* poetry install ([e793acb](https://github.com/unoplat/unoplat-code-confluence/commit/e793acb17871b3a02674e2b4c0db29bec678ab5e))
* poetry lock file ([0117d54](https://github.com/unoplat/unoplat-code-confluence/commit/0117d54e54c45bee6ad7cd89d04b59b73943c164))
* relationship direction ([fc08aff](https://github.com/unoplat/unoplat-code-confluence/commit/fc08aff5610de56741f0b295d5a94c8465f3993e))
* relationships from and to codebase, packages, classes and method with right cardinality ([739c190](https://github.com/unoplat/unoplat-code-confluence/commit/739c190bafc6947306b65f41030ddab8de4c1098))
* removed default as required is true ([c835a3d](https://github.com/unoplat/unoplat-code-confluence/commit/c835a3d1af4fb230f4c02c96d970b11241e4d8b6))
* removed vector indexes and renamed properly to ensure right dimensions at the time of creation ([393331a](https://github.com/unoplat/unoplat-code-confluence/commit/393331a1f9f0ea73caed93d2663f2768bec081b5))
* simplifying the names ([ea47cb6](https://github.com/unoplat/unoplat-code-confluence/commit/ea47cb6b548e338d78ee9607eb533d850b20b5ee))
* test for release of commons post huly release ([c7224df](https://github.com/unoplat/unoplat-code-confluence/commit/c7224df1faf7f6bc28bc6c459d4a1ddfe577620a))
* test github release please action ([b3cc20e](https://github.com/unoplat/unoplat-code-confluence/commit/b3cc20ef1526b177e88f4ecdebb9229cf8d7126b))
* test google release please action ([aec06a7](https://github.com/unoplat/unoplat-code-confluence/commit/aec06a79262e2528181e718352d6edc36a74a002))
* test release please action ([d47656f](https://github.com/unoplat/unoplat-code-confluence/commit/d47656fdf10e30b01de9c4daab08f394092af79a))

## [0.9.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.9.1...unoplat-code-confluence-commons-v0.9.2) (2025-01-20)


### Bug Fixes

* fix schema not handling local path of codebase node in neo4j ([9d5e7d2](https://github.com/unoplat/unoplat-code-confluence/commit/9d5e7d2bd6cd2d24505ec2cc6e0febd58875191a))

## [0.9.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.9.0...unoplat-code-confluence-commons-v0.9.1) (2025-01-08)


### Bug Fixes

* increase version of pytest asyncio to be compatible with parent project ingestion ([af7deef](https://github.com/unoplat/unoplat-code-confluence/commit/af7deef64a7e13cdff5a9106cbe18c364118a4d7))
* poetry install ([e793acb](https://github.com/unoplat/unoplat-code-confluence/commit/e793acb17871b3a02674e2b4c0db29bec678ab5e))

## [0.9.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.8.1...unoplat-code-confluence-commons-v0.9.0) (2025-01-07)


### Features

* added comments based description to improve summarisation and query ([513c38f](https://github.com/unoplat/unoplat-code-confluence/commit/513c38fa0884b3f1a4226d82d35e39a1dc4b7932))
* added common lib for ingestion and query utility ([f5058fb](https://github.com/unoplat/unoplat-code-confluence/commit/f5058fbcdd03f634567e8bb196ff20e0cd36d368))
* added extensible rich schema for neomodel ([2a8427e](https://github.com/unoplat/unoplat-code-confluence/commit/2a8427e7eb5dc349398d1de9edf4d7e4702841b0))
* added qualified names to repository and codebase for uniqueness ([b2272e7](https://github.com/unoplat/unoplat-code-confluence/commit/b2272e7e07cae25404ad329a9416bd1e3d313792))
* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* added vector indexes and moved vector properties to sub classes to maintain distinction ([899f103](https://github.com/unoplat/unoplat-code-confluence/commit/899f103d9c0e44bf29a7f2aca05c0a0e268f4a84))
* enhanced data models from python ([6288f3d](https://github.com/unoplat/unoplat-code-confluence/commit/6288f3d1b0ca68f8ee38f685102b8e22fd366aad))
* made models completely async and added async pytest with testcontainers ([2432a37](https://github.com/unoplat/unoplat-code-confluence/commit/2432a37e09f367e9adc4948fb10c1150746aa303))
* moved to async nodes and relationships ([1c207c4](https://github.com/unoplat/unoplat-code-confluence/commit/1c207c4e48ba6f8ba3e831c881255f93f7c0638f))
* neomodel schema updated with newer ingestion schema ([2964ca2](https://github.com/unoplat/unoplat-code-confluence/commit/2964ca2b6b6808473fc2e4873c1c15ba809708ff))


### Bug Fixes

* add float type to array property to hold vector indexes properly ([27d6d1b](https://github.com/unoplat/unoplat-code-confluence/commit/27d6d1b5d9af9926060c2769505b447542ac114d))
* added poetry related files ([60a32dd](https://github.com/unoplat/unoplat-code-confluence/commit/60a32dd45b03a41c1e1fc633a1472f92437ef67e))
* added README for poetry ([8f215ba](https://github.com/unoplat/unoplat-code-confluence/commit/8f215babc07e3e4049935635a108e350809f65cd))
* circular imports in models ([2b046d7](https://github.com/unoplat/unoplat-code-confluence/commit/2b046d7ad8e6cf7bf82577aff1d3a16516f76963))
* enable bidirectional cardinality ([4415bb0](https://github.com/unoplat/unoplat-code-confluence/commit/4415bb0ba60fd7eced738b217e2d6c565f646d92))
* import issues ([5be2854](https://github.com/unoplat/unoplat-code-confluence/commit/5be285468aac53f049e7376db90a604ba5ba2ac1))
* poetry lock file ([0117d54](https://github.com/unoplat/unoplat-code-confluence/commit/0117d54e54c45bee6ad7cd89d04b59b73943c164))
* relationship direction ([fc08aff](https://github.com/unoplat/unoplat-code-confluence/commit/fc08aff5610de56741f0b295d5a94c8465f3993e))
* relationships from and to codebase, packages, classes and method with right cardinality ([739c190](https://github.com/unoplat/unoplat-code-confluence/commit/739c190bafc6947306b65f41030ddab8de4c1098))
* removed default as required is true ([c835a3d](https://github.com/unoplat/unoplat-code-confluence/commit/c835a3d1af4fb230f4c02c96d970b11241e4d8b6))
* removed vector indexes and renamed properly to ensure right dimensions at the time of creation ([393331a](https://github.com/unoplat/unoplat-code-confluence/commit/393331a1f9f0ea73caed93d2663f2768bec081b5))
* simplifying the names ([ea47cb6](https://github.com/unoplat/unoplat-code-confluence/commit/ea47cb6b548e338d78ee9607eb533d850b20b5ee))
* test for release of commons post huly release ([c7224df](https://github.com/unoplat/unoplat-code-confluence/commit/c7224df1faf7f6bc28bc6c459d4a1ddfe577620a))
* test github release please action ([b3cc20e](https://github.com/unoplat/unoplat-code-confluence/commit/b3cc20ef1526b177e88f4ecdebb9229cf8d7126b))
* test google release please action ([aec06a7](https://github.com/unoplat/unoplat-code-confluence/commit/aec06a79262e2528181e718352d6edc36a74a002))
* test release please action ([d47656f](https://github.com/unoplat/unoplat-code-confluence/commit/d47656fdf10e30b01de9c4daab08f394092af79a))

## [0.8.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.8.0...unoplat-code-confluence-commons-v0.8.1) (2025-01-07)


### Bug Fixes

* test for release of commons post huly release ([c7224df](https://github.com/unoplat/unoplat-code-confluence/commit/c7224df1faf7f6bc28bc6c459d4a1ddfe577620a))
* test github release please action ([b3cc20e](https://github.com/unoplat/unoplat-code-confluence/commit/b3cc20ef1526b177e88f4ecdebb9229cf8d7126b))
* test google release please action ([aec06a7](https://github.com/unoplat/unoplat-code-confluence/commit/aec06a79262e2528181e718352d6edc36a74a002))

## [0.8.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.7.0...unoplat-code-confluence-commons-v0.8.0) (2025-01-04)


### Features

* made models completely async and added async pytest with testcontainers ([2432a37](https://github.com/unoplat/unoplat-code-confluence/commit/2432a37e09f367e9adc4948fb10c1150746aa303))

## [0.7.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.6.2...unoplat-code-confluence-commons-v0.7.0) (2025-01-04)


### Features

* moved to async nodes and relationships ([1c207c4](https://github.com/unoplat/unoplat-code-confluence/commit/1c207c4e48ba6f8ba3e831c881255f93f7c0638f))

## [0.6.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.6.1...unoplat-code-confluence-commons-v0.6.2) (2025-01-04)


### Bug Fixes

* import issues ([5be2854](https://github.com/unoplat/unoplat-code-confluence/commit/5be285468aac53f049e7376db90a604ba5ba2ac1))

## [0.6.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.6.0...unoplat-code-confluence-commons-v0.6.1) (2025-01-03)


### Bug Fixes

* relationship direction ([fc08aff](https://github.com/unoplat/unoplat-code-confluence/commit/fc08aff5610de56741f0b295d5a94c8465f3993e))

## [0.6.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.5.0...unoplat-code-confluence-commons-v0.6.0) (2025-01-03)


### Features

* added qualified names to repository and codebase for uniqueness ([b2272e7](https://github.com/unoplat/unoplat-code-confluence/commit/b2272e7e07cae25404ad329a9416bd1e3d313792))

## [0.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.4.0...unoplat-code-confluence-commons-v0.5.0) (2025-01-03)


### Features

* added relationships for annotation ([3c97e15](https://github.com/unoplat/unoplat-code-confluence/commit/3c97e1521134022c6dbcfcba7ae8293621eae378))
* neomodel schema updated with newer ingestion schema ([2964ca2](https://github.com/unoplat/unoplat-code-confluence/commit/2964ca2b6b6808473fc2e4873c1c15ba809708ff))

## [0.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.3.0...unoplat-code-confluence-commons-v0.4.0) (2024-12-20)


### Features

* added comments based description to improve summarisation and query ([513c38f](https://github.com/unoplat/unoplat-code-confluence/commit/513c38fa0884b3f1a4226d82d35e39a1dc4b7932))
* added extensible rich schema for neomodel ([2a8427e](https://github.com/unoplat/unoplat-code-confluence/commit/2a8427e7eb5dc349398d1de9edf4d7e4702841b0))

## [0.3.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.7...unoplat-code-confluence-commons-v0.3.0) (2024-11-04)


### Features

* enhanced data models from python ([6288f3d](https://github.com/unoplat/unoplat-code-confluence/commit/6288f3d1b0ca68f8ee38f685102b8e22fd366aad))

## [0.2.7](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.6...unoplat-code-confluence-commons-v0.2.7) (2024-10-25)


### Bug Fixes

* simplifying the names ([ea47cb6](https://github.com/unoplat/unoplat-code-confluence/commit/ea47cb6b548e338d78ee9607eb533d850b20b5ee))

## [0.2.6](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.5...unoplat-code-confluence-commons-v0.2.6) (2024-10-25)


### Bug Fixes

* relationships from and to codebase, packages, classes and method with right cardinality ([739c190](https://github.com/unoplat/unoplat-code-confluence/commit/739c190bafc6947306b65f41030ddab8de4c1098))

## [0.2.5](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.4...unoplat-code-confluence-commons-v0.2.5) (2024-10-25)


### Bug Fixes

* enable bidirectional cardinality ([4415bb0](https://github.com/unoplat/unoplat-code-confluence/commit/4415bb0ba60fd7eced738b217e2d6c565f646d92))

## [0.2.4](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.3...unoplat-code-confluence-commons-v0.2.4) (2024-10-25)


### Bug Fixes

* circular imports in models ([2b046d7](https://github.com/unoplat/unoplat-code-confluence/commit/2b046d7ad8e6cf7bf82577aff1d3a16516f76963))

## [0.2.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.2...unoplat-code-confluence-commons-v0.2.3) (2024-10-25)


### Bug Fixes

* removed default as required is true ([c835a3d](https://github.com/unoplat/unoplat-code-confluence/commit/c835a3d1af4fb230f4c02c96d970b11241e4d8b6))

## [0.2.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.1...unoplat-code-confluence-commons-v0.2.2) (2024-10-24)


### Bug Fixes

* removed vector indexes and renamed properly to ensure right dimensions at the time of creation ([393331a](https://github.com/unoplat/unoplat-code-confluence/commit/393331a1f9f0ea73caed93d2663f2768bec081b5))

## [0.2.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.2.0...unoplat-code-confluence-commons-v0.2.1) (2024-10-24)


### Bug Fixes

* add float type to array property to hold vector indexes properly ([27d6d1b](https://github.com/unoplat/unoplat-code-confluence/commit/27d6d1b5d9af9926060c2769505b447542ac114d))

## [0.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-commons-v0.1.0...unoplat-code-confluence-commons-v0.2.0) (2024-10-23)


### Features

* added vector indexes and moved vector properties to sub classes to maintain distinction ([899f103](https://github.com/unoplat/unoplat-code-confluence/commit/899f103d9c0e44bf29a7f2aca05c0a0e268f4a84))


### Bug Fixes

* added poetry related files ([60a32dd](https://github.com/unoplat/unoplat-code-confluence/commit/60a32dd45b03a41c1e1fc633a1472f92437ef67e))
* added README for poetry ([8f215ba](https://github.com/unoplat/unoplat-code-confluence/commit/8f215babc07e3e4049935635a108e350809f65cd))
* poetry lock file ([0117d54](https://github.com/unoplat/unoplat-code-confluence/commit/0117d54e54c45bee6ad7cd89d04b59b73943c164))

## 0.1.0 (2024-10-23)


### Features

* added common lib for ingestion and query utility ([f5058fb](https://github.com/unoplat/unoplat-code-confluence/commit/f5058fbcdd03f634567e8bb196ff20e0cd36d368))
