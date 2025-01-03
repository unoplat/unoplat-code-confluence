# Changelog

## [0.17.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.16.0...unoplat-code-confluence-v0.17.0) (2024-12-21)


### Features

* made config as per current progress ([9a315d1](https://github.com/unoplat/unoplat-code-confluence/commit/9a315d11ece4c361d1b489d8442d66f8b177b124))


### Bug Fixes

* changed the name of output path to not tie it with extension of file ([35e6675](https://github.com/unoplat/unoplat-code-confluence/commit/35e667580736bcdc7f4c0d7132972599a4ec7e90))

## [0.16.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.15.0...unoplat-code-confluence-v0.16.0) (2024-12-20)


### Features

* add example config and enhance type checking. included robust class variables and function local variables handling ([d1d2afb](https://github.com/unoplat/unoplat-code-confluence/commit/d1d2afb68573a599d65b4358a0cbfe0be9dcb000))
* add function call cleaning method and new tests for sorting function dependencies- Introduced a new method `__clean_function_call` in `FunctionMetadataParser` to extract just the function name from call strings.- Updated the test for local variables to reflect the change in function call value assertion.- Added new tests for sorting function dependencies, covering various scenarios including simple chains, no dependencies, and cyclic dependencies.- Created an empty `__init__.py` file in the `in_class_dependency` directory to establish the package structure. ([1a174bc](https://github.com/unoplat/unoplat-code-confluence/commit/1a174bc0deff5e7f730b905aff1464f773ac5a7f))
* added ability to read package manager based on programming language for enhanced context starting with python ([f9a6cd2](https://github.com/unoplat/unoplat-code-confluence/commit/f9a6cd24f366fe3907d00ee9597a009479cd6d16))
* added ability to read versions if not able to figure out from proper poetry or pip package management ([5ccbea3](https://github.com/unoplat/unoplat-code-confluence/commit/5ccbea3b3806dadd869b56801ee342cf5d29851b))
* added ability to segregate imports and improved context based on github repo to many codebases. Also improved unoplat inhouse struct for handling imports of programming languages like python that can have multiple ways of imports being defined. ([d691bd6](https://github.com/unoplat/unoplat-code-confluence/commit/d691bd6ea5ac200205a48926d40aa664cd866a32))
* added comments for class and function ([97fd429](https://github.com/unoplat/unoplat-code-confluence/commit/97fd429126ccbd72783fe1525e8d698b8cd6cd28))
* added parameters as part of function chapi metadata which was missing and added default value if parameter has been assigned default value ([4cf6294](https://github.com/unoplat/unoplat-code-confluence/commit/4cf6294307935a76ad249fddd238e6625de4ef44))
* added parsing and consolidating imports through ast and filling in unique imports in chapi struct as chapi is ambiguos right now ([03bd901](https://github.com/unoplat/unoplat-code-confluence/commit/03bd901154754fd83430f3ba859b7f00eb351868))
* added reference to package manager metadata from source codebase data model ([cc246fd](https://github.com/unoplat/unoplat-code-confluence/commit/cc246fd8937f24846eac4a5b0ecf0a96848cc1e2))
* added requirement_utils ([8991012](https://github.com/unoplat/unoplat-code-confluence/commit/89910122c06430cb8cf766954e28813adb91252d))
* added stdlist module to figure out system modules of python ([d4c5671](https://github.com/unoplat/unoplat-code-confluence/commit/d4c56719706f13a0bbb25f52a15b8ac2092c6159))
* added support for pip ([5c9a5f2](https://github.com/unoplat/unoplat-code-confluence/commit/5c9a5f222ba488b87a80484a477c4ce81cc7d312))
* Added support for qualified names of packages ([6018817](https://github.com/unoplat/unoplat-code-confluence/commit/6018817151eff03305a3f16ba75641a70fd0e4c3))
* added support for repo name and repo url as metadata ([f6577a7](https://github.com/unoplat/unoplat-code-confluence/commit/f6577a7cedf970e1737daf51ef251126d5be61ed))
* added support for system import reading ([177f9ff](https://github.com/unoplat/unoplat-code-confluence/commit/177f9fff763f1fe912bea8b86e85bf6055fb729e))
* enabled qualified name while parsing classes and better structure for custom language things ([8f6faeb](https://github.com/unoplat/unoplat-code-confluence/commit/8f6faeba5850484dc9c0007a297a8c683c330a94))
* enhance Python parsing with tree-sitter, new metadata parsers, dependency sorting, refactoring, and robust unit tests ([bd9bec6](https://github.com/unoplat/unoplat-code-confluence/commit/bd9bec6ec4d854a8dd9bcc6efa08de391ab3390e))
* introduce new data models and refactor existing ones for enhanced codebase management and import handling- Added new data models under `chapi_forge` for better organization and handling of codebases, repositories, and package metadata.- Refactored existing models to improve clarity and maintainability, including renaming and restructuring imports.- Introduced unit tests for `GithubHelper` to ensure proper functionality when cloning repositories.- Created an empty `__init__.py` file to establish the `confluence_git` package.- Updated main application logic to utilize the new data models and improve overall code structure. ([4440955](https://github.com/unoplat/unoplat-code-confluence/commit/444095510b15ddb9df06eb20a04d76a101b897a7))
* moved to requirements-parser lib for parsing requirements file making the implementation more robust ([efe5c54](https://github.com/unoplat/unoplat-code-confluence/commit/efe5c549412674015b4a8c3c77a850fc19e4ae0f))
* revamped entire code to do programming language related custom processing with ease and implemented external dependency parsing ([501ff7c](https://github.com/unoplat/unoplat-code-confluence/commit/501ff7c443946d0883578b5e1c04ded97a8b9347))
* segregated secrets and normal json config through base model and base settings of pydantic and a class to handle them both ([c23c9f1](https://github.com/unoplat/unoplat-code-confluence/commit/c23c9f1468a498fa3dab81bc126d8ac2b146ddee))
* update dependencies and enhance code structureAdded black (v23.12.1) and pathspec (v0.12.1) for formatting and path matching.Updated pyproject.toml and ruff.toml with enhanced configurations.Added debug_tree_sitter_content.py for AST analysis.Refactored data models for clarity (e.g., renamed fields in chapi_class_global_fieldmodel and chapi_function_field_model).Improved NodeVariablesParser logic and added class name utility.Updated tests for new features and robustness. ([b24403a](https://github.com/unoplat/unoplat-code-confluence/commit/b24403a57b3385aabb2e31b9cfb2e84295fb57a0))
* update linting rules, refactor tests, add class name validator, and enhance dependency error handling ([1f4e370](https://github.com/unoplat/unoplat-code-confluence/commit/1f4e3704c85300cec213a83daada67af49eb0dbe))
* upgraded arcguard to 2.2.3 ([1b865c4](https://github.com/unoplat/unoplat-code-confluence/commit/1b865c40cfae895ebdd0cb298b54b52c252a8124))
* upgraded upstream archguard to 2.2.7 which fixes parameters of functions and function calls ([d6f2b3c](https://github.com/unoplat/unoplat-code-confluence/commit/d6f2b3c4109a93fe6da156073ba1acf5439fae41))


### Bug Fixes

* handle different types of setup scripts in setup.py ([dd30032](https://github.com/unoplat/unoplat-code-confluence/commit/dd30032ce059668673af686f61db15fee05ab921))
* handle multi path for codebases inside monorepo ([b2a754a](https://github.com/unoplat/unoplat-code-confluence/commit/b2a754a64521f761280a2ec2c81339194693d3f2))
* only pass root package for parsing ([19b1345](https://github.com/unoplat/unoplat-code-confluence/commit/19b1345065582c9ea3669737f3dbf7bed752a80b))
* pass content of file to parse global variables ([9eee27c](https://github.com/unoplat/unoplat-code-confluence/commit/9eee27c10345f4cae99196c7b64ad4a0171fb59d))
* read/parse poetry better ([49cd0a8](https://github.com/unoplat/unoplat-code-confluence/commit/49cd0a88f1f88970892a4592209904f4609e055f))
* removed redundant field ([749d054](https://github.com/unoplat/unoplat-code-confluence/commit/749d05472db51ea497cde9048209cfa60f8b2cf3))
* support falling back to explicit python version from user if not mentioned in setup.py(pip) or poetry config ([7613f5a](https://github.com/unoplat/unoplat-code-confluence/commit/7613f5a55ebb9cd360cddc78a503e62f23a91873))

## [0.15.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.14.0...unoplat-code-confluence-v0.15.0) (2024-11-04)


### Features

* added more context and right exclusions for pipelines ([add3c28](https://github.com/unoplat/unoplat-code-confluence/commit/add3c28afecb9b6a395075f195290f2dddb18b52))
* enabled litellm support for dspy ([c96a059](https://github.com/unoplat/unoplat-code-confluence/commit/c96a059059c5d4745320d2bb02351b73594a85d3))
* enhanced data models from python ([6288f3d](https://github.com/unoplat/unoplat-code-confluence/commit/6288f3d1b0ca68f8ee38f685102b8e22fd366aad))
* enhanced dspy pipelines by introducing json schema before sharing json ([34d69d8](https://github.com/unoplat/unoplat-code-confluence/commit/34d69d81bc9219436bb73a39ba7ffb5f84414483))
* enhanced function summary by introducing json schema ([c0e4944](https://github.com/unoplat/unoplat-code-confluence/commit/c0e4944aaf9f291610338d4d45dade945b7229b2))

## [0.14.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.13.4...unoplat-code-confluence-v0.14.0) (2024-10-29)


### Features

* enabled neomodel in ingestion. Enabled dimensions of vector index based on embedding model selected from hugging face ([218d863](https://github.com/unoplat/unoplat-code-confluence/commit/218d8633875ddfc27063c7f4117e76a1236068cf))
* moved from native cypher to neomodel and it feels at home ([1abc7f4](https://github.com/unoplat/unoplat-code-confluence/commit/1abc7f44a6d73c99a665522f6f5d1fbeb615d88e))

## [0.13.4](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.13.3...unoplat-code-confluence-v0.13.4) (2024-10-08)


### Bug Fixes

* merge conflicts ([868649e](https://github.com/unoplat/unoplat-code-confluence/commit/868649ea8f825b15af6923c72bf2be1f96704fce))

## [0.13.3](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.13.2...unoplat-code-confluence-v0.13.3) (2024-10-07)


### Bug Fixes

* fix max lines when response is received ([a3145b7](https://github.com/unoplat/unoplat-code-confluence/commit/a3145b7df88ed5c95afe2c20061007e1ef331f62))

## [0.13.2](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.13.1...unoplat-code-confluence-v0.13.2) (2024-10-07)


### Bug Fixes

* added poetry lock for reproducible environments ([a3f0a2b](https://github.com/unoplat/unoplat-code-confluence/commit/a3f0a2b6f6eb863b701485857e5a52f8ebdbbfcc))
* added rich for beatutiful formatting in terminal ([3986c5a](https://github.com/unoplat/unoplat-code-confluence/commit/3986c5a7afe2b57cc0f11347621f99f3ca013088))

## [0.13.1](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.13.0...unoplat-code-confluence-v0.13.1) (2024-10-07)


### Bug Fixes

* bug fix for poetry script ([56ba319](https://github.com/unoplat/unoplat-code-confluence/commit/56ba319b8c714db7b4867538c0ea26052d4e23c3))

## [0.13.0](https://github.com/unoplat/unoplat-code-confluence/compare/unoplat-code-confluence-v0.12.0...unoplat-code-confluence-v0.13.0) (2024-10-04)


### Features

* add better logging at function,class,package level ([43c2189](https://github.com/unoplat/unoplat-code-confluence/commit/43c2189e77aa9122a5846428dea3be920de8d28d))
* add doc ([7510bab](https://github.com/unoplat/unoplat-code-confluence/commit/7510bab0858890dcbe6091d610d820c010055b03))
* added dspy typed signature and predictor for function level summary ([6face17](https://github.com/unoplat/unoplat-code-confluence/commit/6face17b43f42e18c366305b48faf4d02d19f0c8))
* added examples for java and python. Python is in beta support ([5e2d100](https://github.com/unoplat/unoplat-code-confluence/commit/5e2d100ff27cf93f0168033f090822e8b6644a42))
* added output ([4accaf6](https://github.com/unoplat/unoplat-code-confluence/commit/4accaf6474329ab0814478e193c277a7424e4170))
* added support for cohere but it is not tested ([e67b11e](https://github.com/unoplat/unoplat-code-confluence/commit/e67b11eb9e226b0402ad7f4b300b7c26197dd6c6))
* auditable examples ([21bcdd1](https://github.com/unoplat/unoplat-code-confluence/commit/21bcdd1d6547a538db0d1951405cdf7b64fe9501))
* drastically improved summarisation with chainofthoughtwithhints ([b328688](https://github.com/unoplat/unoplat-code-confluence/commit/b3286880a92a278e9091c97cdbd1ead6411f07d6))
* enable ollama cohere support and fix the naming convention for aws anthropic provider for anthropic models ([d341dbd](https://github.com/unoplat/unoplat-code-confluence/commit/d341dbd376b387ab55bd03aa01b5d520fd55e1d9))
* enabled textual based chat ([f765b30](https://github.com/unoplat/unoplat-code-confluence/commit/f765b303353effdd2427b30e0c91a31d5de69831))
* enhanced dspy pipeline for function summary reducing token usage and latency ([bd094c2](https://github.com/unoplat/unoplat-code-confluence/commit/bd094c25809bf31e8ee79f39dbfdf581d0fc3995))
* externalised llm provider config and enabled support for anthropic, anyscale, together and openai ([30aa226](https://github.com/unoplat/unoplat-code-confluence/commit/30aa22674fb1992f4d667f1438f1f3c9ee2137f0))
* fix and enhance models for chapi and for dspy ([07658b2](https://github.com/unoplat/unoplat-code-confluence/commit/07658b2628c8ea905b6d32af467f709be05ae3cd))
* fixed iterating over codebases ([84f3aa7](https://github.com/unoplat/unoplat-code-confluence/commit/84f3aa7953f3a551fd49ca6c7dc39c2d0a7aadbc))
* improved comprehension at class, package and codebase level ([47b2e9b](https://github.com/unoplat/unoplat-code-confluence/commit/47b2e9b35784f0e0516238aacf0e3562c7b3583a))
* improved reliability by moving towards typed chain of thought and typed predictors ([bd73c3c](https://github.com/unoplat/unoplat-code-confluence/commit/bd73c3c00a0d5910756322ece96611b6c3eb6542))
* perf improvement through parallelisation of classes ([9be18e4](https://github.com/unoplat/unoplat-code-confluence/commit/9be18e407468f48e8cc03c59e417f63020a9c377))
* support ingestion into neo4j with vector embeddings ([07bd949](https://github.com/unoplat/unoplat-code-confluence/commit/07bd949c3834903000ccc52f4148714b231345cc))
* updated documentation ([086d684](https://github.com/unoplat/unoplat-code-confluence/commit/086d6846bcddce9b5c757fae6ddb50274c28cf76))


### Bug Fixes

* added basic devsecops ([#30](https://github.com/unoplat/unoplat-code-confluence/issues/30)) ([ad243e0](https://github.com/unoplat/unoplat-code-confluence/commit/ad243e0eae84c9a88a4ac8fcee5ea65b139e8cfe))
* added markdown summary ([fbbc9f8](https://github.com/unoplat/unoplat-code-confluence/commit/fbbc9f8dfcc1f39bca44c5332ea283911e69a726))
* added nested progress bars, support for efficient graph traversal and support for files that are not object oriented ([a0f9f8d](https://github.com/unoplat/unoplat-code-confluence/commit/a0f9f8d7830ec71942a06e95ea465c29a828da21))
* added new features ([874be58](https://github.com/unoplat/unoplat-code-confluence/commit/874be58091d125f1c5c4f364fabd788f124d8c69))
* added poetry tool script to work with pipx ([77a9d7f](https://github.com/unoplat/unoplat-code-confluence/commit/77a9d7f6fc99db55d3a029077c4663f761b8da7a))
* arcguard always download latest fix ([612c095](https://github.com/unoplat/unoplat-code-confluence/commit/612c0951acbeb168386c1d131198781ff938c262))
* arcguard latest download jar fix when already downloaded jar on user machine exists ([353092d](https://github.com/unoplat/unoplat-code-confluence/commit/353092d6bc430f52fa9d8691cf239d3e53b4d161))
* better exception handling at function,class,package and codebase ([0edb975](https://github.com/unoplat/unoplat-code-confluence/commit/0edb975b191d29775d6ab7e55dfdda5e00ff23a7))
* bug where huge classes used to fail as comprehension will not happen. improved function dspy pipeline. switched to experimental true for better performance of chat models. ([6b84f2e](https://github.com/unoplat/unoplat-code-confluence/commit/6b84f2e180a964fd9b9bc64c3e1bb13f09e3dfbb))
* bugs during ingestion of codebase-&gt;package->class ([a18c3b6](https://github.com/unoplat/unoplat-code-confluence/commit/a18c3b678a33d3b11f6cae41f290e845e77f6ec1))
* codebase objective first and summary second and removing unwanted files ([f8664a0](https://github.com/unoplat/unoplat-code-confluence/commit/f8664a01e66bfdf340d962ca87ee10d2f920311e))
* content ([2875d8d](https://github.com/unoplat/unoplat-code-confluence/commit/2875d8db4a4be4d3bf41c1d3e67fda0dd4b3fda9))
* doc position ([6665e23](https://github.com/unoplat/unoplat-code-confluence/commit/6665e2334a1cb81e450e235f2f1b86a595c528f5))
* dummy doc to test cicd ([0717554](https://github.com/unoplat/unoplat-code-confluence/commit/07175546eb0e09578e80d7f2c591de6188f0031d))
* extension fix ([75a75e3](https://github.com/unoplat/unoplat-code-confluence/commit/75a75e37f39c624cf53a3d0fe0b84a9da443ed96))
* extension for different programming languages such as python ([37068fa](https://github.com/unoplat/unoplat-code-confluence/commit/37068fa9cd28889b74ac92ab0e91a2f7dd1ef20b))
* externalised json output as bool to represent unoplat pydantic schema in json ([602667f](https://github.com/unoplat/unoplat-code-confluence/commit/602667f8b0a4b725039e6ff48e2f775e1beb9570))
* graph data structure for construction of codebase ([99cbe3c](https://github.com/unoplat/unoplat-code-confluence/commit/99cbe3c27978bd7db6385e37beed27948ea920a7))
* init with new models for packages ([d491585](https://github.com/unoplat/unoplat-code-confluence/commit/d4915859c29291c9f034152e13b591461417667e))
* loguru config externalised. Fixed verbose info logging to debug ([7e2e881](https://github.com/unoplat/unoplat-code-confluence/commit/7e2e8811db2bd9714d71b40f689c2420719e212f))
* markdown formatting issues ([6cd1cf0](https://github.com/unoplat/unoplat-code-confluence/commit/6cd1cf0a49907b6fd3c60b3fdb077b68ab36fbcd))
* markdown headers ([c9b1ee4](https://github.com/unoplat/unoplat-code-confluence/commit/c9b1ee4c0b1e1db21b664b3675781becb2374861))
* markdown summary ([2108771](https://github.com/unoplat/unoplat-code-confluence/commit/2108771ea011cf0ee661b8a3f324d44083f2cae5))
* merge issues ([27eb2fc](https://github.com/unoplat/unoplat-code-confluence/commit/27eb2fc28fb470f6fc089970c92736d9d100c460))
* models ([fbb1e7c](https://github.com/unoplat/unoplat-code-confluence/commit/fbb1e7cd745c034bf47c4c0ce1a06055dacceaed))
* more structure changes ([3e0ea93](https://github.com/unoplat/unoplat-code-confluence/commit/3e0ea93ce05912c1f1bc26896769d61c223216f2))
* pipx installable structure and fix loading api tokens (right now only openai) from json ([f903b52](https://github.com/unoplat/unoplat-code-confluence/commit/f903b5201f38e17b5f6ecc7d6923b8460f13abd4))
* project structure and commented loguru config as of now ([2f7b50d](https://github.com/unoplat/unoplat-code-confluence/commit/2f7b50df6cb6d610ba843e6461815de63b21568a))
* pydantic data model for python for supporting multiple inheritance in python ([72dff98](https://github.com/unoplat/unoplat-code-confluence/commit/72dff98f7cb2d81f31a97fc363a5484ccc126f36))
* python structure ([9f17650](https://github.com/unoplat/unoplat-code-confluence/commit/9f17650798689ef5d612cd7965713265ba43ce64))
* repeatitive attributes in function ([1a65943](https://github.com/unoplat/unoplat-code-confluence/commit/1a65943a7383bc0d7cb2d0a04fb19e3c96738adc))
* structure ([9205550](https://github.com/unoplat/unoplat-code-confluence/commit/9205550ff374ff7a7f197a183eabef14391bf31e))
* structure ([1999343](https://github.com/unoplat/unoplat-code-confluence/commit/1999343dd7f1faf642727c18fde449944f1af26e))
* structure ([a6878ff](https://github.com/unoplat/unoplat-code-confluence/commit/a6878ff62e7dd292c9a4d9ddd800875b1d9134b7))
* structure according to poetry ([b3a74e8](https://github.com/unoplat/unoplat-code-confluence/commit/b3a74e862347e9fac82fa984e01439053e69f439))
* structure and names ([d44709c](https://github.com/unoplat/unoplat-code-confluence/commit/d44709c75f10b171ea26f0e660c4eeeae93f2de9))
* support for python multiple inheritance ([6572ee9](https://github.com/unoplat/unoplat-code-confluence/commit/6572ee92f0570e730a1a295db961055e6ef3e88f))

## [0.12.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.11.1...v0.12.0) (2024-10-04)


### Features

* enabled textual based chat ([f765b30](https://github.com/unoplat/unoplat-code-confluence/commit/f765b303353effdd2427b30e0c91a31d5de69831))
* support ingestion into neo4j with vector embeddings ([07bd949](https://github.com/unoplat/unoplat-code-confluence/commit/07bd949c3834903000ccc52f4148714b231345cc))


### Bug Fixes

* bugs during ingestion of codebase-&gt;package->class ([a18c3b6](https://github.com/unoplat/unoplat-code-confluence/commit/a18c3b678a33d3b11f6cae41f290e845e77f6ec1))

## [0.11.1](https://github.com/unoplat/unoplat-code-confluence/compare/v0.11.0...v0.11.1) (2024-09-07)


### Bug Fixes

* externalised json output as bool to represent unoplat pydantic schema in json ([602667f](https://github.com/unoplat/unoplat-code-confluence/commit/602667f8b0a4b725039e6ff48e2f775e1beb9570))

## [0.11.0](https://github.com/unoplat/unoplat-code-confluence/compare/v0.10.1...v0.11.0) (2024-09-07)


### Features

* perf improvement through parallelisation of classes ([9be18e4](https://github.com/unoplat/unoplat-code-confluence/commit/9be18e407468f48e8cc03c59e417f63020a9c377))

## [0.10.1](https://github.com/unoplat/unoplat-code-confluence/compare/v0.10.0...v0.10.1) (2024-07-28)


### Bug Fixes

* added nested progress bars, support for efficient graph traversal and support for files that are not object oriented ([a0f9f8d](https://github.com/unoplat/unoplat-code-confluence/commit/a0f9f8d7830ec71942a06e95ea465c29a828da21))
* graph data structure for construction of codebase ([99cbe3c](https://github.com/unoplat/unoplat-code-confluence/commit/99cbe3c27978bd7db6385e37beed27948ea920a7))

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
