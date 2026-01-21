// Configuration de l'API
const API_BASE_URL = 'http://localhost:8000/api';

// État de l'application
const state = {
    allData: [],           // Toutes les données chargées
    filteredData: [],      // Données après filtrage
    sortColumn: null,      // Colonne de tri actuelle
    sortDirection: 'asc',  // Direction du tri
    versions: [],
    filedInValues: [],
    funds: [],             // Liste des fonds disponibles
    fundResults: {},       // Résultats du fonds sélectionné {field_name: result}
    selectedFund: null     // Fonds sélectionné
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

// Initialisation de l'application
async function initializeApp() {
    await loadVersions();
    await loadFunds();
    await loadAllEETFields();

    // Appliquer les filtres par défaut (version EET_1_1_3)
    applyFilters();
}

// Configuration des écouteurs d'événements
function setupEventListeners() {
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    const exportBtn = document.getElementById('export-btn');
    const searchField = document.getElementById('search-field');
    const versionFilter = document.getElementById('version-filter');
    const fixedValueFilter = document.getElementById('fixed-value-filter');
    const filedInFilter = document.getElementById('filed-in-filter');
    const fundFilter = document.getElementById('fund-filter');
    const dateFilter = document.getElementById('date-filter');

    applyFiltersBtn.addEventListener('click', applyFilters);
    resetFiltersBtn.addEventListener('click', resetFilters);
    exportBtn.addEventListener('click', exportToCSV);
    searchField.addEventListener('input', debounce(applyFilters, 300));

    // Auto-update au changement des filtres
    versionFilter.addEventListener('change', applyFilters);
    fixedValueFilter.addEventListener('change', applyFilters);
    filedInFilter.addEventListener('change', applyFilters);
    fundFilter.addEventListener('change', handleFundChange);
    dateFilter.addEventListener('change', handleFundChange);

    // Gestion du tri sur les colonnes
    const headers = document.querySelectorAll('th.sortable');
    headers.forEach(header => {
        header.addEventListener('click', () => handleSort(header.dataset.column));
    });
}

// Chargement de la liste des versions
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

// Remplir le filtre de versions
function populateVersionsFilter() {
    const select = document.getElementById('version-filter');
    state.versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        select.appendChild(option);
    });

    // Sélectionner EET_1_1_3 par défaut si disponible
    if (state.versions.includes('EET_1_1_3')) {
        select.value = 'EET_1_1_3';
    }
}

