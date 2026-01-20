# Administration des Rapports Réglementaires

Application web pour l'administration et la gestion des rapports réglementaires avec système de validation.

## 📋 Description

Cette application permet de :
- Visualiser et sélectionner des fonds depuis la table `Ref_Funds`
- Consulter les templates de reporting depuis la table `tb_eet_fields`
- Gérer les demandes de modification via un système de validation (`tb_validation_requests`)

## 🛠️ Tech Stack

### Backend
- **FastAPI** : Framework web Python moderne et performant
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **PyODBC** : Connexion à SQL Server
- **Pandas** : Manipulation des données
- **Uvicorn** : Serveur ASGI

### Frontend
- **HTML5** : Structure de l'interface
- **CSS3** : Styles et mise en page responsive
- **JavaScript (Vanilla)** : Logique côté client et interactions API

### Base de données
- **SQL Server** : Base de données relationnelle

## 📁 Structure du Projet

```
.
├── backend/
│   ├── main.py              # Application FastAPI principale
│   └── dwh_connect.py       # Module de connexion à la base de données
├── frontend/
│   ├── templates/
│   │   └── index.html       # Page principale
│   └── static/
│       ├── css/
│       │   └── style.css    # Styles de l'application
│       └── js/
│           └── app.js       # Logique JavaScript
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- ODBC Driver 13 ou 17 for SQL Server
- Accès à la base de données SQL Server (MandarineGestion_Datawarehouse)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <url-du-repo>
cd repo_test_claude
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Vérifier la configuration de la base de données**

Ouvrir `backend/dwh_connect.py` et vérifier les paramètres de connexion :
- Serveur : `SQLDW.mandarine.lan` ou `SQLDW`
- Base de données : `MandarineGestion_Datawarehouse`

## ▶️ Lancement de l'application

1. **Démarrer le serveur backend**
```bash
cd backend
python main.py
```
Ou via uvicorn :
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Accéder à l'application**

Ouvrir votre navigateur et aller à : `http://localhost:8000`

3. **Documentation de l'API**

FastAPI génère automatiquement une documentation interactive :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Fonds
- `GET /api/funds` - Liste tous les fonds disponibles
- Retourne : `[{Mnemo_Fund: str, Lib_Fund: str}, ...]`

### Templates EET
- `GET /api/eet-fields?version={version}` - Récupère les champs EET pour une version
- `GET /api/eet-versions` - Liste toutes les versions disponibles

### Validation Requests
- `POST /api/validation-requests` - Crée une demande de validation
- `GET /api/validation-requests?status={status}` - Liste les demandes de validation

### Health Check
- `GET /health` - Vérifie l'état de l'application et de la connexion DB

## 📝 Fonctionnalités Phase 1

### ✅ Implémenté
- [x] Page d'accueil avec interface responsive
- [x] Sélection de fonds depuis `Ref_Funds`
- [x] Affichage des informations du fonds sélectionné
- [x] Sélection de versions de templates
- [x] Visualisation des champs `tb_eet_fields`
- [x] Architecture de validation requests
- [x] Connexion à la base de données SQL Server

### 🔄 À développer (phases suivantes)
- [ ] Interface complète de validation des requêtes
- [ ] Création/modification/suppression de données avec validation
- [ ] Système d'authentification et d'autorisation
- [ ] Historique des modifications
- [ ] Export des données (Excel, CSV)
- [ ] Filtres et recherche avancée
- [ ] Tableau de bord analytique

## 🔐 Sécurité

- Les requêtes de modification passent par `tb_validation_requests`
- CORS configuré (à restreindre en production)
- Utiliser HTTPS en production
- Implémenter l'authentification pour les endpoints sensibles

## 🐛 Debugging

### Test de connexion à la base de données
```bash
cd backend
python dwh_connect.py
```

### Vérifier l'état de l'application
```bash
curl http://localhost:8000/health
```

## 📚 Prochaines étapes

1. Tester l'application avec les données réelles
2. Affiner l'interface utilisateur selon les retours
3. Implémenter le workflow complet de validation
4. Ajouter les fonctionnalités de modification de données
5. Créer les écrans de gestion des demandes de validation

## 🤝 Contribution

Cette application est en phase de développement initial. Les suggestions et améliorations sont les bienvenues !

## 📄 License

Usage interne uniquement.
