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
