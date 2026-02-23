// Configuration de l'API - Utilise l'host actuel
const API_BASE_URL = `${window.location.origin}/api`;

// État de l'application
const state = {
    allFunds: [],
    filteredFunds: [],
    selectedFunds: new Set(),
    versions: [],
    sfdrCategories: [],
    publicDedieValues: []
};

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    await loadVersions();
    await loadFunds();
    setDefaultCalcDate();
}

// Définir la date par défaut à la fin de l'année précédente
function setDefaultCalcDate() {
    const dateInput = document.getElementById('date-input');
    if (dateInput) {
        const currentYear = new Date().getFullYear();
        const lastYearEnd = `${currentYear - 1}-12-31`;
        dateInput.value = lastYearEnd;
    }
}

function setupEventListeners() {
    const sfdrFilter = document.getElementById('sfdr-filter');
    const publicFilter = document.getElementById('public-filter');
    const searchInput = document.getElementById('search-input');
    const selectAllBtn = document.getElementById('select-all-btn');
    const deselectAllBtn = document.getElementById('deselect-all-btn');
    const generateBtn = document.getElementById('generate-btn');

    sfdrFilter.addEventListener('change', applyFilters);
    publicFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', debounce(applyFilters, 300));
    selectAllBtn.addEventListener('click', selectAll);
    deselectAllBtn.addEventListener('click', deselectAll);
    generateBtn.addEventListener('click', generateEET);
}

// Chargement des versions
async function loadVersions() {
    try {
        const response = await fetch(`${API_BASE_URL}/eet-versions`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();
        state.versions = data.versions;
        populateVersionSelect();
    } catch (error) {
        showError(`Erreur lors du chargement des versions: ${error.message}`);
    }
}

function populateVersionSelect() {
    const select = document.getElementById('version-select');
    select.innerHTML = '';

    state.versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        select.appendChild(option);
    });

    // Sélectionner la première version (la plus récente) par défaut
    if (state.versions.length > 0) {
        select.value = state.versions[0];
    }
}

// Chargement des fonds
async function loadFunds() {
    try {
        const response = await fetch(`${API_BASE_URL}/funds-details`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        state.allFunds = await response.json();
        state.filteredFunds = [...state.allFunds];

        // Extraire les valeurs uniques pour les filtres
        extractFilterValues();
        populateFilters();
        renderFundsList();
    } catch (error) {
        showError(`Erreur lors du chargement des fonds: ${error.message}`);
    }
}

function extractFilterValues() {
    const sfdrSet = new Set();
    const publicSet = new Set();

    state.allFunds.forEach(fund => {
        if (fund.sfdr_cat) sfdrSet.add(fund.sfdr_cat);
        if (fund.Public_Dedie) publicSet.add(fund.Public_Dedie);
    });

    state.sfdrCategories = Array.from(sfdrSet).sort();
    state.publicDedieValues = Array.from(publicSet).sort();
}

function populateFilters() {
    const sfdrFilter = document.getElementById('sfdr-filter');
    const publicFilter = document.getElementById('public-filter');

    // SFDR categories
    state.sfdrCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        sfdrFilter.appendChild(option);
    });

    // Public/Dédié
    state.publicDedieValues.forEach(val => {
        const option = document.createElement('option');
        option.value = val;
        option.textContent = val;
        publicFilter.appendChild(option);
    });
}

// Application des filtres
function applyFilters() {
    const sfdrFilter = document.getElementById('sfdr-filter').value;
    const publicFilter = document.getElementById('public-filter').value;
    const searchTerm = document.getElementById('search-input').value.toLowerCase();

    state.filteredFunds = state.allFunds.filter(fund => {
        // Filtre SFDR (comparaison non stricte pour gérer nombre vs string)
        if (sfdrFilter && String(fund.sfdr_cat) !== String(sfdrFilter)) return false;

        // Filtre Public/Dédié (comparaison non stricte)
        if (publicFilter && String(fund.Public_Dedie) !== String(publicFilter)) return false;

        // Recherche textuelle
        if (searchTerm) {
            const searchText = `${fund.Mnemo_Fund} ${fund.Lib_Fund}`.toLowerCase();
            if (!searchText.includes(searchTerm)) return false;
        }

        return true;
    });

    renderFundsList();
}

