// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Code Confluence',
  tagline: 'Powered by ',
  customFields: {
    taglineImage: 'img/Unoplat_Logo.svg',
  },
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://docs.unoplat.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'unoplat', // Usually your GitHub org/user name.
  projectName: 'code-confluence', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  staticDirectories: ['static'],
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/', // Serve the docs at the site's root
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false, // Disable the blog plugin
        pages: false, // Disable pages plugin to avoid conflicts
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themes: [
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      ({
        // Index docs only (since we disabled blog and pages)
        indexDocs: true,
        indexBlog: false,
        indexPages: false,
        
        // For docs-only mode, use "/" as route base path
        docsRouteBasePath: "/",
        
        // Language support
        language: ["en"],
        
        // Position search in middle of navbar
        searchBarPosition: "right",
        
        // Enable keyboard shortcuts
        searchBarShortcut: true,
        searchBarShortcutHint: true,
        
        // Highlight search terms on target page
        highlightSearchTermsOnTargetPage: true,
        
        // Search result limits and context
        searchResultLimits: 8,
        searchResultContextMaxLength: 100,
        
        // Performance optimizations
        hashed: true,
        
        // Remove default stop words for programming docs
        removeDefaultStopWordFilter: ["en"],
        
        // Exclude files from indexing to avoid errors
        ignoreFiles: [
          // Image files
          /.*\.(png|jpg|jpeg|gif|svg|ico|webp|bmp|tiff?)$/i,
          // Document files
          /.*\.(pdf|docx?|xlsx?|pptx?|odt|ods|odp)$/i,
          // Archive files
          /.*\.(zip|tar|gz|bz2|7z|rar)$/i,
          // Media files
          /.*\.(mp3|mp4|avi|mov|wmv|flv|mkv|webm|ogg|wav)$/i,
          // Font files
          /.*\.(woff2?|ttf|otf|eot)$/i,
          // Exclude entire static directory
          "static/**/*",
          // Exclude build artifacts
          "build/**/*",
          ".docusaurus/**/*",
          // Exclude yarn files
          ".yarn/**/*",
          ".pnp.*",
        ],
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      // image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: '                ',
        logo: {
          alt: 'Code Confluence',
          src: 'img/Unoplat_Logo.svg',
          srcDark: 'img/Unoplat_Logo.svg', // Using same logo for dark mode
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            label: 'Contact Us',
            href: 'https://www.unoplat.io/contact/',
            position: 'left',
          },
        ],
      },
      // algolia: {
      //   apiKey: '21acb3ae035a0a588a5377e5e9e06c3b',
      //   indexName: 'unoplatio',
      //   // Optional: see doc section below
      //   appId: '0PYM5MWDAT', // Optional, if using App ID
      //   contextualSearch: true,
      //   // Optional: Algolia search parameters
      //   searchParameters: {},
      // },  
      // footer: {
      //   style: 'dark',
      //   links: [
      //     {
      //       title: 'Docs',
      //       items: [
      //         {
      //           label: 'Tutorial',
      //           to: '/docs/intro',
      //         },
      //       ],
      //     },
      //     {
      //       title: 'Community',
      //       items: [
      //         {
      //           label: 'Stack Overflow',
      //           href: 'https://stackoverflow.com/questions/tagged/docusaurus',
      //         },
      //         {
      //           label: 'Discord',
      //           href: 'https://discordapp.com/invite/docusaurus',
      //         },
      //         {
      //           label: 'Twitter',
      //           href: 'https://twitter.com/docusaurus',
      //         },
      //       ],
      //     },
      //     {
      //       title: 'More',
      //       items: [
      //         // {
      //         //   label: 'Blog',
      //         //   to: '/blog',
      //         // },
      //         {
      //           label: 'GitHub',
      //           href: 'https://github.com/facebook/docusaurus',
      //         },
      //       ],
      //     },
      //   ],
      //   copyright: `Copyright © ${new Date().getFullYear()} Code Confluence, Inc. Built with Docusaurus.`,
      // },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      zoom: {
        selector: '.zoomable',
        background: {
          light: 'rgb(255, 255, 255)',
          dark: 'rgb(50, 50, 50)'
        },
        config: {
          // options you can specify via https://github.com/francoischalifour/medium-zoom#usage
        }
      },
    }),
  stylesheets: [
    '/src/css/custom.css',
  ],
  webpack: {
    jsLoader: () => ({
      loader: require.resolve('swc-loader'),
      options: {
        jsc: {
          parser: {
            syntax: 'ecmascript',
            jsx: true,
          },
          transform: {
            react: {
              runtime: 'automatic',
            },
          },
        },
      },
    }),
  }
};

export default config;
