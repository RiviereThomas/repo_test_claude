// Configuration de l'API - Utilise l'host actuel
const API_BASE_URL = `${window.location.origin}/api`;

// État de l'application
const state = {
    allData: [],
    filteredData: [],
    versions: [],
    currentEditField: null,
    currentMode: '1' // '1' = valeur fixe, '0' = valeur calculée
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
    const modeFilter = document.getElementById('mode-filter');
    const versionFilter = document.getElementById('version-filter');
    const searchField = document.getElementById('search-field');
    const resetBtn = document.getElementById('reset-filters-btn');
    const closeModal = document.getElementById('close-modal');
    const cancelEdit = document.getElementById('cancel-edit');
    const saveEdit = document.getElementById('save-edit');

    modeFilter.addEventListener('change', () => {
        state.currentMode = modeFilter.value;
        loadFields();
    });
    versionFilter.addEventListener('change', loadFields);
    searchField.addEventListener('input', debounce(applyFilters, 300));
    resetBtn.addEventListener('click', resetFilters);
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

        // Filtrer selon le mode sélectionné
        state.allData = data.filter(item => item.is_fixed_value === state.currentMode);
        state.filteredData = [...state.allData];

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

// Déterminer si un champ est modifiable selon sa source
function isFieldEditable(item) {
    if (item.is_fixed_value === '1') {
        return true; // Toujours modifiable en mode valeur fixe
    }

    // En mode valeur calculée (0), vérifier la source
    const source = (item.value_source || '').toLowerCase();

    // Non modifiable si source commence par "table ref_funds" ou "table ref_funds_parts"
    if (source.startsWith('table ref_funds') || source.startsWith('table ref_funds_parts')) {
        return false;
    }

    return true;
}

// Obtenir le tooltip approprié selon la source
function getSourceTooltip(item) {
    if (item.is_fixed_value === '1') {
        return 'Cliquer pour soumettre une validation';
    }

    const source = (item.value_source || '').toLowerCase();

    // Non modifiable
    if (source.startsWith('table ref_funds') || source.startsWith('table ref_funds_parts')) {
        return 'Passer par l\'IT ou l\'application existante pour modifier les référentiels des fonds';
    }

    // Modifiable - vérifier le type
    if (source.startsWith('table tb_eet_data')) {
        return 'La modification sera appliquée aux portefeuilles sélectionnés - Cliquer pour soumettre une validation';
    }

    // Autre source modifiable
    return 'La modification sera appliquée à tous les portefeuilles - Cliquer pour soumettre une validation';
}

// Rendu du tableau
function renderTable() {
    const tbody = document.getElementById('table-body');

    if (state.filteredData.length === 0) {
        const modeText = state.currentMode === '1' ? 'valeur fixe' : 'valeur calculée';
        tbody.innerHTML = `<tr><td colspan="6" class="no-data">Aucun champ avec ${modeText} trouvé</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    state.filteredData.forEach(item => {
        const row = document.createElement('tr');
        const editable = isFieldEditable(item);
        const tooltip = getSourceTooltip(item);

        if (editable) {
            row.classList.add('editable-row');
        } else {
            row.classList.add('non-editable-row');
        }

        row.setAttribute('title', tooltip);
        row.setAttribute('data-field', item.field_name);

        // Créer le tooltip pour Valeur Fixe
        const fixedValueTooltip = item.is_fixed_value === '1'
            ? 'Valeur Fixe = 1 : Le fichier prendra la valeur brute de la colonne source'
            : 'Valeur Fixe = 0 : Le fichier prendra la valeur recalculée de la colonne source';

        row.innerHTML = `
            <td>${item.version || ''}</td>
            <td class="field-name"><strong>${item.field_name || ''}</strong></td>
            <td class="centered" title="${fixedValueTooltip}">${item.is_fixed_value || ''}</td>
            <td class="editable-cell" title="${item.value_source || ''}">${truncateText(item.value_source || '', 40)}</td>
            <td class="centered editable-cell">${item.is_filed_in || ''}</td>
            <td class="centered">${editable ? '' : '🔒'}</td>
        `;

        tbody.appendChild(row);
    });

    // Ajouter les event listeners seulement sur les lignes modifiables
    document.querySelectorAll('.editable-row').forEach(row => {
        row.addEventListener('click', (e) => {
            const fieldName = row.dataset.field;
            openEditModal(fieldName);
        });
    });
}

// Ouvrir le modal d'édition
function openEditModal(fieldName) {
    const item = state.allData.find(i => i.field_name === fieldName);
    if (!item) return;

    state.currentEditField = item;

    document.getElementById('modal-field-name').value = item.field_name || '';
    document.getElementById('modal-is-fixed-value').value = item.is_fixed_value || '1';
    document.getElementById('modal-value-source').value = item.value_source || '';
    document.getElementById('modal-is-filed-in').value = item.is_filed_in || '';

    document.getElementById('edit-modal').style.display = 'flex';
}

// Fermer le modal
function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
    state.currentEditField = null;
}

// Sauvegarder les modifications du champ
async function saveFieldEdit() {
    if (!state.currentEditField) return;

    const newData = {
        is_fixed_value: document.getElementById('modal-is-fixed-value').value,
        value_source: document.getElementById('modal-value-source').value,
        is_filed_in: document.getElementById('modal-is-filed-in').value
    };

    // Vérifier si les données ont changé
    const hasChanged =
        newData.is_fixed_value !== state.currentEditField.is_fixed_value ||
        newData.value_source !== state.currentEditField.value_source ||
        newData.is_filed_in !== state.currentEditField.is_filed_in;

    if (!hasChanged) {
        closeEditModal();
        return;
    }

    try {
        showLoading(true);

        // Soumettre directement la demande de validation
        const response = await fetch(`${API_BASE_URL}/validation-requests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                operation_type: 'UPDATE',
                table_name: 'tb_eet_fields',
                data_json: newData,
                where_clause_json: {
                    version: state.currentEditField.version,
                    field_name: state.currentEditField.field_name
                },
                creation_reason: 'Modification via interface admin_reporting',
                status: 'PENDING'
            })
        });

        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        showSuccess('Demande de validation créée avec succès !');
        closeEditModal();

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