// Rendu de la liste des fonds
function renderFundsList() {
    const fundsList = document.getElementById('funds-list');

    if (state.filteredFunds.length === 0) {
        fundsList.innerHTML = '<p class="loading-text">Aucun fonds trouvé</p>';
        return;
    }

    fundsList.innerHTML = '';
    state.filteredFunds.forEach(fund => {
        const fundItem = document.createElement('div');
        fundItem.className = 'fund-item';

        const isChecked = state.selectedFunds.has(fund.Mnemo_Fund);

        fundItem.innerHTML = `
            <input type="checkbox"
                   id="fund-${fund.Mnemo_Fund}"
                   value="${fund.Mnemo_Fund}"
                   ${isChecked ? 'checked' : ''}>
            <label for="fund-${fund.Mnemo_Fund}" class="fund-info">
                <div class="fund-name">${fund.Mnemo_Fund}</div>
                <div class="fund-details">
                    ${fund.Lib_Fund}
                    ${fund.sfdr_cat ? ` • SFDR: ${fund.sfdr_cat}` : ''}
                    ${fund.Public_Dedie ? ` • ${fund.Public_Dedie}` : ''}
                </div>
            </label>
        `;

        const checkbox = fundItem.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', (e) => handleFundSelection(e, fund.Mnemo_Fund));

        fundItem.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT') {
                checkbox.checked = !checkbox.checked;
                handleFundSelection({target: checkbox}, fund.Mnemo_Fund);
            }
        });

        fundsList.appendChild(fundItem);
    });

    updateSelectionCount();
}

// Gestion de la sélection
function handleFundSelection(event, fundMnemo) {
    if (event.target.checked) {
        state.selectedFunds.add(fundMnemo);
    } else {
        state.selectedFunds.delete(fundMnemo);
    }
    updateSelectionCount();
}

function selectAll() {
    state.filteredFunds.forEach(fund => {
        state.selectedFunds.add(fund.Mnemo_Fund);
    });
    renderFundsList();
}

function deselectAll() {
    state.selectedFunds.clear();
    renderFundsList();
}

function updateSelectionCount() {
    const count = state.selectedFunds.size;
    document.getElementById('selection-count').textContent = `${count} fonds sélectionné(s)`;

    const generateBtn = document.getElementById('generate-btn');
    generateBtn.disabled = count === 0;
}

// Génération du fichier EET
async function generateEET() {
    const version = document.getElementById('version-select').value;
    const date = document.getElementById('date-input').value;
    const funds = Array.from(state.selectedFunds);

    if (funds.length === 0) {
        showError('Veuillez sélectionner au moins un fonds');
        return;
    }

    if (!version) {
        showError('Veuillez sélectionner une version EET');
        return;
    }

    try {
        showLoading(true);

        // Convertir la date au format DD/MM/YYYY
        const dateCalcul = convertISOtoFrenchDate(date);

        const response = await fetch(`${API_BASE_URL}/generate-eet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                funds: funds,
                version: version,
                date_calcul: dateCalcul
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la génération');
        }

        // Télécharger le fichier
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Récupérer le nom du fichier depuis les headers
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `EET_${date.replace(/-/g, '')}.xlsx`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showLoading(false);
        showSuccess('Fichier EET généré avec succès !');
    } catch (error) {
        showLoading(false);
        showError(`Erreur: ${error.message}`);
    }
}

// Convertir une date ISO (YYYY-MM-DD) en format français (DD/MM/YYYY)
function convertISOtoFrenchDate(isoDate) {
    if (!isoDate) return '31/12/2024';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
}

// Utilitaires
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
