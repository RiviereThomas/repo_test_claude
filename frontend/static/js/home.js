// Lancer la production d'un module
async function runProduction(module) {
    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const response = await fetch(`/api/run-production/${module}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            alert(`Production ${module.toUpperCase()} lancée avec succès!\n\n${result.message}`);
        } else {
            alert(`Erreur lors du lancement de la production ${module.toUpperCase()}:\n${result.detail}`);
        }
    } catch (error) {
        alert(`Erreur de communication avec le serveur:\n${error.message}`);
    } finally {
        loading.style.display = 'none';
    }
}

// Ouvrir le dossier des archives
async function openArchives(module) {
    try {
        const response = await fetch(`/api/open-archives/${module}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            alert(`Ouverture du dossier ${module.toUpperCase()} dans l'explorateur...`);
        } else {
            alert(`Erreur lors de l'ouverture du dossier:\n${result.detail}`);
        }
    } catch (error) {
        alert(`Erreur de communication avec le serveur:\n${error.message}`);
    }
}

// Afficher le loader au clic sur les liens
document.addEventListener('DOMContentLoaded', () => {
    // Sélectionner tous les liens actifs (pas les boutons disabled)
    const activeLinks = document.querySelectorAll('a.module-btn:not([disabled])');
    const loading = document.getElementById('loading');

    activeLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Afficher le loader seulement pour les liens internes (pas les liens externes)
            if (!link.hasAttribute('target') || link.getAttribute('target') !== '_blank') {
                loading.style.display = 'flex';
            }
        });
    });
});
