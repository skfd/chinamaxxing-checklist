# AGENTS.md

Guide for AI agents working on the CHINAMAXXING Checklist project.

## Project Overview

A static web-based checklist application for tracking progress in the "Becoming Chinese" / "Chinamaxxing" trend. Users track their journey through Chinese language, culture, politics, and lifestyle habits.

**Live Site:** https://skfd.github.io/chinamaxxing-checklist/

## Tech Stack

- **Frontend:** Vanilla JavaScript (ES6 modules), HTML5, CSS3
- **No build step** - served directly as static files
- **No dependencies** - pure browser APIs
- **State:** localStorage + URL-based state sharing (base64 encoded)
- **Fonts:** Google Fonts (Oswald, ZCOOL QingKe HuangYou)
- **Analytics:** GoatCounter (privacy-friendly)

## Version Management

**CRITICAL:** Two independent version numbers exist:

| Constant | Location | When to Increment |
|----------|----------|-------------------|
| `CODE_VERSION` | `assets/js/data.js:1` | Any change to `app.js`, `styles.css`, or `index.html` |
| `DATA_VERSION` | `assets/js/data.js:2` | Any change to checklist items in `data.js` |

Update the version display in `index.html` header:
```html
<a href="..." class="version-link">data v{DATA_VERSION}, code v{CODE_VERSION}</a>
```

## Data Structure

The checklist is a nested tree structure in `assets/js/data.js`:

```javascript
export const checklistData = {
  "version": 1,  // Must match DATA_VERSION
  "items": [
    {
      "title": "Section Title",
      "items": [
        {
          "title": "Subsection Title",
          "items": [
            {
              "id": "unique-kebab-case-id",
              "text": "Item text with **markdown bold** support",
              "link": "https://optional-link.com",  // Optional
              "items": [...]  // Optional nested items
            }
          ]
        }
      ]
    },
    {
      "type": "blockquote",
      "text": "Inspirational quote between sections"
    }
  ]
}
```

**Item ID Rules:**
- Kebab-case (lowercase, hyphens)
- Must be unique across entire checklist
- Auto-generated from text but can be manually specified
- Changing IDs breaks user saved state (localStorage)

## Development Rules

### Required Practices

1. **Increment versions** when modifying code or data (see Version Management)
2. **Preserve backwards compatibility** - changing item IDs orphaned user progress
3. **Test both pages** - changes must work on both `index.html` and `print.html`
4. **No build tools** - code must run directly in browsers
5. **No external dependencies** - keep the project dependency-free

### Code Style

- **JavaScript:** ES6 modules, class-based (see `ChecklistApp` pattern)
- **CSS:** BEM-like naming, no preprocessors
- **HTML:** Semantic elements, accessibility attributes where needed
- **Indentation:** 4 spaces (follow existing files)
- **Comments:** Minimal, only for non-obvious logic

### UI/UX Constraints

- **Theme:** Heroes of Might & Magic III-inspired aesthetic (leather, parchment, red/gold)
- **Fonts:** `Oswald` for headers/UI, `ZCOOL QingKe HuangYou` for body text
- **Colors:** 
  - Primary red: `#BF1B2C`
  - Gold accent: `#F5D76E`
  - Parchment: `#F0E4CE`
  - Dark brown: `#3A2A1A`
- **Responsive:** Grid layout adapts to screen size

## State Management

User progress is stored in `localStorage`:
- Key: `chinamaxxing-checklist-v2`
- Format: `{ version: number, checked: { [id]: boolean } }`

Shareable links encode state in URL `?state=` parameter (base64 JSON).

## Print Version

`print.html` is a separate page optimized for printing:
- Loads same `data.js`
- Different rendering logic for 2-column A4 layout
- Auto-triggers print dialog on load
- Minimal styling (black/white, serif fonts)
- Typographic

## Common Tasks

### Adding/Modifying Checklist Items

1. Edit `assets/js/data.js` directly (or use `generate_data.py` from markdown)
2. Increment `DATA_VERSION`
3. Update version display in `index.html`
4. Test that existing user state migrates correctly

### Adding New Features

1. Modify `assets/js/app.js` for logic
2. Modify `assets/css/styles.css` for styling
3. Increment `CODE_VERSION`
4. Update version display in `index.html`
5. Test on both desktop and mobile viewports

### Updating Links

Item links are stored in `data.js` as the `link` property. Links open in new tabs with `rel="noopener"`.

## Deployment

Static hosting on GitHub Pages. Push to `main` branch to deploy.

No CI/CD - changes are live immediately after push.

## Things NOT to Do

- Don't add build tools (webpack, vite, etc.)
- Don't add npm dependencies
- Don't change item IDs casually (breaks user data)
- Don't add heavy JavaScript libraries
- Don't modify the HOMM3 aesthetic without good reason
- Don't use emojis in code (they're fine in checklist content)
