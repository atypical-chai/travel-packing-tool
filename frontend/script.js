// Trip data storage
let tripData = {
    destination: '',
    tripType: '',
    duration: 0
};

// Checklist data structure
let checklistData = {
    pack: [],
    buy: [],
    do: []
};

// Default items for each section (will be customized based on trip type)
const defaultItems = {
    pack: {
        vacation: ['Passport', 'Clothes', 'Toiletries', 'Phone charger', 'Camera'],
        business: ['Laptop', 'Business cards', 'Formal clothes', 'Documents', 'Phone charger'],
        adventure: ['Hiking boots', 'Backpack', 'First aid kit', 'Water bottle', 'Map'],
        family: ['Diapers', 'Baby clothes', 'Toys', 'Snacks', 'Stroller'],
        other: ['Essentials', 'Documents', 'Chargers', 'Clothes', 'Toiletries']
    },
    buy: {
        vacation: ['Travel adapter', 'Sunscreen', 'Travel guide', 'Snacks'],
        business: ['Travel adapter', 'Notebook', 'Pens'],
        adventure: ['Energy bars', 'Compass', 'Flashlight'],
        family: ['Baby food', 'Diapers', 'Wipes'],
        other: ['Travel essentials']
    },
    do: {
        vacation: ['Book flights', 'Reserve hotel', 'Check passport expiry', 'Get travel insurance'],
        business: ['Book flights', 'Schedule meetings', 'Prepare presentation', 'Check visa requirements'],
        adventure: ['Plan route', 'Check weather', 'Inform emergency contact', 'Pack first aid'],
        family: ['Book family-friendly hotel', 'Plan activities', 'Pack baby essentials', 'Check vaccinations'],
        other: ['Plan itinerary', 'Book accommodations', 'Check requirements']
    }
};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    const tripForm = document.getElementById('tripForm');
    tripForm.addEventListener('submit', handleTripSubmit);

    // Load saved data from localStorage if available
    loadSavedData();
});

// Handle trip form submission
function handleTripSubmit(e) {
    e.preventDefault();
    
    tripData.destination = document.getElementById('destination').value;
    tripData.tripType = document.getElementById('tripType').value;
    tripData.duration = parseInt(document.getElementById('duration').value);

    // Show trip summary
    const tripSummary = document.getElementById('tripSummary');
    tripSummary.textContent = `${tripData.destination} • ${tripData.tripType} • ${tripData.duration} days`;

    // Hide form and show checklist
    document.querySelector('.trip-details').style.display = 'none';
    document.getElementById('checklistContainer').style.display = 'block';

    // Generate initial checklist items
    generateInitialChecklist();

    // Save to localStorage
    saveData();
}

// Generate initial checklist based on trip type
function generateInitialChecklist() {
    const tripType = tripData.tripType || 'other';
    
    // Clear existing items
    checklistData.pack = [];
    checklistData.buy = [];
    checklistData.do = [];

    // Add default items for each section
    defaultItems.pack[tripType].forEach(item => {
        checklistData.pack.push({ text: item, completed: false });
    });

    defaultItems.buy[tripType].forEach(item => {
        checklistData.buy.push({ text: item, completed: false });
    });

    defaultItems.do[tripType].forEach(item => {
        checklistData.do.push({ text: item, completed: false });
    });

    // Render all sections
    renderSection('pack');
    renderSection('buy');
    renderSection('do');

    // Set up event listeners for add buttons
    setupAddItemListeners();
    setupParentCheckboxListeners();
}

// Render a checklist section
function renderSection(sectionName) {
    const itemsList = document.getElementById(`${sectionName}-items`);
    itemsList.innerHTML = '';

    checklistData[sectionName].forEach((item, index) => {
        const li = createChecklistItem(sectionName, index, item.text, item.completed);
        itemsList.appendChild(li);
    });

    // Update parent checkbox state
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
        parentCheckbox.indeterminate = true; // Some items completed
    }
}

// Handle parent checkbox click
function setupParentCheckboxListeners() {
    ['pack', 'buy', 'do'].forEach(sectionName => {
        const parentCheckbox = document.getElementById(`${sectionName}-parent`);
        parentCheckbox.addEventListener('change', () => {
            toggleAllItems(sectionName, parentCheckbox.checked);
        });
    });
}

// Toggle all items in a section
function toggleAllItems(sectionName, checked) {
    checklistData[sectionName].forEach(item => {
        item.completed = checked;
    });
    renderSection(sectionName);
    saveData();
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
    // Remove any existing input
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

            // If we have saved data, show the checklist
            if (tripData.destination) {
                document.getElementById('destination').value = tripData.destination;
                document.getElementById('tripType').value = tripData.tripType;
                document.getElementById('duration').value = tripData.duration;

                const tripSummary = document.getElementById('tripSummary');
                tripSummary.textContent = `${tripData.destination} • ${tripData.tripType} • ${tripData.duration} days`;

                document.querySelector('.trip-details').style.display = 'none';
                document.getElementById('checklistContainer').style.display = 'block';

                renderSection('pack');
                renderSection('buy');
                renderSection('do');
                setupAddItemListeners();
                setupParentCheckboxListeners();
            }
        } catch (e) {
            console.error('Error loading saved data:', e);
        }
    }
}
