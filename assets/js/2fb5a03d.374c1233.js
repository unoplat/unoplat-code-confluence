"use strict";(self.webpackChunkcode_confluence=self.webpackChunkcode_confluence||[]).push([[270],{4555:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>s,default:()=>u,frontMatter:()=>i,metadata:()=>r,toc:()=>c});var a=t(4848),o=t(8453);const i={sidebar_position:2},s="Quick Start Guide",r={id:"quickstart/how-to-run",title:"Quick Start Guide",description:"Welcome to Unoplat Code Confluence! This guide will help you quickly set up and start using our platform to enhance your codebase management and collaboration.",source:"@site/docs/quickstart/how-to-run.md",sourceDirName:"quickstart",slug:"/quickstart/how-to-run",permalink:"/unoplat-code-confluence/docs/quickstart/how-to-run",draft:!1,unlisted:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/quickstart/how-to-run.md",tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"tutorialSidebar",previous:{title:"Quickstart",permalink:"/unoplat-code-confluence/docs/category/quickstart"},next:{title:"Unoplat-oss-atlas",permalink:"/unoplat-code-confluence/docs/category/unoplat-oss-atlas"}},l={},c=[{value:"Table of Contents",id:"table-of-contents",level:2},{value:"Introduction",id:"introduction",level:2},{value:"Prerequisites",id:"prerequisites",level:2},{value:"1. Graph Database Setup",id:"1-graph-database-setup",level:2},{value:"Installation",id:"installation",level:3},{value:"2. Generate Summary and Ingest Codebase",id:"2-generate-summary-and-ingest-codebase",level:2},{value:"Ingestion Configuration",id:"ingestion-configuration",level:3},{value:"Run the Unoplat Code Confluence Ingestion Utility",id:"run-the-unoplat-code-confluence-ingestion-utility",level:3},{value:"3. Setup Chat Interface",id:"3-setup-chat-interface",level:2},{value:"Query Engine Configuration",id:"query-engine-configuration",level:3},{value:"Launch Query Engine",id:"launch-query-engine",level:3},{value:"Troubleshooting",id:"troubleshooting",level:2}];function d(e){const n={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",header:"header",li:"li",ol:"ol",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,o.R)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(n.header,{children:(0,a.jsx)(n.h1,{id:"quick-start-guide",children:"Quick Start Guide"})}),"\n",(0,a.jsxs)(n.p,{children:["Welcome to ",(0,a.jsx)(n.strong,{children:"Unoplat Code Confluence"}),"! This guide will help you quickly set up and start using our platform to enhance your codebase management and collaboration."]}),"\n",(0,a.jsx)(n.h2,{id:"table-of-contents",children:"Table of Contents"}),"\n",(0,a.jsxs)(n.ol,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#introduction",children:"Introduction"})}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#prerequisites",children:"Prerequisites"})}),"\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.a,{href:"#1-graph-database-setup",children:"1. Graph Database Setup"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#installation",children:"Installation"})}),"\n"]}),"\n"]}),"\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.a,{href:"#2-generate-summary-and-ingest-codebase",children:"2. Generate Summary and Ingest Codebase"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#ingestion-configuration",children:"Ingestion Configuration"})}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#run-the-unoplat-code-confluence-ingestion-utility",children:"Run the Unoplat Code Confluence Ingestion Utility"})}),"\n"]}),"\n"]}),"\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.a,{href:"#3-setup-chat-interface",children:"3. Setup Chat Interface"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#query-engine-configuration",children:"Query Engine Configuration"})}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#launch-query-engine",children:"Launch Query Engine"})}),"\n"]}),"\n"]}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"#troubleshooting",children:"Troubleshooting"})}),"\n"]}),"\n",(0,a.jsx)(n.h2,{id:"introduction",children:"Introduction"}),"\n",(0,a.jsxs)(n.p,{children:[(0,a.jsx)(n.strong,{children:"Unoplat Code Confluence"})," empowers developers to effortlessly navigate and understand complex codebases. By leveraging a graph database and an intuitive chat interface, our platform enhances collaboration and accelerates onboarding."]}),"\n",(0,a.jsx)(n.h2,{id:"prerequisites",children:"Prerequisites"}),"\n",(0,a.jsx)(n.p,{children:"Before you begin, ensure you have the following installed on your system:"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"https://www.docker.com/get-started",children:"Docker"})}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"https://github.com/pypa/pipx",children:"Pipx"})}),"\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.a,{href:"https://python-poetry.org/",children:"Poetry"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"pipx install poetry\n"})}),"\n",(0,a.jsx)(n.h2,{id:"1-graph-database-setup",children:"1. Graph Database Setup"}),"\n",(0,a.jsx)(n.h3,{id:"installation",children:"Installation"}),"\n",(0,a.jsxs)(n.ol,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Run the Neo4j Container"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"docker run \\\n  --name neo4j-container \\\n  --restart always \\\n  --publish 7474:7474 \\\n  --publish 7687:7687 \\\n  --env NEO4J_AUTH=neo4j/Ke7Rk7jB:Jn2Uz: \\\n  --volume /Users/jayghiya/Documents/unoplat/neo4j-data:/data \\\n  --volume /Users/jayghiya/Documents/unoplat/neo4j-plugins/:/plugins \\\n  neo4j:5.23.0\n"})}),"\n",(0,a.jsx)(n.h2,{id:"2-generate-summary-and-ingest-codebase",children:"2. Generate Summary and Ingest Codebase"}),"\n",(0,a.jsx)(n.h3,{id:"ingestion-configuration",children:"Ingestion Configuration"}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-json",children:'{\n  "local_workspace_path": "/Users/jayghiya/Documents/unoplat/textgrad/textgrad",\n  "output_path": "/Users/jayghiya/Documents/unoplat",\n  "output_file_name": "unoplat_textgrad.md",\n  "codebase_name": "textgrad",\n  "programming_language": "python",\n  "repo": {\n    "download_url": "archguard/archguard",\n    "download_directory": "/Users/jayghiya/Documents/unoplat"\n  },\n  "api_tokens": {\n    "github_token": "Your github pat token"\n  },\n  "llm_provider_config": {\n    "openai": {\n      "api_key": "Your openai api key",\n      "model": "gpt-4o-mini",\n      "model_type": "chat",\n      "max_tokens": 512,\n      "temperature": 0.0\n    }\n  },\n  "logging_handlers": [\n    {\n      "sink": "~/Documents/unoplat/app.log",\n      "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <magenta>{thread.name}</magenta> - <level>{message}</level>",\n      "rotation": "10 MB",\n      "retention": "10 days",\n      "level": "DEBUG"\n    }\n  ],\n  "parallisation": 3,\n  "sentence_transformer_model": "jinaai/jina-embeddings-v3",\n  "neo4j_uri": "bolt://localhost:7687",\n  "neo4j_username": "neo4j",\n  "neo4j_password": "Ke7Rk7jB:Jn2Uz:"\n}\n'})}),"\n",(0,a.jsx)(n.h3,{id:"run-the-unoplat-code-confluence-ingestion-utility",children:"Run the Unoplat Code Confluence Ingestion Utility"}),"\n",(0,a.jsxs)(n.ol,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Installation"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@main#subdirectory=unoplat-code-confluence'\n"})}),"\n",(0,a.jsxs)(n.ol,{start:"2",children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Run the Ingestion Utility"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"unoplat-code-confluence --config /path/to/your/config.json\n"})}),"\n",(0,a.jsxs)(n.ol,{start:"3",children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Example Run"})}),"\n"]}),"\n",(0,a.jsx)("img",{src:t(9306).A,alt:"Unoplat Code Confluence Output",className:"zoomable"}),"\n",(0,a.jsx)(n.p,{children:"After running the ingestion utility, you'll find the generated markdown file in the specified output directory. The file will contain a comprehensive summary of your codebase. Also the summary and other relevant metadata would be stored in the graph database."}),"\n",(0,a.jsxs)(n.p,{children:["Also check out the Neo4j Browser to visualize the graph database. Go to ",(0,a.jsx)(n.a,{href:"http://localhost:7474/browser/",children:"http://localhost:7474/browser/"})]}),"\n",(0,a.jsx)("img",{src:t(7660).A,alt:"Unoplat Code Confluence Graph Database",className:"zoomable"}),"\n",(0,a.jsx)(n.h2,{id:"3-setup-chat-interface",children:"3. Setup Chat Interface"}),"\n",(0,a.jsx)(n.h3,{id:"query-engine-configuration",children:"Query Engine Configuration"}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-json",children:'{\n  "sentence_transformer_model": "jinaai/jina-embeddings-v3",\n  "neo4j_uri": "bolt://localhost:7687",\n  "neo4j_username": "neo4j",\n  "neo4j_password": "your neo4j password",\n  "provider_model_dict": {\n    "model_provider": "openai/gpt-4o-mini",\n    "model_provider_args": {\n      "api_key": "your openai api key",\n      "max_tokens": 500,\n      "temperature": 0.0\n    }\n  }\n}\n'})}),"\n",(0,a.jsx)(n.h3,{id:"launch-query-engine",children:"Launch Query Engine"}),"\n",(0,a.jsxs)(n.ol,{children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Installation"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"pipx install 'git+https://github.com/unoplat/unoplat-code-confluence.git@main#subdirectory=unoplat-code-confluence-query-engine'\n"})}),"\n",(0,a.jsxs)(n.ol,{start:"2",children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Run the Query Engine"})}),"\n"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-bash",children:"unoplat-code-confluence-query-engine --config /path/to/your/config.json\n"})}),"\n",(0,a.jsxs)(n.ol,{start:"3",children:["\n",(0,a.jsx)(n.li,{children:(0,a.jsx)(n.strong,{children:"Example Run"})}),"\n"]}),"\n",(0,a.jsx)("img",{src:t(8368).A,alt:"Unoplat Code Confluence Query Engine",className:"zoomable"}),"\n",(0,a.jsxs)(n.p,{children:["We had added ",(0,a.jsx)(n.a,{href:"https://github.com/zou-group/textgrad",children:"textgrad"})," to our graph database in the configuration of ingestion utility. You can now chat with the codebase. To view existing codebases press ctrl + e."]}),"\n",(0,a.jsx)("img",{src:t(8068).A,alt:"Unoplat Code Confluence Existing Codebases",className:"zoomable"}),"\n",(0,a.jsx)(n.h2,{id:"troubleshooting",children:"Troubleshooting"})]})}function u(e={}){const{wrapper:n}={...(0,o.R)(),...e.components};return n?(0,a.jsx)(n,{...e,children:(0,a.jsx)(d,{...e})}):d(e)}},8068:(e,n,t)=>{t.d(n,{A:()=>a});const a=t.p+"assets/images/code-confluence-existing-codebases-1304445cc3c0e69f0e46b15a338ee720.png"},7660:(e,n,t)=>{t.d(n,{A:()=>a});const a=t.p+"assets/images/code-confluence-neo4j-browser-7fe7f55087853205351a652508d13dae.png"},9306:(e,n,t)=>{t.d(n,{A:()=>a});const a=t.p+"assets/images/code-confluence-parsing-ingestion-ae71b777dcdd7aef8a13a19fce66c6cc.png"},8368:(e,n,t)=>{t.d(n,{A:()=>a});const a=t.p+"assets/images/code-confluence-query-engine-5e755581cb605bda6c4d9aca1ee581ce.png"},8453:(e,n,t)=>{t.d(n,{R:()=>s,x:()=>r});var a=t(6540);const o={},i=a.createContext(o);function s(e){const n=a.useContext(i);return a.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:s(e.components),a.createElement(i.Provider,{value:n},e.children)}}}]);