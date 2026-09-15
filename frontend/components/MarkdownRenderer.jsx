import React from 'react';

/**
 * Parses inline Markdown syntax:
 * - **bold** or __bold__ -> <strong>bold</strong>
 * - *italic* or _italic_ -> <em>italic</em>
 * - `code` -> <code>code</code>
 */
function renderInlineMarkdown(text) {
  if (!text) return '';

  // Match bold, italic, inline code
  const tokenRegex = /(`[^`]+`|\*\*[^*]+\*\*|__[^*]+__|\*[^*]+\*|_[^*]+_)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, index) => {
    if (!part) return null;

    // Inline Code
    if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
      return (
        <code
          key={index}
          style={{
            background: 'var(--color-surface-subtle, #f3f4f6)',
            padding: '2px 6px',
            borderRadius: '4px',
            fontSize: '0.9em',
            fontFamily: 'monospace',
            color: 'var(--primary-700, #1d4ed8)',
          }}
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    // Bold (** or __)
    if (
      ((part.startsWith('**') && part.endsWith('**')) || (part.startsWith('__') && part.endsWith('__'))) &&
      part.length >= 4
    ) {
      return (
        <strong key={index} style={{ fontWeight: 600, color: 'var(--color-text-main, #111827)' }}>
          {part.slice(2, -2)}
        </strong>
      );
    }

    // Italic (* or _)
    if (
      ((part.startsWith('*') && part.endsWith('*')) || (part.startsWith('_') && part.endsWith('_'))) &&
      part.length >= 2
    ) {
      return (
        <em key={index} style={{ fontStyle: 'italic' }}>
          {part.slice(1, -1)}
        </em>
      );
    }

    return part;
  });
}

/**
 * MarkdownRenderer component
 * Safely parses and renders headings, paragraphs, lists, and inline styles.
 */
export default function MarkdownRenderer({ content, className = '' }) {
  if (!content) return null;

  // Normalize line endings
  const normalized = content.replace(/\r\n/g, '\n');
  
  // Split into paragraphs/blocks by empty lines
  const blocks = normalized.split(/\n\n+/);

  return (
    <div className={`markdown-body ${className}`} style={{ lineHeight: '1.6', fontSize: '14.5px' }}>
      {blocks.map((block, blockIdx) => {
        const lines = block.split('\n');

        // 1. Check if block is a heading (e.g. # Heading)
        if (lines.length === 1) {
          const headingMatch = block.match(/^(#{1,6})\s+(.*)$/);
          if (headingMatch) {
            const level = headingMatch[1].length;
            const textContent = headingMatch[2];
            const Tag = `h${level}`;
            
            // Return heading element with clean sizing
            const sizes = {
              1: '1.6rem',
              2: '1.3rem',
              3: '1.15rem',
              4: '1.05rem',
              5: '1.0rem',
              6: '0.9rem'
            };
            return (
              <Tag
                key={blockIdx}
                style={{
                  fontSize: sizes[level] || '1.15rem',
                  fontWeight: 600,
                  margin: '14px 0 6px 0',
                  color: 'var(--color-text-main)',
                  lineHeight: '1.3'
                }}
              >
                {renderInlineMarkdown(textContent)}
              </Tag>
            );
          }
        }

        // 2. Check if the block is an unordered list
        const isBulletList = lines.every((l) => /^\s*[-*•]\s+/.test(l));
        if (isBulletList) {
          return (
            <ul
              key={blockIdx}
              style={{
                margin: '10px 0',
                paddingLeft: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
                listStyleType: 'disc'
              }}
            >
              {lines.map((l, lIdx) => {
                const cleanItem = l.replace(/^\s*[-*•]\s+/, '');
                return (
                  <li key={lIdx} style={{ color: 'var(--color-text-secondary)' }}>
                    {renderInlineMarkdown(cleanItem)}
                  </li>
                );
              })}
            </ul>
          );
        }

        // 3. Check if the block is an ordered list
        const isOrderedList = lines.every((l) => /^\s*\d+\.\s+/.test(l));
        if (isOrderedList) {
          return (
            <ol
              key={blockIdx}
              style={{
                margin: '10px 0',
                paddingLeft: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}
            >
              {lines.map((l, lIdx) => {
                const cleanItem = l.replace(/^\s*\d+\.\s+/, '');
                return (
                  <li key={lIdx} style={{ color: 'var(--color-text-secondary)' }}>
                    {renderInlineMarkdown(cleanItem)}
                  </li>
                );
              })}
            </ol>
          );
        }

        // 4. Regular paragraph
        return (
          <p key={blockIdx} style={{ margin: blockIdx > 0 ? '12px 0 0 0' : '0', color: 'var(--color-text-secondary)' }}>
            {lines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {lIdx > 0 && <br />}
                {renderInlineMarkdown(line)}
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
}
