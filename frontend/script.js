// Trip data storage
let tripData = {
    destination: '',
    tripType: '',
    travellingWith: [],
    season: ''
};

// Checklist data structure
let checklistData = {
    pack: [],
    buy: [],
    do: []
};

// Default items: each dimension adds items. Final list = merge + dedupe.
// Keys: tripType (trek, leisure, work, backpacking), travellingWith (solo, withParents, couple, withKids, withFriends), season (summer, winter, autumn, spring)
const defaultItems = {
    pack: {
        byTripType: {
            trek: ['Hiking boots', 'Backpack', 'First aid kit', 'Water bottle', 'Map', 'Energy bars'],
            leisure: ['Passport', 'Clothes', 'Toiletries', 'Phone charger', 'Camera', 'Sunscreen'],
            work: ['Laptop', 'Business cards', 'Formal clothes', 'Documents', 'Phone charger'],
            backpacking: ['Backpack', 'First aid kit', 'Water bottle', 'Quick-dry clothes', 'Headlamp']
        },
        byTravellingWith: {
            solo: ['Portable charger', 'Travel adapter'],
            withParents: ['Comfortable shoes', 'Medications list'],
            couple: ['Camera', 'Travel adapter'],
            withKids: ['Diapers', 'Baby clothes', 'Toys', 'Snacks', 'Stroller', 'Baby wipes'],
            withFriends: ['Portable speaker', 'Games', 'Snacks']
        },
        bySeason: {
            summer: ['Sunscreen', 'Hat', 'Light clothes', 'Sandals'],
            winter: ['Warm jacket', 'Gloves', 'Scarf', 'Thermal layers'],
            autumn: ['Layers', 'Rain jacket', 'Closed shoes'],
            spring: ['Light jacket', 'Layers', 'Comfortable shoes']
        }
    },
    buy: {
        byTripType: {
            trek: ['Energy bars', 'Compass', 'Flashlight', 'Trekking poles'],
            leisure: ['Travel adapter', 'Sunscreen', 'Travel guide', 'Snacks'],
            work: ['Travel adapter', 'Notebook', 'Pens'],
            backpacking: ['Energy bars', 'Dry bags', 'Trekking poles']
        },
        byTravellingWith: {
            solo: ['Travel guide'],
            withParents: ['Comfort items'],
            couple: ['Travel guide'],
            withKids: ['Baby food', 'Diapers', 'Wipes', 'Snacks'],
            withFriends: ['Snacks', 'Games']
        },
        bySeason: {
            summer: ['Sunscreen', 'Insect repellent'],
            winter: ['Hand warmers', 'Lip balm'],
            autumn: ['Umbrella', 'Rain cover'],
            spring: ['Allergy meds', 'Sunscreen']
        }
    },
    do: {
        byTripType: {
            trek: ['Plan route', 'Check weather', 'Inform emergency contact', 'Pack first aid', 'Book permits'],
            leisure: ['Book flights', 'Reserve hotel', 'Check passport expiry', 'Get travel insurance'],
            work: ['Book flights', 'Schedule meetings', 'Prepare presentation', 'Check visa requirements'],
            backpacking: ['Plan route', 'Check weather', 'Book hostels', 'Check visa']
        },
        byTravellingWith: {
            solo: ['Share itinerary with someone'],
            withParents: ['Check accessibility', 'Book direct flights'],
            couple: ['Book flights', 'Reserve hotel'],
            withKids: ['Book family-friendly hotel', 'Plan activities', 'Check vaccinations', 'Pack baby essentials'],
            withFriends: ['Coordinate dates', 'Book accommodation']
        },
        bySeason: {
            summer: ['Check heat advisories', 'Book AC accommodation'],
            winter: ['Check road conditions', 'Pack winter gear'],
            autumn: ['Check fall foliage timing'],
            spring: ['Check allergy season', 'Pack layers']
        }
    }
};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    const tripForm = document.getElementById('tripForm');
    tripForm.addEventListener('submit', handleTripSubmit);

    const restartBtn = document.getElementById('restartBtn');
    restartBtn.addEventListener('click', showRestartModal);

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

    loadSavedData();
});

