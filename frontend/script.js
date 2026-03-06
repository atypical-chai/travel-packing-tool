// Backend API: local when served from localhost, otherwise deployed (Render)
const API_BASE_URL =
    (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
        ? 'http://127.0.0.1:8000'
        : 'https://travel-packing-tool-backend.onrender.com';

// Trip data storage
let tripData = {
    destination: '',
    tripType: '',
    travellingWith: [],
    season: ''
};

// Checklist data structure: just 3 lists. Content comes from backend (or hardcoded default for now).
let checklistData = {
    pack: [],
    buy: [],
    do: []
};

// Collapsed state for "X completed items" block per section (default: collapsed).
let completedBlockExpanded = { pack: false, buy: false, do: false };

// Hardcoded default checklist until backend exists. When backend is ready, replace loadChecklist()
// to call API with tripData and set checklistData from response: { pack, buy, do }.
function getDefaultChecklist() {
    return {
        pack: [
            'Passport', 'Clothes', 'Toiletries', 'Phone charger', 'Documents',
            'Travel adapter', 'First aid kit', 'Comfortable shoes'
        ].map(text => ({ text, completed: false })),
        buy: [
            'Travel adapter', 'Sunscreen', 'Travel guide', 'Snacks'
        ].map(text => ({ text, completed: false })),
        do: [
            'Book flights', 'Reserve hotel', 'Check passport expiry', 'Get travel insurance'
        ].map(text => ({ text, completed: false }))
    };
}

// Load the 3 lists from backend API; on error fall back to hardcoded list.
async function loadChecklist() {
    const loadingEl = document.getElementById('checklistLoading');
    if (loadingEl) loadingEl.style.display = 'block';

    try {
        const res = await fetch(`${API_BASE_URL}/api/generate-checklist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                destination: tripData.destination,
                tripType: tripData.tripType,
                travellingWith: tripData.travellingWith,
                season: tripData.season
            })
        });
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data = await res.json();
        checklistData.pack = data.pack || [];
        checklistData.buy = data.buy || [];
        checklistData.do = data.do || [];
        console.log('Checklist loaded from backend: pack:', checklistData.pack.length, 'buy:', checklistData.buy.length, 'do:', checklistData.do.length);
    } catch (e) {
        console.warn('Backend not available, using default checklist:', e.message);
        const defaultChecklist = getDefaultChecklist();
        checklistData.pack = defaultChecklist.pack.map(item => ({ ...item }));
        checklistData.buy = defaultChecklist.buy.map(item => ({ ...item }));
        checklistData.do = defaultChecklist.do.map(item => ({ ...item }));
    }
    renderSection('pack');
    renderSection('buy');
    renderSection('do');

    if (loadingEl) loadingEl.style.display = 'none';
}

// --- Theme (dark / light): default dark, persist in same blob as checklist ---
function initTheme() {
    let theme = null;
    const blob = localStorage.getItem('travelPackingList');
    if (blob) {
        try {
            const data = JSON.parse(blob);
            if (data.theme === 'light' || data.theme === 'dark') theme = data.theme;
        } catch (_) {}
    }
    if (!theme) {
        const standalone = localStorage.getItem('theme');
        if (standalone === 'light' || standalone === 'dark') theme = standalone;
    }
    document.documentElement.setAttribute('data-theme', theme || 'dark');
    updateThemeToggleUI();
}

function updateThemeToggleUI() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const toggles = document.querySelectorAll('.theme-toggle-switch');
    toggles.forEach((el) => {
        el.setAttribute('aria-checked', isDark ? 'true' : 'false');
        el.setAttribute('title', isDark ? 'Dark mode' : 'Light mode');
    });
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeToggleUI();
    saveData();
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    document.querySelectorAll('.theme-toggle-switch').forEach((btn) => {
        btn.addEventListener('click', toggleTheme);
    });

    const tripForm = document.getElementById('tripForm');
    tripForm.addEventListener('submit', handleTripSubmit);

    const restartBtn = document.getElementById('restartBtn');
    restartBtn.addEventListener('click', showRestartModal);
    const restartBtnBottom = document.getElementById('restartBtnBottom');
    restartBtnBottom.addEventListener('click', showRestartModal);

    document.getElementById('restartModalNo').addEventListener('click', hideRestartModal);
    document.getElementById('restartModalYes').addEventListener('click', confirmRestart);
    document.getElementById('congratsModalOk').addEventListener('click', hideCongratsModal);

    // Single delegated listener for parent checkboxes (avoids duplicates after Restart)
    document.getElementById('checklistContainer').addEventListener('change', (e) => {
        if (e.target.classList.contains('parent-checkbox')) {
            const id = e.target.id;
            const sectionName = id.replace('-parent', '');
            if (sectionName && ['pack', 'buy', 'do'].includes(sectionName)) {
                toggleAllItems(sectionName, e.target.checked);
            }
        }
    });

    // Delegated listener for add-item row (always-visible "+ List item" that expands to input)
    document.getElementById('checklistContainer').addEventListener('click', (e) => {
        const row = e.target.closest('.add-item-row');
        if (!row || row.classList.contains('is-editing')) return;
        e.preventDefault();
        const sectionName = row.getAttribute('data-section');
        if (sectionName && ['pack', 'buy', 'do'].includes(sectionName)) {
            showAddItemInputInRow(row, sectionName);
        }
    });

    document.getElementById('checklistContainer').addEventListener('keydown', (e) => {
        const row = e.target.closest('.add-item-row');
        if (!row) return;
        const sectionName = row.getAttribute('data-section');

        if (row.classList.contains('is-editing')) {
            const input = row.querySelector('input.add-item-input');
            if (!input) return;
            if (e.key === 'Enter') {
                e.preventDefault();
                finishAddItemInRow(row, input, sectionName);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                restoreAddItemRow(row);
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (sectionName && ['pack', 'buy', 'do'].includes(sectionName)) {
                showAddItemInputInRow(row, sectionName);
            }
        }
    });

    loadSavedData();
});

// --- Restart flow ---
function showRestartModal() {
    document.getElementById('restartModal').style.display = 'flex';
}

function hideRestartModal() {
    document.getElementById('restartModal').style.display = 'none';
}

// Clear the checklist list DOM and completed blocks (e.g. after Restart or while loading).
function clearChecklistDOM() {
    ['pack', 'buy', 'do'].forEach(section => {
        const listEl = document.getElementById(`${section}-items`);
        if (listEl) listEl.innerHTML = '';
        const completedEl = document.getElementById(`${section}-completed`);
        if (completedEl) completedEl.innerHTML = '';
    });
}

function confirmRestart() {
    hideRestartModal();
    tripData.destination = '';
    tripData.tripType = '';
    tripData.travellingWith = [];
    tripData.season = '';
    checklistData.pack = [];
    checklistData.buy = [];
    checklistData.do = [];
    completedBlockExpanded = { pack: false, buy: false, do: false };
    clearChecklistDOM();
    document.getElementById('tripForm').reset();
    document.querySelector('.trip-details').style.display = 'block';
    document.getElementById('checklistContainer').style.display = 'none';
    saveData();
}

// --- Congrats modal (all items done) ---
function showCongratsModal() {
    document.getElementById('congratsModal').style.display = 'flex';
}

function hideCongratsModal() {
    document.getElementById('congratsModal').style.display = 'none';
}

function checkAllItemsCompleted() {
    const total = checklistData.pack.length + checklistData.buy.length + checklistData.do.length;
    if (total === 0) return false;
    const completed = checklistData.pack.filter(i => i.completed).length
        + checklistData.buy.filter(i => i.completed).length
        + checklistData.do.filter(i => i.completed).length;
    return completed === total;
}

// --- Form submission ---
function handleTripSubmit(e) {
    e.preventDefault();

    tripData.destination = document.getElementById('destination').value.trim();
    tripData.tripType = document.getElementById('tripType').value;
    tripData.travellingWith = Array.from(document.querySelectorAll('input[name="travellingWith"]:checked')).map(cb => cb.value);
    tripData.season = document.getElementById('season').value;

    const summaryParts = [tripData.destination, tripData.tripType, tripData.season];
    if (tripData.travellingWith.length > 0) {
        summaryParts.splice(2, 0, tripData.travellingWith.join(', '));
    }
    const tripSummary = document.getElementById('tripSummary');
    tripSummary.textContent = summaryParts.join(' • ');

    document.querySelector('.trip-details').style.display = 'none';
    document.getElementById('checklistContainer').style.display = 'block';
    clearChecklistDOM();
    loadChecklist().then(() => saveData());
}

// Render a checklist section: active items in the main list, completed in collapsible block.
function renderSection(sectionName) {
    const items = checklistData[sectionName];
    const activeItems = items.map((item, index) => ({ item, index })).filter(({ item }) => !item.completed);
    const completedItems = items.map((item, index) => ({ item, index })).filter(({ item }) => item.completed);

    const itemsList = document.getElementById(`${sectionName}-items`);
    itemsList.innerHTML = '';
    activeItems.forEach(({ item, index }) => {
        const li = createChecklistItem(sectionName, index, item.text, false);
        itemsList.appendChild(li);
    });

    renderCompletedBlock(sectionName, completedItems);
    updateParentCheckbox(sectionName);
}

// Render the "X completed items" collapsible block for a section.
function renderCompletedBlock(sectionName, completedItems) {
    const blockEl = document.getElementById(`${sectionName}-completed`);
    if (!blockEl) return;

    blockEl.innerHTML = '';
    const count = completedItems.length;
    if (count === 0) {
        blockEl.classList.add('collapsed', 'is-empty');
        return;
    }

    blockEl.classList.remove('is-empty');
    const isExpanded = completedBlockExpanded[sectionName];
    if (!isExpanded) blockEl.classList.add('collapsed');
    else blockEl.classList.remove('collapsed');

    const header = document.createElement('div');
    header.className = 'completed-block-header';
    header.setAttribute('role', 'button');
    header.setAttribute('tabindex', '0');
    header.setAttribute('aria-expanded', isExpanded);
    header.innerHTML = `<span class="chevron" aria-hidden="true">▼</span><span>${count} completed item${count === 1 ? '' : 's'}</span>`;
    header.addEventListener('click', () => {
        completedBlockExpanded[sectionName] = !completedBlockExpanded[sectionName];
        blockEl.classList.toggle('collapsed', !completedBlockExpanded[sectionName]);
        header.setAttribute('aria-expanded', completedBlockExpanded[sectionName]);
    });
    blockEl.appendChild(header);

    const list = document.createElement('ul');
    list.className = 'completed-block-list';
    completedItems.forEach(({ item, index }) => {
        const li = createChecklistItem(sectionName, index, item.text, true);
        list.appendChild(li);
    });
    blockEl.appendChild(list);
}

// Create a single checklist item element
function createChecklistItem(sectionName, index, text, completed) {
    const li = document.createElement('li');
    li.className = `checklist-item ${completed ? 'completed' : ''}`;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = completed;
    checkbox.addEventListener('change', () => {
        toggleItem(sectionName, index);
    });

    const label = document.createElement('span');
    label.className = 'item-label';
    label.textContent = text;

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'item-delete';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', () => {
        deleteItem(sectionName, index);
    });

    li.appendChild(checkbox);
    li.appendChild(label);
    li.appendChild(deleteBtn);

    return li;
}

// Toggle item completion
function toggleItem(sectionName, index) {
    checklistData[sectionName][index].completed = !checklistData[sectionName][index].completed;
    renderSection(sectionName);
    saveData();
    if (checkAllItemsCompleted()) showCongratsModal();
}

// Delete an item
function deleteItem(sectionName, index) {
    checklistData[sectionName].splice(index, 1);
    renderSection(sectionName);
    saveData();
}

// Update parent checkbox based on child items
function updateParentCheckbox(sectionName) {
    const parentCheckbox = document.getElementById(`${sectionName}-parent`);
    const items = checklistData[sectionName];

    if (items.length === 0) {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = false;
        return;
    }

    const completedCount = items.filter(item => item.completed).length;

    if (completedCount === 0) {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = false;
    } else if (completedCount === items.length) {
        parentCheckbox.checked = true;
        parentCheckbox.indeterminate = false;
    } else {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = true;
    }
}

// Toggle all items in a section
function toggleAllItems(sectionName, checked) {
    checklistData[sectionName].forEach(item => {
        item.completed = checked;
    });
    renderSection(sectionName);
    saveData();
    if (checkAllItemsCompleted()) showCongratsModal();
}

// Show input inside the add-item row (Keep-style: row expands to input).
function showAddItemInputInRow(row, sectionName) {
    if (row.classList.contains('is-editing')) return;
    row.classList.add('is-editing');

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'add-item-input';
    input.placeholder = 'List item';
    input.setAttribute('aria-label', 'New item');

    input.addEventListener('blur', () => {
        finishAddItemInRow(row, input, sectionName);
    });

    row.appendChild(input);
    input.focus();
}

function finishAddItemInRow(row, input, sectionName) {
    if (!row.contains(input)) return; // avoid double-run from blur + Enter
    const value = input.value.trim();
    if (value) {
        addNewItem(sectionName, value);
    }
    restoreAddItemRow(row);
}

function restoreAddItemRow(row) {
    const input = row.querySelector('input.add-item-input');
    if (input) input.remove();
    row.classList.remove('is-editing');
    // Restore placeholder if it was removed (e.g. by innerHTML elsewhere)
    if (!row.querySelector('.add-item-text')) {
        const icon = document.createElement('span');
        icon.className = 'add-item-icon';
        icon.textContent = '+';
        const text = document.createElement('span');
        text.className = 'add-item-text';
        text.textContent = 'List item';
        row.appendChild(icon);
        row.appendChild(text);
    }
}

// Add a new item to a section
function addNewItem(sectionName, text) {
    checklistData[sectionName].push({ text: text, completed: false });
    renderSection(sectionName);
    saveData();
}

// Save data to localStorage (trip, checklist, and theme – same blob for persistence)
function saveData() {
    const dataToSave = {
        tripData: tripData,
        checklistData: checklistData,
        theme: document.documentElement.getAttribute('data-theme')
    };
    localStorage.setItem('travelPackingList', JSON.stringify(dataToSave));
}

// Load saved data from localStorage
function loadSavedData() {
    // Prevent initial "flash" of the form before we decide what to show.
    // index.html starts with both sections hidden; we show the right one here.
    const saved = localStorage.getItem('travelPackingList');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            tripData = data.tripData || tripData;
            checklistData = data.checklistData || checklistData;
            if (data.theme === 'light' || data.theme === 'dark') {
                document.documentElement.setAttribute('data-theme', data.theme);
                updateThemeToggleUI();
            }

            if (!tripData.travellingWith) tripData.travellingWith = [];
            if (!tripData.season) tripData.season = '';

            if (tripData.destination) {
                document.getElementById('destination').value = tripData.destination;
                document.getElementById('tripType').value = tripData.tripType || '';
                document.getElementById('season').value = tripData.season || '';
                const whoInputs = document.querySelectorAll('input[name="travellingWith"]');
                whoInputs.forEach(inp => {
                    inp.checked = (tripData.travellingWith || []).includes(inp.value);
                });

                const summaryParts = [tripData.destination, tripData.tripType, tripData.season];
                if ((tripData.travellingWith || []).length > 0) {
                    summaryParts.splice(2, 0, tripData.travellingWith.join(', '));
                }
                document.getElementById('tripSummary').textContent = summaryParts.join(' • ');

                document.querySelector('.trip-details').style.display = 'none';
                document.getElementById('checklistContainer').style.display = 'block';

                renderSection('pack');
                renderSection('buy');
                renderSection('do');
                return;
            }
        } catch (e) {
            console.error('Error loading saved data:', e);
        }
    }

    // No saved trip (or failed to load) → show the form.
    document.querySelector('.trip-details').style.display = 'block';
    document.getElementById('checklistContainer').style.display = 'none';
}