// Chargement de tous les champs EET
async function loadAllEETFields() {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/eet-fields`);

        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        state.allData = await response.json();
        state.filteredData = [...state.allData];

        // Extraire les valeurs uniques pour le filtre "Filed In"
        extractFiledInValues();
        populateFiledInFilter();

        renderTable();
        updateRowCount();
        showLoading(false);
    } catch (error) {
        showError(`Erreur lors du chargement des données: ${error.message}`);
        showLoading(false);
    }
}

// Extraire les valeurs uniques de "Filed In"
function extractFiledInValues() {
    const values = new Set();
    state.allData.forEach(item => {
        if (item.is_filed_in) {
            values.add(item.is_filed_in);
        }
    });
    state.filedInValues = Array.from(values).sort();
}

// Remplir le filtre "Filed In"
function populateFiledInFilter() {
    const select = document.getElementById('filed-in-filter');
    state.filedInValues.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    });
}

// Chargement de la liste des fonds
async function loadFunds() {
    try {
        const response = await fetch(`${API_BASE_URL}/funds`);
        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        state.funds = await response.json();
        populateFundsFilter();
    } catch (error) {
        showError(`Erreur lors du chargement des fonds: ${error.message}`);
    }
}

// Remplir le filtre de fonds
function populateFundsFilter() {
    const select = document.getElementById('fund-filter');
    state.funds.forEach(fund => {
        const option = document.createElement('option');
        option.value = fund.Mnemo_Fund;
        option.textContent = `${fund.Mnemo_Fund} - ${fund.Lib_Fund}`;
        select.appendChild(option);
    });
}

// Gestion du changement de fonds
async function handleFundChange() {
    const fundSelect = document.getElementById('fund-filter');
    const selectedFund = fundSelect.value;

    if (selectedFund) {
        state.selectedFund = selectedFund;
        await loadFundResults(selectedFund);
    } else {
        state.selectedFund = null;
        state.fundResults = {};
    }

    // Re-render le tableau avec ou sans résultats
    renderTable();
}

// Charger les résultats d'un fonds
async function loadFundResults(fund) {
    try {
        showLoading(true);
        const versionFilter = document.getElementById('version-filter').value || 'EET_1_1_3';
        const dateFilter = document.getElementById('date-filter').value;

        // Convertir la date du format ISO (YYYY-MM-DD) au format DD/MM/YYYY
        const dateCalcul = convertISOtoFrenchDate(dateFilter);

        const response = await fetch(`${API_BASE_URL}/fund-results/${fund}?version=${versionFilter}&date_calcul=${encodeURIComponent(dateCalcul)}`);

        if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

        const data = await response.json();
        state.fundResults = data.results;
        showLoading(false);
    } catch (error) {
        showError(`Erreur lors du chargement des résultats: ${error.message}`);
        state.fundResults = {};
        showLoading(false);
    }
}

// Convertir une date ISO (YYYY-MM-DD) en format français (DD/MM/YYYY)
function convertISOtoFrenchDate(isoDate) {
    if (!isoDate) return '31/12/2024';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
}

// Application des filtres
function applyFilters() {
    const versionFilter = document.getElementById('version-filter').value;
    const fixedValueFilter = document.getElementById('fixed-value-filter').value;
    const filedInFilter = document.getElementById('filed-in-filter').value;
    const searchTerm = document.getElementById('search-field').value.toLowerCase();

    state.filteredData = state.allData.filter(item => {
        // Filtre par version
        if (versionFilter && item.version !== versionFilter) return false;

        // Filtre par valeur fixe
        if (fixedValueFilter && item.is_fixed_value !== fixedValueFilter) return false;

        // Filtre par filed in
        if (filedInFilter && item.is_filed_in !== filedInFilter) return false;

        // Filtre par recherche de nom
        if (searchTerm && !item.field_name?.toLowerCase().includes(searchTerm)) return false;

        return true;
    });

    renderTable();
    updateRowCount();
}

// Réinitialisation des filtres
function resetFilters() {
    document.getElementById('version-filter').value = '';
    document.getElementById('fixed-value-filter').value = '';
    document.getElementById('filed-in-filter').value = '';
    document.getElementById('search-field').value = '';

    state.filteredData = [...state.allData];
    state.sortColumn = null;
    state.sortDirection = 'asc';

    renderTable();
    updateRowCount();
    updateSortIcons();
}

// Gestion du tri
function handleSort(column) {
    if (state.sortColumn === column) {
        // Inverser la direction si on clique sur la même colonne
        state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // Nouvelle colonne, tri ascendant par défaut
        state.sortColumn = column;
        state.sortDirection = 'asc';
    }

    sortData();
    renderTable();
    updateSortIcons();
}

// Tri des données
function sortData() {
    if (!state.sortColumn) return;

    state.filteredData.sort((a, b) => {
        let aVal = a[state.sortColumn] || '';
        let bVal = b[state.sortColumn] || '';

        // Conversion en chaîne pour comparaison
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();

        if (aVal < bVal) return state.sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return state.sortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

// Mise à jour des icônes de tri
function updateSortIcons() {
    const headers = document.querySelectorAll('th.sortable');
    headers.forEach(header => {
        const icon = header.querySelector('.sort-icon');
        if (header.dataset.column === state.sortColumn) {
            icon.textContent = state.sortDirection === 'asc' ? '↑' : '↓';
            header.classList.add('sorted');
        } else {
            icon.textContent = '⇅';
            header.classList.remove('sorted');
        }
    });
}

// Rendu du tableau
function renderTable() {
    const tbody = document.getElementById('table-body');

    if (state.filteredData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">Aucune donnée correspondante</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    state.filteredData.forEach(item => {
        const result = state.fundResults[item.field_name] || '';
        const resultClass = state.selectedFund ? 'result-value' : 'result-empty';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.version || ''}</td>
            <td class="field-name"><strong>${item.field_name || ''}</strong></td>
            <td class="centered">${item.is_fixed_value || ''}</td>
            <td>${item.value_source || ''}</td>
            <td class="centered">${item.is_filed_in || ''}</td>
            <td>${item.requirement_type || ''}</td>
            <td>${item.format || ''}</td>
            <td class="remarks">${item.remarques || ''}</td>
            <td class="${resultClass}">${result}</td>
        `;
        tbody.appendChild(row);
    });

    // Ajouter les event listeners pour tooltip et menu contextuel
    setupCellInteractions();
}

