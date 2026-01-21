// Configuration de l'API - Utilise l'host actuel
const API_BASE_URL = `${window.location.origin}/api`;

// État de l'application
const state = {
    allData: [],
    filteredData: [],
    versions: [],
    modifications: new Map(), // Map<field_name, {old: {...}, new: {...}}>
    currentEditField: null
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    await loadVersions();
}

function setupEventListeners() {
    const versionFilter = document.getElementById('version-filter');
    const searchField = document.getElementById('search-field');
    const resetBtn = document.getElementById('reset-filters-btn');
    const saveBtn = document.getElementById('save-btn');
    const closeModal = document.getElementById('close-modal');
    const cancelEdit = document.getElementById('cancel-edit');
    const saveEdit = document.getElementById('save-edit');

    versionFilter.addEventListener('change', loadFields);
    searchField.addEventListener('input', debounce(applyFilters, 300));
    resetBtn.addEventListener('click', resetFilters);
    saveBtn.addEventListener('click', submitModifications);
    closeModal.addEventListener('click', closeEditModal);
    cancelEdit.addEventListener('click', closeEditModal);
    saveEdit.addEventListener('click', saveFieldEdit);
}

// Chargement des versions
async function loadVersions() {
    try {
        const response = await fetch(`${API_BASE_URL}/eet-versions`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();
        state.versions = data.versions;
        populateVersionsFilter();
    } catch (error) {
        showError(`Erreur lors du chargement des versions: ${error.message}`);
    }
}

function populateVersionsFilter() {
    const select = document.getElementById('version-filter');
    select.innerHTML = '<option value="">Sélectionner une version...</option>';

    state.versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        select.appendChild(option);
    });

    // Sélectionner la première version par défaut
    if (state.versions.length > 0) {
        select.value = state.versions[0];
        loadFields();
    }
}

