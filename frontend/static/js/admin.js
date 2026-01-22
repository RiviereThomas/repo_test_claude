// Configuration de l'API - Utilise l'host actuel
const API_BASE_URL = `${window.location.origin}/api`;

// État de l'application
const state = {
    allData: [],
    filteredData: [],
    versions: [],
    currentEditField: null,
    currentMode: '', // '' = tous, '1' = valeur fixe, '0' = valeur calculée
    fundResults: null, // Résultats du calcul de fonds
    fundCalcVisible: false,
    sortColumn: null,
    sortOrder: 'asc' // 'asc' ou 'desc'
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    await loadVersions();
    await loadFunds();
    setupSortListeners();
}

function setupEventListeners() {
    const modeFilter = document.getElementById('mode-filter');
    const versionFilter = document.getElementById('version-filter');
    const searchField = document.getElementById('search-field');
    const resetBtn = document.getElementById('reset-filters-btn');
    const fundCalcToggleBtn = document.getElementById('fund-calc-toggle-btn');
    const calculateFundBtn = document.getElementById('calculate-fund-btn');
    const clearFundBtn = document.getElementById('clear-fund-btn');
    const closeModal = document.getElementById('close-modal');
    const cancelEdit = document.getElementById('cancel-edit');
    const saveEdit = document.getElementById('save-edit');

    // Synchroniser le select avec state.currentMode au démarrage
    modeFilter.value = state.currentMode;
    console.log('Mode initial:', state.currentMode);

    modeFilter.addEventListener('change', () => {
        state.currentMode = modeFilter.value;
        console.log('Mode changé vers:', state.currentMode || 'Tous');
        loadFields();
    });
    versionFilter.addEventListener('change', loadFields);
    searchField.addEventListener('input', debounce(applyFilters, 300));
    resetBtn.addEventListener('click', resetFilters);
    fundCalcToggleBtn.addEventListener('click', toggleFundCalcSection);
    calculateFundBtn.addEventListener('click', calculateFundResults);
    clearFundBtn.addEventListener('click', clearFundResults);
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

// Chargement des fonds
async function loadFunds() {
    try {
        const response = await fetch(`${API_BASE_URL}/funds`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const funds = await response.json();
        const select = document.getElementById('fund-select');
        select.innerHTML = '<option value="">Sélectionner un fonds...</option>';

        funds.forEach(fund => {
            const option = document.createElement('option');
            option.value = fund.Mnemo_Fund;
            option.textContent = `${fund.Mnemo_Fund} - ${fund.Lib_Fund}`;
            select.appendChild(option);
        });
    } catch (error) {
        showError(`Erreur lors du chargement des fonds: ${error.message}`);
    }
}

// Toggle la section de calcul fonds
function toggleFundCalcSection() {
    const section = document.getElementById('fund-calc-section');
    const btn = document.getElementById('fund-calc-toggle-btn');
    state.fundCalcVisible = !state.fundCalcVisible;

    if (state.fundCalcVisible) {
        section.style.display = 'block';
        btn.classList.add('active');
    } else {
        section.style.display = 'none';
        btn.classList.remove('active');
    }
}

// Calculer les résultats du fonds
async function calculateFundResults() {
    const fund = document.getElementById('fund-select').value;
    const dateInput = document.getElementById('calc-date').value;
    const version = document.getElementById('version-filter').value;

    if (!fund) {
        showError('Veuillez sélectionner un fonds');
        return;
    }

    if (!version) {
        showError('Veuillez sélectionner une version');
        return;
    }

    // Convertir la date au format français
    const [year, month, day] = dateInput.split('-');
    const dateCalcul = `${day}/${month}/${year}`;

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/fund-results/${fund}?version=${version}&date_calcul=${encodeURIComponent(dateCalcul)}`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();
        state.fundResults = data.results;

        // Afficher la colonne résultat
        document.getElementById('result-column-header').style.display = '';

        renderTable();
        showLoading(false);
        showSuccess(`Résultats calculés pour ${fund} au ${dateCalcul}`);
    } catch (error) {
        showError(`Erreur lors du calcul: ${error.message}`);
        showLoading(false);
    }
}

// Effacer les résultats du fonds
function clearFundResults() {
    state.fundResults = null;
    document.getElementById('fund-select').value = '';
    document.getElementById('result-column-header').style.display = 'none';
    renderTable();
}

// Chargement des champs selon le mode et la version
async function loadFields() {
    const version = document.getElementById('version-filter').value;
    if (!version) return;

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/eet-fields?version=${version}`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();

        console.log('=== DEBUG LOAD FIELDS ===');
        console.log('Total données reçues:', data.length);
        console.log('Mode actuel (type:', typeof state.currentMode, '):', state.currentMode);
        console.log('Mode vide?', state.currentMode === '');
        console.log('Exemple de données:', data.slice(0, 3).map(d => ({field: d.field_name, is_fixed: d.is_fixed_value, type: typeof d.is_fixed_value})));

        // Filtrer selon le mode sélectionné
        if (state.currentMode === '') {
            // Mode "Tous" - afficher tous les champs
            console.log('Mode TOUS - Affichage de tous les champs');
            state.allData = data;
        } else {
            // Filtrer selon le mode - convertir en string pour comparaison
            console.log('Filtrage par mode:', state.currentMode);
            state.allData = data.filter(item => String(item.is_fixed_value) === String(state.currentMode));
        }
        state.filteredData = [...state.allData];

        console.log(`Mode: ${state.currentMode || 'Tous'}, Champs trouvés: ${state.allData.length}`);
        console.log('======================');

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

// Configuration des listeners de tri
function setupSortListeners() {
    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.column;
            sortData(column);
        });
    });
}

