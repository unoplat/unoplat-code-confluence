# Changelog

## [0.10.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.9.1...v0.10.0) (2024-07-22)


### Features

* improved comprehension at class, package and codebase level ([47b2e9b](https://github.com/unoplat/unoplat-code-confluence/commit/47b2e9b35784f0e0516238aacf0e3562c7b3583a))


### Bug Fixes

* better exception handling at function,class,package and codebase ([0edb975](https://github.com/unoplat/unoplat-code-confluence/commit/0edb975b191d29775d6ab7e55dfdda5e00ff23a7))

## [0.9.1](https://github.com/unoplat/unoplat-code-confluence/compare/v0.9.0...v0.9.1) (2024-07-16)


### Bug Fixes

* loguru config externalised. Fixed verbose info logging to debug ([7e2e881](https://github.com/unoplat/unoplat-code-confluence/commit/7e2e8811db2bd9714d71b40f689c2420719e212f))

## [0.9.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.8.0...v0.9.0) (2024-07-15)


### Features

* auditable examples ([21bcdd1](https://github.com/unoplat/unoplat-code-confluence/commit/21bcdd1d6547a538db0d1951405cdf7b64fe9501))

## [0.8.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.7.0...v0.8.0) (2024-07-15)


### Features

* drastically improved summarisation with chainofthoughtwithhints ([b328688](https://github.com/unoplat/unoplat-code-confluence/commit/b3286880a92a278e9091c97cdbd1ead6411f07d6))

## [0.7.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.6.0...v0.7.0) (2024-07-12)


### Features

* added examples for java and python. Python is in beta support ([5e2d100](https://github.com/unoplat/unoplat-code-confluence/commit/5e2d100ff27cf93f0168033f090822e8b6644a42))
* added support for cohere but it is not tested ([e67b11e](https://github.com/unoplat/unoplat-code-confluence/commit/e67b11eb9e226b0402ad7f4b300b7c26197dd6c6))
* improved reliability by moving towards typed chain of thought and typed predictors ([bd73c3c](https://github.com/unoplat/unoplat-code-confluence/commit/bd73c3c00a0d5910756322ece96611b6c3eb6542))


### Bug Fixes

* arcguard always download latest fix ([612c095](https://github.com/unoplat/unoplat-code-confluence/commit/612c0951acbeb168386c1d131198781ff938c262))
* arcguard latest download jar fix when already downloaded jar on user machine exists ([353092d](https://github.com/unoplat/unoplat-code-confluence/commit/353092d6bc430f52fa9d8691cf239d3e53b4d161))
* extension fix ([75a75e3](https://github.com/unoplat/unoplat-code-confluence/commit/75a75e37f39c624cf53a3d0fe0b84a9da443ed96))
* extension for different programming languages such as python ([37068fa](https://github.com/unoplat/unoplat-code-confluence/commit/37068fa9cd28889b74ac92ab0e91a2f7dd1ef20b))
* pydantic data model for python for supporting multiple inheritance in python ([72dff98](https://github.com/unoplat/unoplat-code-confluence/commit/72dff98f7cb2d81f31a97fc363a5484ccc126f36))
* support for python multiple inheritance ([6572ee9](https://github.com/unoplat/unoplat-code-confluence/commit/6572ee92f0570e730a1a295db961055e6ef3e88f))

## [0.6.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.5.0...v0.6.0) (2024-07-12)


### Features

* enable ollama cohere support and fix the naming convention for aws anthropic provider for anthropic models ([d341dbd](https://github.com/unoplat/unoplat-code-confluence/commit/d341dbd376b387ab55bd03aa01b5d520fd55e1d9))

## [0.5.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.4.0...v0.5.0) (2024-07-12)


### Features

* enhanced dspy pipeline for function summary reducing token usage and latency ([bd094c2](https://github.com/unoplat/unoplat-code-confluence/commit/bd094c25809bf31e8ee79f39dbfdf581d0fc3995))

## [0.4.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.3.0...v0.4.0) (2024-07-11)


### Features

* externalised llm provider config and enabled support for anthropic, anyscale, together and openai ([30aa226](https://github.com/unoplat/unoplat-code-confluence/commit/30aa22674fb1992f4d667f1438f1f3c9ee2137f0))

## [0.3.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.2.4...v0.3.0) (2024-07-10)


### Features

* add better logging at function,class,package level ([43c2189](https://github.com/unoplat/unoplat-code-confluence/commit/43c2189e77aa9122a5846428dea3be920de8d28d))


### Bug Fixes

* bug where huge classes used to fail as comprehension will not happen. improved function dspy pipeline. switched to experimental true for better performance of chat models. ([6b84f2e](https://github.com/unoplat/unoplat-code-confluence/commit/6b84f2e180a964fd9b9bc64c3e1bb13f09e3dfbb))

## [0.2.4](https://github.com/unoplat/unoplat-code-confluence/compare/v0.2.3...v0.2.4) (2024-07-08)


### Bug Fixes

* added markdown summary ([fbbc9f8](https://github.com/unoplat/unoplat-code-confluence/commit/fbbc9f8dfcc1f39bca44c5332ea283911e69a726))
* codebase objective first and summary second and removing unwanted files ([f8664a0](https://github.com/unoplat/unoplat-code-confluence/commit/f8664a01e66bfdf340d962ca87ee10d2f920311e))
* markdown formatting issues ([6cd1cf0](https://github.com/unoplat/unoplat-code-confluence/commit/6cd1cf0a49907b6fd3c60b3fdb077b68ab36fbcd))
* markdown summary ([2108771](https://github.com/unoplat/unoplat-code-confluence/commit/2108771ea011cf0ee661b8a3f324d44083f2cae5))

## [0.2.3](https://github.com/unoplat/unoplat-code-confluence/compare/v0.2.2...v0.2.3) (2024-07-04)


### Bug Fixes

* more structure changes ([3e0ea93](https://github.com/unoplat/unoplat-code-confluence/commit/3e0ea93ce05912c1f1bc26896769d61c223216f2))
* project structure and commented loguru config as of now ([2f7b50d](https://github.com/unoplat/unoplat-code-confluence/commit/2f7b50df6cb6d610ba843e6461815de63b21568a))
* structure ([9205550](https://github.com/unoplat/unoplat-code-confluence/commit/9205550ff374ff7a7f197a183eabef14391bf31e))
* structure ([1999343](https://github.com/unoplat/unoplat-code-confluence/commit/1999343dd7f1faf642727c18fde449944f1af26e))
* structure ([a6878ff](https://github.com/unoplat/unoplat-code-confluence/commit/a6878ff62e7dd292c9a4d9ddd800875b1d9134b7))
* structure and names ([d44709c](https://github.com/unoplat/unoplat-code-confluence/commit/d44709c75f10b171ea26f0e660c4eeeae93f2de9))

## [0.2.2](https://github.com/unoplat/unoplat-code-confluence/compare/v0.2.1...v0.2.2) (2024-07-04)


### Bug Fixes

* pipx installable structure and fix loading api tokens (right now only openai) from json ([f903b52](https://github.com/unoplat/unoplat-code-confluence/commit/f903b5201f38e17b5f6ecc7d6923b8460f13abd4))

## [0.2.1](https://github.com/unoplat/unoplat-code-confluence/compare/v0.2.0...v0.2.1) (2024-07-02)


### Bug Fixes

* added poetry tool script to work with pipx ([77a9d7f](https://github.com/unoplat/unoplat-code-confluence/commit/77a9d7f6fc99db55d3a029077c4663f761b8da7a))
* markdown headers ([c9b1ee4](https://github.com/unoplat/unoplat-code-confluence/commit/c9b1ee4c0b1e1db21b664b3675781becb2374861))
* python structure ([9f17650](https://github.com/unoplat/unoplat-code-confluence/commit/9f17650798689ef5d612cd7965713265ba43ce64))

## [0.2.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.1.0...v0.2.0) (2024-07-02)


### Features

* add doc ([7510bab](https://github.com/unoplat/unoplat-code-confluence/commit/7510bab0858890dcbe6091d610d820c010055b03))
* added dspy typed signature and predictor for function level summary ([6face17](https://github.com/unoplat/unoplat-code-confluence/commit/6face17b43f42e18c366305b48faf4d02d19f0c8))
* added output ([4accaf6](https://github.com/unoplat/unoplat-code-confluence/commit/4accaf6474329ab0814478e193c277a7424e4170))
* fix and enhance models for chapi and for dspy ([07658b2](https://github.com/unoplat/unoplat-code-confluence/commit/07658b2628c8ea905b6d32af467f709be05ae3cd))
* fixed iterating over codebases ([84f3aa7](https://github.com/unoplat/unoplat-code-confluence/commit/84f3aa7953f3a551fd49ca6c7dc39c2d0a7aadbc))
* updated documentation ([086d684](https://github.com/unoplat/unoplat-code-confluence/commit/086d6846bcddce9b5c757fae6ddb50274c28cf76))


### Bug Fixes

* added basic devsecops ([#30](https://github.com/unoplat/unoplat-code-confluence/issues/30)) ([ad243e0](https://github.com/unoplat/unoplat-code-confluence/commit/ad243e0eae84c9a88a4ac8fcee5ea65b139e8cfe))
* added new features ([874be58](https://github.com/unoplat/unoplat-code-confluence/commit/874be58091d125f1c5c4f364fabd788f124d8c69))
* content ([2875d8d](https://github.com/unoplat/unoplat-code-confluence/commit/2875d8db4a4be4d3bf41c1d3e67fda0dd4b3fda9))
* doc position ([6665e23](https://github.com/unoplat/unoplat-code-confluence/commit/6665e2334a1cb81e450e235f2f1b86a595c528f5))
* init with new models for packages ([d491585](https://github.com/unoplat/unoplat-code-confluence/commit/d4915859c29291c9f034152e13b591461417667e))
* merge issues ([27eb2fc](https://github.com/unoplat/unoplat-code-confluence/commit/27eb2fc28fb470f6fc089970c92736d9d100c460))
* models ([fbb1e7c](https://github.com/unoplat/unoplat-code-confluence/commit/fbb1e7cd745c034bf47c4c0ce1a06055dacceaed))
* repeatitive attributes in function ([1a65943](https://github.com/unoplat/unoplat-code-confluence/commit/1a65943a7383bc0d7cb2d0a04fb19e3c96738adc))
* structure according to poetry ([b3a74e8](https://github.com/unoplat/unoplat-code-confluence/commit/b3a74e862347e9fac82fa984e01439053e69f439))