// Chargement des champs avec is_fixed_value = '1'
async function loadFields() {
    const version = document.getElementById('version-filter').value;
    if (!version) return;

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/eet-fields?version=${version}`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();

        // Filtrer seulement les champs avec is_fixed_value = '1'
        state.allData = data.filter(item => item.is_fixed_value === '1');
        state.filteredData = [...state.allData];

        // Réinitialiser les modifications
        state.modifications.clear();
        updateSaveButton();

        renderTable();
        updateRowCount();
        showLoading(false);
    } catch (error) {
        showError(`Erreur lors du chargement des champs: ${error.message}`);
        showLoading(false);
    }
}

// Application des filtres
function applyFilters() {
    const searchTerm = document.getElementById('search-field').value.toLowerCase();

    state.filteredData = state.allData.filter(item => {
        if (searchTerm && !item.field_name?.toLowerCase().includes(searchTerm)) return false;
        return true;
    });

    renderTable();
    updateRowCount();
}

// Réinitialisation des filtres
function resetFilters() {
    document.getElementById('search-field').value = '';
    state.filteredData = [...state.allData];
    renderTable();
    updateRowCount();
}

// Rendu du tableau
function renderTable() {
    const tbody = document.getElementById('table-body');

    if (state.filteredData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">Aucun champ avec valeur fixe trouvé</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    state.filteredData.forEach(item => {
        const hasModification = state.modifications.has(item.field_name);
        const modifiedData = hasModification ? state.modifications.get(item.field_name).new : item;

        const row = document.createElement('tr');
        if (hasModification) {
            row.classList.add('modified-row');
        }

        row.innerHTML = `
            <td>${item.version || ''}</td>
            <td class="field-name"><strong>${item.field_name || ''}</strong></td>
            <td class="centered">${modifiedData.is_fixed_value || ''}</td>
            <td class="editable-cell" title="${modifiedData.value_source || ''}">${truncateText(modifiedData.value_source || '', 40)}</td>
            <td class="centered editable-cell">${modifiedData.is_filed_in || ''}</td>
            <td class="centered">
                <button class="btn-edit" data-field="${item.field_name}">✏️ Modifier</button>
                ${hasModification ? '<button class="btn-undo" data-field="' + item.field_name + '">↶ Annuler</button>' : ''}
            </td>
        `;

        tbody.appendChild(row);
    });

    // Ajouter les event listeners
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fieldName = e.target.dataset.field;
            openEditModal(fieldName);
        });
    });

    document.querySelectorAll('.btn-undo').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fieldName = e.target.dataset.field;
            undoModification(fieldName);
        });
    });
}

// Ouvrir le modal d'édition
function openEditModal(fieldName) {
    const item = state.allData.find(i => i.field_name === fieldName);
    if (!item) return;

    const currentData = state.modifications.has(fieldName)
        ? state.modifications.get(fieldName).new
        : item;

    state.currentEditField = item;

    document.getElementById('modal-field-name').value = item.field_name;
    document.getElementById('modal-is-fixed-value').value = currentData.is_fixed_value || '0';
    document.getElementById('modal-value-source').value = currentData.value_source || '';
    document.getElementById('modal-is-filed-in').value = currentData.is_filed_in || '';

    document.getElementById('edit-modal').style.display = 'flex';
}

// Fermer le modal
function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
    state.currentEditField = null;
}

// Sauvegarder les modifications du champ
function saveFieldEdit() {
    if (!state.currentEditField) return;

    const newData = {
        version: state.currentEditField.version,
        field_name: state.currentEditField.field_name,
        is_fixed_value: document.getElementById('modal-is-fixed-value').value,
        value_source: document.getElementById('modal-value-source').value,
        is_filed_in: document.getElementById('modal-is-filed-in').value
    };

    // Vérifier si les données ont changé
    const hasChanged =
        newData.is_fixed_value !== state.currentEditField.is_fixed_value ||
        newData.value_source !== state.currentEditField.value_source ||
        newData.is_filed_in !== state.currentEditField.is_filed_in;

    if (hasChanged) {
        state.modifications.set(state.currentEditField.field_name, {
            old: {...state.currentEditField},
            new: newData
        });
    } else {
        // Si les modifications sont annulées, retirer de la map
        state.modifications.delete(state.currentEditField.field_name);
    }

    updateSaveButton();
    renderTable();
    closeEditModal();
}

// Annuler une modification
function undoModification(fieldName) {
    state.modifications.delete(fieldName);
    updateSaveButton();
    renderTable();
}

// Mettre à jour le bouton de sauvegarde
function updateSaveButton() {
    const saveBtn = document.getElementById('save-btn');
    const count = state.modifications.size;

    if (count > 0) {
        saveBtn.disabled = false;
        saveBtn.textContent = `💾 Soumettre ${count} modification(s)`;
    } else {
        saveBtn.disabled = true;
        saveBtn.textContent = '💾 Soumettre les modifications';
    }
}

// Soumettre les modifications
async function submitModifications() {
    if (state.modifications.size === 0) return;

    const modifications = Array.from(state.modifications.values());

    try {
        showLoading(true);

        // Soumettre chaque modification comme une demande de validation
        const promises = modifications.map(mod => {
            return fetch(`${API_BASE_URL}/validation-requests`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    operation_type: 'UPDATE',
                    table_name: 'tb_eet_fields',
                    data_json: {
                        is_fixed_value: mod.new.is_fixed_value,
                        value_source: mod.new.value_source,
                        is_filed_in: mod.new.is_filed_in
                    },
                    where_clause_json: {
                        version: mod.new.version,
                        field_name: mod.new.field_name
                    },
                    creation_reason: 'Modification via interface admin_reporting',
                    status: 'PENDING'
                })
            });
        });

        await Promise.all(promises);

        showSuccess(`${modifications.length} demande(s) de validation créée(s) avec succès !`);

        // Réinitialiser les modifications
        state.modifications.clear();
        updateSaveButton();

        // Recharger les données
        await loadFields();

        showLoading(false);
    } catch (error) {
        showError(`Erreur lors de la soumission: ${error.message}`);
        showLoading(false);
    }
}

// Mise à jour du compteur
function updateRowCount() {
    const rowCount = document.getElementById('row-count');
    const count = state.filteredData.length;
    rowCount.textContent = `${count} champ${count > 1 ? 's' : ''}`;
}

// Utilitaires
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 5000);
}