// Tri des données
function sortData(column) {
    // Si on clique sur la même colonne, inverser l'ordre
    if (state.sortColumn === column) {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        state.sortColumn = column;
        state.sortOrder = 'asc';
    }

    // Trier les données
    state.filteredData.sort((a, b) => {
        let valueA = a[column] || '';
        let valueB = b[column] || '';

        // Convertir en minuscules pour tri insensible à la casse
        if (typeof valueA === 'string') valueA = valueA.toLowerCase();
        if (typeof valueB === 'string') valueB = valueB.toLowerCase();

        if (valueA < valueB) return state.sortOrder === 'asc' ? -1 : 1;
        if (valueA > valueB) return state.sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    // Mettre à jour l'affichage des icônes de tri
    updateSortIcons();
    renderTable();
}

// Mise à jour des icônes de tri
function updateSortIcons() {
    document.querySelectorAll('.sortable').forEach(th => {
        const icon = th.querySelector('.sort-icon');
        th.classList.remove('sorted');

        if (th.dataset.column === state.sortColumn) {
            th.classList.add('sorted');
            icon.textContent = state.sortOrder === 'asc' ? '▲' : '▼';
        } else {
            icon.textContent = '';
        }
    });
}

// Déterminer si un champ est modifiable selon sa source
function isFieldEditable(item) {
    if (String(item.is_fixed_value) === '1') {
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
    // En mode valeur fixe (1)
    if (String(item.is_fixed_value) === '1') {
        return 'Cliquer pour soumettre une validation';
    }

    // En mode valeur calculée (0), ajouter le contexte selon la source
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
        let modeText = 'valeur fixe';
        if (state.currentMode === '0') modeText = 'valeur calculée';
        else if (state.currentMode === '') modeText = '';

        const message = state.currentMode === ''
            ? 'Aucun champ trouvé'
            : `Aucun champ avec ${modeText} trouvé`;
        const colspan = state.fundResults ? 7 : 6;
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="no-data">${message}</td></tr>`;
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

        // Obtenir le résultat si disponible
        let resultCell = '';
        if (state.fundResults) {
            const result = state.fundResults[item.field_name];
            if (result !== undefined && result !== null && result !== '') {
                resultCell = `<td class="result-value">${result}</td>`;
            } else {
                resultCell = `<td class="result-empty">-</td>`;
            }
        }

        row.innerHTML = `
            <td>${item.version || ''}</td>
            <td class="field-name"><strong>${item.field_name || ''}</strong></td>
            <td class="centered">${item.is_fixed_value || ''}</td>
            <td class="editable-cell">${truncateText(item.value_source || '', 40)}</td>
            <td class="centered editable-cell">${item.is_filed_in || ''}</td>
            ${resultCell}
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

    // Mettre à jour les icônes de tri
    updateSortIcons();
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
