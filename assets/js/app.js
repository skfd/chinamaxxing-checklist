import { checklistData } from './data.js';

class ChecklistApp {
    constructor() {
        this.data = checklistData;
        this.state = this.loadState();
        this.init();
    }

    loadState() {
        const saved = localStorage.getItem('chinamaxxing-checklist-v2');
        if (saved) {
            return JSON.parse(saved);
        }

        // Check for v1 (legacy) data if needed?
        // User requested no initial migration, so we start fresh or with empty.

        return {
            version: this.data.version,
            checked: {}
        };
    }

    saveState() {
        localStorage.setItem('chinamaxxing-checklist-v2', JSON.stringify(this.state));
    }

    init() {
        // Version check / Future Migration logic
        if (this.state.version < this.data.version) {
            console.log("Migration needed (future implementation)");
            // this.migrate();
            this.state.version = this.data.version;
            this.saveState();
        }

        this.render();
        this.attachEventListeners();
        this.updateStats();
    }

    formatText(text) {
        // Basic HTML escaping
        const escaped = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Parse bold markdown: **text** -> <strong>text</strong>
        return escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    render() {
        const container = document.getElementById('checklist-content');
        container.innerHTML = '';

        // Iterate over top-level items (Sections generally)
        for (let item of this.data.items) {
            container.appendChild(this.createNode(item));
        }
    }

    createNode(item, level = 0) {
        // Decision logic:
        // 1. If it has 'items', it's a container (Section, Subsection, or Nested Item).
        // 2. If it has 'type: blockquote', it's a blockquote.
        // 3. Otherwise, it's a standard checklist item.

        // Special case: Blockquote
        if (item.type === 'blockquote') {
            const el = document.createElement('blockquote');
            el.textContent = item.text;
            return el;
        }

        // Case A: Container (Section/Subsection/Nested Group)
        if (item.items && item.title) {
            // It's a Section (Level 0) or Subsection (Level 1)
            const wrapper = document.createElement('div');
            wrapper.className = level === 0 ? 'section' : 'subsection';

            // Header
            if (level === 0) {
                const header = document.createElement('div');
                header.className = 'section-header';
                header.innerHTML = item.title;
                wrapper.appendChild(header);
            } else {
                const header = document.createElement('h3');
                header.innerHTML = item.title;
                wrapper.appendChild(header);
            }

            // Content Container
            const content = document.createElement('div');
            // Sections have a content wrapper with padding, subsections don't explicitly need one but it helps
            if (level === 0) content.className = 'section-content';

            for (let child of item.items) {
                content.appendChild(this.createNode(child, level + 1));
            }

            wrapper.appendChild(content);
            return wrapper;
        }

        // Case B Checklist Item (Leaf or Node with children but no title? Or just Item with children)
        // Note: The data structure has items inside items.
        // If an item has an ID, it's a checklist item.

        if (item.id) {
            return this.createChecklistItem(item, level);
        }

        // Fallback
        return document.createElement('div');
    }

    createChecklistItem(item, level) {
        const itemEl = document.createElement('div');
        // Indent handling: Level 2 is top-level item (Section -> Subsection -> Item)
        // So indent 0.
        // If deeply nested, we add indent.
        // The original CSS had .indent-1, .indent-2
        // Let's determine indent based on level relative to Subsection.
        // Section=0, Subsection=1, Item=2.
        // So if level > 2, it is indented.

        let indentClass = '';
        if (level > 2) {
            indentClass = `indent-${level - 2}`;
        }

        const isChecked = this.state.checked[item.id] || false;

        itemEl.className = `checklist-item ${isChecked ? 'checked' : ''} ${indentClass}`;
        itemEl.dataset.id = item.id;

        const checkbox = document.createElement('div');
        checkbox.className = `checkbox ${isChecked ? 'checked' : ''}`;

        const textDiv = document.createElement('div');
        textDiv.className = 'item-text';
        textDiv.innerHTML = this.formatText(item.text);

        itemEl.appendChild(checkbox);
        itemEl.appendChild(textDiv);

        if (item.link) {
            const link = document.createElement('a');
            link.className = 'item-link';
            link.href = item.link;
            link.target = '_blank';
            link.rel = 'noopener';
            link.innerHTML = `<img src="assets/cloud1.png" alt="link" class="link-icon">`;
            link.addEventListener('click', (e) => e.stopPropagation());
            itemEl.appendChild(link);
        }

        itemEl.addEventListener('click', (e) => {
            // Stop propagation so we don't toggle parent items if this is a nested item
            e.stopPropagation();
            this.toggleItem(item.id);
        });

        // Recursive rendering of children (if item has sub-items but no title, it's a nested list)
        if (item.items && item.items.length > 0) {
            // We need a container for children to ensure they appear BELOW the item line
            // But strict HTML structure in the original was flat list with margin-left.
            // If we wrap them, `itemEl` becomes a parent div.
            // Let's wrap the checkbox+text in a row div, and put children in a sibling div.

            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.width = '100%';
            row.style.alignItems = 'flex-start';
            // Move contents to row
            while (itemEl.firstChild) row.appendChild(itemEl.firstChild);
            itemEl.appendChild(row);

            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'nested-items';
            // childrenContainer.style.marginLeft = '20px'; // Visual indent

            for (let child of item.items) {
                childrenContainer.appendChild(this.createNode(child, level + 1));
            }
            itemEl.appendChild(childrenContainer);
            itemEl.style.flexDirection = 'column'; // Allow children to stack below
        }

        return itemEl;
    }

    toggleItem(id) {
        if (this.state.checked[id]) {
            delete this.state.checked[id];
        } else {
            this.state.checked[id] = true;
        }
        this.saveState();

        // Update UI directly instead of full re-render for performance?
        // Full re-render is safer for sync.
        this.render();
        this.updateStats();
    }

    getAllItemIds(items = this.data.items, ids = []) {
        for (let item of items) {
            if (item.id) ids.push(item.id);
            if (item.items) this.getAllItemIds(item.items, ids);
        }
        return ids;
    }

    toggleAll() {
        const allIds = this.getAllItemIds();
        const allChecked = allIds.every(id => this.state.checked[id]);

        if (allChecked) {
            this.state.checked = {};
        } else {
            allIds.forEach(id => this.state.checked[id] = true);
        }

        this.saveState();
        this.render();
        this.updateStats();
    }

    resetAll() {
        if (confirm('Are you sure you want to reset ALL progress? This cannot be undone!')) {
            this.state.checked = {};
            this.saveState();
            this.render();
            this.updateStats();
        }
    }

    updateStats() {
        const allIds = this.getAllItemIds();
        const total = allIds.length;
        const completed = Object.keys(this.state.checked).length;
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

        document.getElementById('completed-count').textContent = completed;
        document.getElementById('total-count').textContent = total;
        document.getElementById('percentage').textContent = percentage + '%';
    }

    attachEventListeners() {
        document.getElementById('toggle-all').addEventListener('click', () => this.toggleAll());
        document.getElementById('reset-all').addEventListener('click', () => this.resetAll());
    }
}

// Initialize
// Wait for DOM? It's a module usually deferred.
new ChecklistApp();
