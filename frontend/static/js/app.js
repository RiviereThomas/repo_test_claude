// Configuration de l'API
const API_BASE_URL = 'http://localhost:8000/api';

// État de l'application
const state = {
    funds: [],
    selectedFund: null,
    versions: [],
    selectedVersion: null,
    eetFields: []
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

// Initialisation de l'application
async function initializeApp() {
    await loadFunds();
    await loadVersions();
}

// Configuration des écouteurs d'événements
function setupEventListeners() {
    const fundSelect = document.getElementById('fund-select');
    const versionSelect = document.getElementById('version-select');
    const loadFieldsBtn = document.getElementById('load-fields-btn');
    const viewRequestsBtn = document.getElementById('view-requests-btn');

    fundSelect.addEventListener('change', handleFundSelection);
    loadFieldsBtn.addEventListener('click', handleLoadFields);
    viewRequestsBtn.addEventListener('click', handleViewRequests);
}

// Chargement de la liste des fonds
async function loadFunds() {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/funds`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        state.funds = await response.json();
        populateFundsSelect();
        showLoading(false);
    } catch (error) {
        showError(`Erreur lors du chargement des fonds: ${error.message}`);
        showLoading(false);
    }
}

// Chargement de la liste des versions
async function loadVersions() {
    try {
        const response = await fetch(`${API_BASE_URL}/eet-versions`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        state.versions = data.versions;
        populateVersionsSelect();
    } catch (error) {
        showError(`Erreur lors du chargement des versions: ${error.message}`);
    }
}

// Remplir le sélecteur de fonds
function populateFundsSelect() {
    const select = document.getElementById('fund-select');
    select.innerHTML = '<option value="">-- Sélectionner un fonds --</option>';

    state.funds.forEach(fund => {
        const option = document.createElement('option');
        option.value = fund.Mnemo_Fund;
        option.textContent = `${fund.Mnemo_Fund} - ${fund.Lib_Fund}`;
        option.dataset.lib = fund.Lib_Fund;
        select.appendChild(option);
    });
}

// Remplir le sélecteur de versions
function populateVersionsSelect() {
    const select = document.getElementById('version-select');
    select.innerHTML = '<option value="">-- Sélectionner une version --</option>';

    state.versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        select.appendChild(option);
    });
}

// Gestion de la sélection d'un fonds
function handleFundSelection(event) {
    const select = event.target;
    const selectedOption = select.options[select.selectedIndex];

    if (select.value) {
        state.selectedFund = {
            mnemo: select.value,
            lib: selectedOption.dataset.lib
        };

        // Afficher les informations du fonds sélectionné
        document.getElementById('selected-mnemo').textContent = state.selectedFund.mnemo;
        document.getElementById('selected-lib').textContent = state.selectedFund.lib;
        document.getElementById('fund-info').style.display = 'block';
    } else {
        state.selectedFund = null;
        document.getElementById('fund-info').style.display = 'none';
    }
}

// Chargement des champs EET
async function handleLoadFields() {
    const versionSelect = document.getElementById('version-select');
    const version = versionSelect.value;

    if (!version) {
        showError('Veuillez sélectionner une version');
        return;
    }

    state.selectedVersion = version;

    try {
        showLoading(true);
        hideError();

        const response = await fetch(`${API_BASE_URL}/eet-fields?version=${encodeURIComponent(version)}`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        state.eetFields = await response.json();
        displayEETFields();
        showLoading(false);
    } catch (error) {
        showError(`Erreur lors du chargement des champs: ${error.message}`);
        showLoading(false);
    }
}

// Affichage des champs EET dans un tableau
function displayEETFields() {
    const container = document.getElementById('fields-container');

    if (state.eetFields.length === 0) {
        container.innerHTML = '<p class="hint">Aucun champ trouvé pour cette version.</p>';
        return;
    }

    // Créer le tableau
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Version</th>
                <th>Nom du Champ</th>
                <th>Valeur Fixe</th>
                <th>Source</th>
                <th>Filed In</th>
                <th>Type Requis</th>
                <th>Format</th>
                <th>Remarques</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    `;

    const tbody = table.querySelector('tbody');

    state.eetFields.forEach(field => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${field.version || ''}</td>
            <td><strong>${field.field_name || ''}</strong></td>
            <td>${field.is_fixed_value || ''}</td>
            <td>${field.value_source || ''}</td>
            <td>${field.is_filed_in || ''}</td>
            <td>${field.requirement_type || ''}</td>
            <td>${field.format || ''}</td>
            <td>${field.remarques || ''}</td>
        `;
        tbody.appendChild(row);
    });

    // Wrapper pour le scroll
    const wrapper = document.createElement('div');
    wrapper.className = 'table-container';
    wrapper.appendChild(table);

    container.innerHTML = '';
    container.appendChild(wrapper);
}

// Affichage des demandes de validation
async function handleViewRequests() {
    try {
        const response = await fetch(`${API_BASE_URL}/validation-requests?status=PENDING`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const requests = await response.json();
        displayValidationRequests(requests);
    } catch (error) {
        showError(`Erreur lors du chargement des demandes: ${error.message}`);
    }
}

// Affichage des demandes de validation dans un tableau
function displayValidationRequests(requests) {
    const container = document.getElementById('validation-requests');
    const tbody = document.querySelector('#requests-table tbody');

    if (requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">Aucune demande en attente</td></tr>';
    } else {
        tbody.innerHTML = '';
        requests.forEach(request => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${request.request_type}</td>
                <td>${request.table_name}</td>
                <td>${request.status}</td>
                <td>${request.created_at || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    container.style.display = 'block';
}

// Affichage du loader
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

// Affichage des erreurs
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    // Masquer automatiquement après 5 secondes
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Masquer les erreurs
function hideError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'none';
}
