import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

export function renderMarkdown(text) {
  const rawHtml = marked.parse(String(text || ''))
  return DOMPurify.sanitize(rawHtml, {
    USE_PROFILES: { html: true },
  })
}