// --- Restart flow ---
function showRestartModal() {
    document.getElementById('restartModal').style.display = 'flex';
}

function hideRestartModal() {
    document.getElementById('restartModal').style.display = 'none';
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

    generateInitialChecklist();
    saveData();
}

// Merge arrays and dedupe by string (case-insensitive, trim)
function mergeAndDedupe(arrays) {
    const seen = new Set();
    const out = [];
    for (const arr of arrays) {
        for (const s of arr) {
            const key = String(s).trim().toLowerCase();
            if (key && !seen.has(key)) {
                seen.add(key);
                out.push(String(s).trim());
            }
        }
    }
    return out;
}

// Generate checklist from trip type + travelling with + season
function generateInitialChecklist() {
    const tt = tripData.tripType || 'leisure';
    const tw = tripData.travellingWith || [];
    const sea = tripData.season || 'summer';

    const packArrays = [
        defaultItems.pack.byTripType[tt] || [],
        ...tw.map(w => defaultItems.pack.byTravellingWith[w] || []),
        defaultItems.pack.bySeason[sea] || []
    ];
    const buyArrays = [
        defaultItems.buy.byTripType[tt] || [],
        ...tw.map(w => defaultItems.buy.byTravellingWith[w] || []),
        defaultItems.buy.bySeason[sea] || []
    ];
    const doArrays = [
        defaultItems.do.byTripType[tt] || [],
        ...tw.map(w => defaultItems.do.byTravellingWith[w] || []),
        defaultItems.do.bySeason[sea] || []
    ];

    checklistData.pack = mergeAndDedupe(packArrays).map(text => ({ text, completed: false }));
    checklistData.buy = mergeAndDedupe(buyArrays).map(text => ({ text, completed: false }));
    checklistData.do = mergeAndDedupe(doArrays).map(text => ({ text, completed: false }));

    renderSection('pack');
    renderSection('buy');
    renderSection('do');
    setupAddItemListeners();
}

// Render a checklist section
function renderSection(sectionName) {
    const itemsList = document.getElementById(`${sectionName}-items`);
    itemsList.innerHTML = '';

    checklistData[sectionName].forEach((item, index) => {
        const li = createChecklistItem(sectionName, index, item.text, item.completed);
        itemsList.appendChild(li);
    });

    updateParentCheckbox(sectionName);
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

// Set up add item button listeners
function setupAddItemListeners() {
    document.querySelectorAll('.add-item-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const sectionName = btn.getAttribute('data-section');
            showAddItemInput(sectionName, btn);
        });
    });
}

// Show input field for adding new item
function showAddItemInput(sectionName, button) {
    const existingInput = document.querySelector(`.new-item-input[data-section="${sectionName}"]`);
    if (existingInput) {
        existingInput.remove();
        return;
    }

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'new-item-input';
    input.setAttribute('data-section', sectionName);
    input.placeholder = 'Enter item name...';

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && input.value.trim()) {
            addNewItem(sectionName, input.value.trim());
            input.remove();
        } else if (e.key === 'Escape') {
            input.remove();
        }
    });

    input.addEventListener('blur', () => {
        if (input.value.trim()) {
            addNewItem(sectionName, input.value.trim());
        }
        input.remove();
    });

    button.parentElement.insertBefore(input, button);
    input.focus();
}

// Add a new item to a section
function addNewItem(sectionName, text) {
    checklistData[sectionName].push({ text: text, completed: false });
    renderSection(sectionName);
    saveData();
}

// Save data to localStorage
function saveData() {
    const dataToSave = {
        tripData: tripData,
        checklistData: checklistData
    };
    localStorage.setItem('travelPackingList', JSON.stringify(dataToSave));
}

// Load saved data from localStorage
function loadSavedData() {
    const saved = localStorage.getItem('travelPackingList');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            tripData = data.tripData || tripData;
            checklistData = data.checklistData || checklistData;

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
                setupAddItemListeners();
            }
        } catch (e) {
            console.error('Error loading saved data:', e);
        }
    }
}
