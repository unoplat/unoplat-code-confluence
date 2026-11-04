import React from "react";
import ReactMarkdown, { type Components } from "react-markdown";

interface ArtifactMarkdownPreviewProps {
  markdown: string;
}

const markdownComponents: Components = {
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
};

// Generated files are untrusted. Raw HTML is dropped, default URL filtering stays
// on, and images are removed so that opening a file cannot fetch a remote URL.
const disallowedMarkdownElements = ["img"];

export function ArtifactMarkdownPreview({
  markdown,
}: ArtifactMarkdownPreviewProps): React.ReactElement {
  return (
    <div className="prose prose-sm dark:prose-invert prose-code:before:content-none prose-code:after:content-none max-w-none [overflow-wrap:anywhere]">
      <ReactMarkdown
        skipHtml
        disallowedElements={disallowedMarkdownElements}
        components={markdownComponents}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
