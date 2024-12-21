"use strict";(self.webpackChunkcode_confluence=self.webpackChunkcode_confluence||[]).push([[270],{4555:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>a,contentTitle:()=>s,default:()=>u,frontMatter:()=>t,metadata:()=>l,toc:()=>c});var o=i(4848),r=i(8453);const t={sidebar_position:2},s="Quick Start Guide",l={id:"quickstart/how-to-run",title:"Quick Start Guide",description:"Welcome to Unoplat Code Confluence",source:"@site/docs/quickstart/how-to-run.md",sourceDirName:"quickstart",slug:"/quickstart/how-to-run",permalink:"/unoplat-code-confluence/docs/quickstart/how-to-run",draft:!1,unlisted:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/quickstart/how-to-run.md",tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"tutorialSidebar",previous:{title:"Quickstart",permalink:"/unoplat-code-confluence/docs/category/quickstart"},next:{title:"Unoplat-oss-atlas",permalink:"/unoplat-code-confluence/docs/category/unoplat-oss-atlas"}},a={},c=[{value:"Table of Contents",id:"table-of-contents",level:2},{value:"Introduction",id:"introduction",level:2},{value:"Prerequisites",id:"prerequisites",level:2},{value:"Codebase Requirements",id:"codebase-requirements",level:3},{value:"Required Configurations",id:"required-configurations",level:3},{value:"1. Ruff Configuration",id:"1-ruff-configuration",level:4},{value:"2. isort Configuration",id:"2-isort-configuration",level:4},{value:"Installation Requirements",id:"installation-requirements",level:3},{value:"Installation",id:"installation",level:2},{value:"1. Python Setup",id:"1-python-setup",level:3},{value:"2. Install Code Confluence",id:"2-install-code-confluence",level:3},{value:"Configuration",id:"configuration",level:2},{value:"JSON Configuration",id:"json-configuration",level:3},{value:"Required Fields",id:"required-fields",level:4},{value:"Example Configuration",id:"example-configuration",level:4},{value:"Environment Variables",id:"environment-variables",level:3},{value:"Running the Application",id:"running-the-application",level:3},{value:"Troubleshooting",id:"troubleshooting",level:2}];function d(e){const n={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",h3:"h3",h4:"h4",header:"header",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,r.R)(),...e.components},{Details:i}=n;return i||function(e,n){throw new Error("Expected "+(n?"component":"object")+" `"+e+"` to be defined: you likely forgot to import, pass, or provide it.")}("Details",!0),(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(n.header,{children:(0,o.jsx)(n.h1,{id:"quick-start-guide",children:"Quick Start Guide"})}),"\n",(0,o.jsxs)(n.p,{children:["Welcome to ",(0,o.jsx)(n.strong,{children:"Unoplat Code Confluence"})]}),"\n",(0,o.jsx)(n.admonition,{title:"Current Status",type:"info",children:(0,o.jsx)(n.p,{children:"Unoplat Code Confluence currently supports Python codebases and is in alpha stage. We're actively working on expanding language support and features."})}),"\n",(0,o.jsx)(n.h2,{id:"table-of-contents",children:"Table of Contents"}),"\n",(0,o.jsxs)(n.ol,{children:["\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"#introduction",children:"Introduction"})}),"\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"#prerequisites",children:"Prerequisites"})}),"\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"#installation",children:"Installation"})}),"\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"#configuration",children:"Configuration"})}),"\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"#troubleshooting",children:"Troubleshooting"})}),"\n"]}),"\n",(0,o.jsx)(n.h2,{id:"introduction",children:"Introduction"}),"\n",(0,o.jsx)(n.p,{children:"The current version supports parsing codebases and exporting a JSON representation of code graph. For more details, check out:"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsx)(n.li,{children:(0,o.jsx)(n.a,{href:"/docs/deep-dive/vision",children:"\ud83d\udcd8 Vision"})}),"\n"]}),"\n",(0,o.jsx)(n.h2,{id:"prerequisites",children:"Prerequisites"}),"\n",(0,o.jsx)(n.h3,{id:"codebase-requirements",children:"Codebase Requirements"}),"\n",(0,o.jsx)(n.admonition,{title:"Version Limitation",type:"caution",children:(0,o.jsx)(n.p,{children:"Currently supports Python codebases up to 3.11 (due to dependency on isort)"})}),"\n",(0,o.jsx)(n.p,{children:"Code Confluence relies on two powerful tools for import segregation and dependency analysis:"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.a,{href:"https://docs.astral.sh/ruff/",children:"\ud83d\udd0d Ruff"})," - For code analysis"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.a,{href:"https://pycqa.github.io/isort/",children:"\ud83d\udd04 isort"})," - For import organization"]}),"\n"]}),"\n",(0,o.jsx)(n.h3,{id:"required-configurations",children:"Required Configurations"}),"\n",(0,o.jsx)(n.h4,{id:"1-ruff-configuration",children:"1. Ruff Configuration"}),"\n",(0,o.jsxs)(n.p,{children:["Create a ",(0,o.jsx)(n.code,{children:"ruff.toml"})," file in your project root:"]}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-toml",metastring:'title="ruff.toml"',children:'target-version = "py311"\n\nexclude = [\n    ".git",\n    ".mypy_cache",\n    ".pytest_cache",\n    ".ruff_cache",\n    ".venv",\n    "venv",\n    "build",\n    "dist",\n]\n\nsrc = ["unoplat_code_confluence"]  # Adjust this to your project\'s source directory\nline-length = 320\n\n[lint]\n# Enable only flake8-tidy-imports\nselect = ["I","E402","INP001","TID","F401","F841"]\n\n[lint.per-file-ignores]\n"__init__.py" = ["E402","F401"]\n\n[lint.flake8-tidy-imports]\nban-relative-imports = "all"\n\n[lint.isort]\ncombine-as-imports = true\nforce-to-top = ["os","sys"]\n'})}),"\n",(0,o.jsx)(n.p,{children:"Run Ruff with:"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",children:"ruff check --fix . --unsafe-fixes\n"})}),"\n",(0,o.jsx)(n.h4,{id:"2-isort-configuration",children:"2. isort Configuration"}),"\n",(0,o.jsxs)(n.p,{children:["Create an ",(0,o.jsx)(n.code,{children:".isort.cfg"})," file:"]}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-ini",metastring:'title=".isort.cfg"',children:'[settings]\nknown_third_party = "Include third party dependencies here"\nimport_heading_stdlib = Standard Library\nimport_heading_thirdparty = Third Party\nimport_heading_firstparty = First Party\nimport_heading_localfolder = Local \npy_version = 311\nline_length = 500\n'})}),"\n",(0,o.jsx)(n.p,{children:"Run isort with:"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",children:"isort . --python-version 311\n"})}),"\n",(0,o.jsx)(n.admonition,{type:"note",children:(0,o.jsx)(n.p,{children:"This configuration is temporary for the alpha version and will be automated in future releases."})}),"\n",(0,o.jsx)(n.h3,{id:"installation-requirements",children:"Installation Requirements"}),"\n",(0,o.jsx)(n.p,{children:"Before starting, install these tools:"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.a,{href:"https://github.com/pyenv/pyenv",children:"\ud83d\udc0d PyEnv"})," - Python version manager"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.a,{href:"https://github.com/pypa/pipx",children:"\ud83d\udce6 Pipx"})," - Python app installer"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.a,{href:"https://python-poetry.org/",children:"\ud83c\udfad Poetry"})," - Dependency manager"]}),"\n"]}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",children:"pipx install poetry\n"})}),"\n",(0,o.jsx)(n.h2,{id:"installation",children:"Installation"}),"\n",(0,o.jsx)(n.h3,{id:"1-python-setup",children:"1. Python Setup"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",children:"pyenv install 3.12.1\npyenv global 3.12.1\n"})}),"\n",(0,o.jsx)(n.h3,{id:"2-install-code-confluence",children:"2. Install Code Confluence"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",metastring:'title="Install latest version"',children:"pipx install --python $(pyenv which python) 'git+https://github.com/unoplat/unoplat-code-confluence.git@unoplat-code-confluence-v0.17.0#subdirectory=unoplat-code-confluence'\n"})}),"\n",(0,o.jsx)(n.h2,{id:"configuration",children:"Configuration"}),"\n",(0,o.jsx)(n.h3,{id:"json-configuration",children:"JSON Configuration"}),"\n",(0,o.jsx)(n.admonition,{type:"tip",children:(0,o.jsxs)(n.p,{children:["All configuration fields support environment variable overrides using the ",(0,o.jsx)(n.code,{children:"UNOPLAT_"})," prefix."]})}),"\n",(0,o.jsx)(n.h4,{id:"required-fields",children:"Required Fields"}),"\n",(0,o.jsxs)(i,{children:[(0,o.jsxs)("summary",{children:[(0,o.jsx)("b",{children:"repositories"}),": Array of repositories to analyze"]}),(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"git_url"}),": Repository URL"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"output_path"}),": Analysis output directory"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"codebases"}),": Array of codebase configurations","\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"codebase_folder_name"}),": Codebase directory name"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"root_package_name"}),": Root package name"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"programming_language_metadata"}),": Language config","\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"language"}),": Programming language"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"package_manager"}),": Package manager type"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"language_version"}),": Language version"]}),"\n"]}),"\n"]}),"\n"]}),"\n"]}),"\n"]})]}),"\n",(0,o.jsxs)(i,{children:[(0,o.jsxs)("summary",{children:[(0,o.jsx)("b",{children:"archguard"}),": ArchGuard tool configuration"]}),(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"download_url"}),": ArchGuard download URL"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"download_directory"}),": Local storage directory"]}),"\n"]})]}),"\n",(0,o.jsxs)(i,{children:[(0,o.jsxs)("summary",{children:[(0,o.jsx)("b",{children:"logging_handlers"}),": Logging configuration"]}),(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"sink"}),": Log file path"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"format"}),": Log message format"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"rotation"}),": Log rotation size"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"retention"}),": Log retention period"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.code,{children:"level"}),": Logging level"]}),"\n"]})]}),"\n",(0,o.jsx)(n.h4,{id:"example-configuration",children:"Example Configuration"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-json",metastring:'title="config.json"',children:'{\n  "repositories": [\n    {\n      "git_url": "https://github.com/unoplat/unoplat-code-confluence",\n      "output_path": "/Users/jayghiya/Documents/unoplat",\n      "codebases": [\n        {\n          "codebase_folder_name": "unoplat-code-confluence",\n          "root_package_name": "unoplat_code_confluence",\n          "programming_language_metadata": {\n            "language": "python",\n            "package_manager": "poetry",\n            "language_version": "3.12.0"\n          }        \n        }\n      ]\n    }\n  ],\n  "archguard": {\n    "download_url": "archguard/archguard",\n    "download_directory": "/Users/jayghiya/Documents/unoplat"\n  },\n  "logging_handlers": [\n    {\n      "sink": "~/Documents/unoplat/app.log",\n      "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <magenta>{thread.name}</magenta> - <level>{message}</level>",\n      "rotation": "10 MB",\n      "retention": "10 days",\n      "level": "DEBUG"\n    }\n  ]\n}\n'})}),"\n",(0,o.jsx)(n.h3,{id:"environment-variables",children:"Environment Variables"}),"\n",(0,o.jsxs)(n.p,{children:["Create a ",(0,o.jsx)(n.code,{children:".env.dev"})," file:"]}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-env",metastring:'title=".env.dev"',children:"UNOPLAT_ENV=dev\nUNOPLAT_DEBUG=true \nUNOPLAT_GITHUB_TOKEN=Your_Github_Pat_Token\n"})}),"\n",(0,o.jsx)(n.h3,{id:"running-the-application",children:"Running the Application"}),"\n",(0,o.jsx)(n.pre,{children:(0,o.jsx)(n.code,{className:"language-bash",children:"unoplat-code-confluence --config /path/to/your/config.json\n"})}),"\n",(0,o.jsx)(n.h2,{id:"troubleshooting",children:"Troubleshooting"}),"\n",(0,o.jsxs)(n.admonition,{title:"Common Issues",type:"danger",children:[(0,o.jsx)(n.p,{children:"If you encounter any issues, please check:"}),(0,o.jsxs)(n.ol,{children:["\n",(0,o.jsx)(n.li,{children:"Python version compatibility"}),"\n",(0,o.jsx)(n.li,{children:"Environment variable configuration"}),"\n",(0,o.jsx)(n.li,{children:"JSON configuration syntax"}),"\n",(0,o.jsxs)(n.li,{children:["For Code Grammar issues please check out current issues and possible resolutions on ",(0,o.jsx)(n.a,{href:"https://github.com/unoplat/unoplat-code-confluence/",children:"GitHub"})," page."]}),"\n"]})]}),"\n",(0,o.jsxs)(n.p,{children:["For more help, visit our ",(0,o.jsx)(n.a,{href:"https://github.com/unoplat/unoplat-code-confluence/issues",children:"GitHub Issues"})," page or join our ",(0,o.jsx)(n.a,{href:"https://discord.com/channels/1131597983058755675/1169968780953260106",children:"Discord"})," community."]})]})}function u(e={}){const{wrapper:n}={...(0,r.R)(),...e.components};return n?(0,o.jsx)(n,{...e,children:(0,o.jsx)(d,{...e})}):d(e)}},8453:(e,n,i)=>{i.d(n,{R:()=>s,x:()=>l});var o=i(6540);const r={},t=o.createContext(r);function s(e){const n=o.useContext(t);return o.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:s(e.components),o.createElement(t.Provider,{value:n},e.children)}}}]);