// Mise à jour du compteur de lignes
function updateRowCount() {
    const rowCount = document.getElementById('row-count');
    const count = state.filteredData.length;
    const total = state.allData.length;
    rowCount.textContent = `${count} ligne${count > 1 ? 's' : ''} (sur ${total} au total)`;
}

// Export CSV
function exportToCSV() {
    if (state.filteredData.length === 0) {
        alert('Aucune donnée à exporter');
        return;
    }

    const headers = ['Version', 'Nom du Champ', 'Valeur Fixe', 'Source', 'Filed In', 'Type Requis', 'Format', 'Remarques'];
    const rows = state.filteredData.map(item => [
        item.version || '',
        item.field_name || '',
        item.is_fixed_value || '',
        item.value_source || '',
        item.is_filed_in || '',
        item.requirement_type || '',
        item.format || '',
        item.remarques || ''
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        // Échapper les virgules et guillemets dans les données
        const escapedRow = row.map(cell => {
            const cellStr = String(cell);
            if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
                return `"${cellStr.replace(/"/g, '""')}"`;
            }
            return cellStr;
        });
        csvContent += escapedRow.join(',') + '\n';
    });

    // Télécharger le fichier
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `eet_fields_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ===== INTERACTIONS CELLULES (Tooltip + Menu Contextuel) =====
let currentCell = null;

function setupCellInteractions() {
    const cells = document.querySelectorAll('.data-table tbody td');
    const tooltip = document.getElementById('cell-tooltip');
    const contextMenu = document.getElementById('context-menu');

    cells.forEach(cell => {
        // Tooltip au survol
        cell.addEventListener('mouseenter', (e) => {
            const cellText = cell.textContent.trim();
            if (cellText && cellText !== '') {
                tooltip.textContent = cellText;
                tooltip.style.display = 'block';
                positionTooltip(e, tooltip);
            }
        });

        cell.addEventListener('mousemove', (e) => {
            if (tooltip.style.display === 'block') {
                positionTooltip(e, tooltip);
            }
        });

        cell.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });

        // Menu contextuel au clic droit
        cell.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            currentCell = cell;
            showContextMenu(e, contextMenu);
        });
    });

    // Fermer le menu contextuel en cliquant ailleurs
    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
    });

    // Action de copie
    document.getElementById('copy-cell').addEventListener('click', () => {
        if (currentCell) {
            copyToClipboard(currentCell.textContent.trim());
            contextMenu.style.display = 'none';
        }
    });
}

// Positionner le tooltip près du curseur
function positionTooltip(e, tooltip) {
    const offset = 15;
    let x = e.clientX + offset;
    let y = e.clientY + offset;

    // Vérifier si le tooltip dépasse l'écran
    const tooltipRect = tooltip.getBoundingClientRect();
    if (x + tooltipRect.width > window.innerWidth) {
        x = e.clientX - tooltipRect.width - offset;
    }
    if (y + tooltipRect.height > window.innerHeight) {
        y = e.clientY - tooltipRect.height - offset;
    }

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
}

// Afficher le menu contextuel
function showContextMenu(e, menu) {
    const x = e.clientX;
    const y = e.clientY;

    // Positionner le menu
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.style.display = 'block';

    // Ajuster si dépasse l'écran
    setTimeout(() => {
        const menuRect = menu.getBoundingClientRect();
        if (menuRect.right > window.innerWidth) {
            menu.style.left = (x - menuRect.width) + 'px';
        }
        if (menuRect.bottom > window.innerHeight) {
            menu.style.top = (y - menuRect.height) + 'px';
        }
    }, 0);
}

// Copier dans le presse-papier
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showCopyNotification();
    } catch (err) {
        // Fallback pour les anciens navigateurs
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showCopyNotification();
    }
}

// Notification de copie
function showCopyNotification() {
    const notification = document.createElement('div');
    notification.textContent = '✓ Copié !';
    notification.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--vert-fonce);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 3000;
        font-weight: 600;
        animation: slideUp 0.3s ease-out;
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Fonction de debounce pour la recherche
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

// Affichage du loader
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'flex' : 'none';
}

// Affichage des erreurs
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}
