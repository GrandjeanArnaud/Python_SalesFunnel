# 🚀 Python Sales Funnel - Lead Scoring & Emailing Automatisé

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136.1-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.49-red.svg?style=flat)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.18.4-orange.svg?style=flat)](https://alembic.sqlalchemy.org/)
[![Tested with Pytest](https://img.shields.io/badge/Tested%20with-Pytest-white.svg?style=flat&logo=pytest&logoColor=green)](https://docs.pytest.org/)

Ce projet est un système backend complet de **Lead Scoring** et d'**Emailing Automatisé** ciblé. Conçu à l'origine dans le cadre d'un projet de formation **Odoo** chez **Technofutur TIC**, il permet de gérer des contacts professionnels répartis par secteurs d'activité, d'évaluer dynamiquement leurs centres d'intérêt grâce à un algorithme de propagation de scores, de leur envoyer des e-mails personnalisés, et de capturer leurs interactions pour affiner en continu leur profil de prospects.

---

## 📋 Sommaire

1. [Fonctionnalités Principales](#-fonctionnalités-principales)
2. [Architecture du Système](#-architecture-du-système)
3. [Schéma de la Base de Données](#-schéma-de-la-base-de-données)
4. [Algorithme de Scoring & Propagation](#-algorithme-de-scoring--propagation)
5. [Structure du Projet](#-structure-du-projet)
6. [Installation & Configuration](#-installation--configuration)
7. [Utilisation & Endpoints](#-utilisation--endpoints)
8. [Exécution des Tests](#-exécution-des-tests)
9. [Contexte du Projet](#-contexte-du-projet)

---

## ✨ Fonctionnalités Principales

- **Lead Scoring & Taxonomie d'Intérêts** : Gestion d'une taxonomie d'intérêts hiérarchique (Arbre de catégories et sous-catégories) adaptée au secteur d'activité du client.
- **Propagation des Scores** : Algorithme de propagation intelligente des scores des centres d'intérêt d'un client (le score d'une sous-catégorie influence ses catégories sœurs et parentes).
- **Moteur d'Emailing Personnalisé** : Génération et envoi de courriels au format HTML (via des templates Jinja2 fluides et responsive) recommandant des produits ciblés.
- **Suivi d'Événements (Event Logging)** : Enregistrement en base de données de chaque action (`EMAIL_SENT`, `LINK_CLICKED`, etc.) pour cartographier le parcours utilisateur.
- **Boucle de Rétroaction** : Endpoint de tracking simulant le clic de l'utilisateur final pour augmenter son intérêt (+0.1) et le rediriger vers une page vitrine.
- **Architecture Propre** : Séparation stricte des responsabilités (DTOs, Repositories, Services, Controllers) reposant sur SQLAlchemy 2.0 et PostgreSQL.

---

## ⚙️ Architecture du Système

Le diagramme suivant illustre le flux opérationnel entre les contrôleurs FastAPI, les services métier de scoring, et les interfaces de persistence :

```mermaid
flowchart TD
    A[Base de Données PostgreSQL] -->|1. Chargement Contacts & Secteurs| B[ContactInterestService]
    B -->|2. Extraction des scores JSON| C[Scoring Engine]
    B -->|3. Filtrage des intérêts par secteur| C
    C -->|4. Calcul de propagation Parent -> Enfant / Frères| C
    C -->|5. Tri et exclusion des catégories racines| D[DTOs prioritaires]
    D -->|6. Rendu Jinja2| E[email_template.html]
    E -->|7. Envoi SMTP| F[Transporteur d'Email / Mailpit]
    F -->|8. Log de l'événement EMAIL_SENT| A
    G[Client clique sur un lien d'intérêt] -->|9. Appel GET /interest| H[interest_controller]
    H -->|10. Log de l'événement LINK_CLICKED| A
    H -->|11. Incrémentation du score (+0.1)| A
    H -->|12. Rendu de redirection_template.html| I[Page de Redirection / E-commerce]
```

---

## 🗄️ Schéma de la Base de Données

Le schéma relationnel est géré par **SQLAlchemy** et synchronisé à l'aide de migrations **Alembic**.

```mermaid
erDiagram
    contacts {
        int id PK "Auto-incrément"
        string name "Nom de l'entreprise"
        string last_name "Nom de famille"
        string first_name "Prénom"
        string email "Email unique"
        int sector_id FK "Clé étrangère vers sectors"
        json interests "Scores d'intérêts {nom_interet: score}"
    }
    sectors {
        int id PK "Auto-incrément"
        string code "Ex: hair_salon, beauty_salon, spa"
        string label "Ex: Salon de Coiffure, Centre de Spa"
    }
    interests {
        int id PK "Auto-incrément"
        string name "Nom de l'intérêt"
        int parent FK "Auto-référence (parent d'intérêt)"
    }
    events {
        int id PK "Auto-incrément"
        int contact_id FK "Clé étrangère vers contacts"
        string type "Enum: EMAIL_SENT, LINK_CLICKED, etc."
        datetime date "Date de création"
        string template "Template d'email utilisé"
    }
    interest_sectors {
        int interest_id FK "Clé vers interests"
        int sector_id FK "Clé vers sectors"
    }

    contacts }o--|| sectors : "appartient à"
    events }o--|| contacts : "concerne"
    interests ||--o{ interests : "a pour parent"
    interest_sectors }o--|| interests : "associe"
    interest_sectors }o--|| sectors : "associe"
```

---

## 🧮 Algorithme de Scoring & Propagation

Le calcul des recommandations s'appuie sur la structure hiérarchique des intérêts dans la base de données. Lorsqu'un utilisateur interagit ou que son profil d'intérêts est extrait, la classe [interest_scoring.py](file:///c:/Users/a.grandjean/Desktop/Python_SalesFunnel/src/services/interest_scoring.py) applique les règles suivantes :

1. **Intérêts explicites** : Les scores bruts définis dans le champ `interests` du `Contact` (allant de $0.0$ à $1.0$) sont conservés.
2. **Propagation descendante (Parent → Enfants)** : Un parent propage **50%** de sa valeur à ses nœuds enfants directs, avec un plafond (cap) de **+0.2**.
3. **Propagation latérale (Frère → Frère)** : Les nœuds ayant le même parent se propagent **20%** de leur score, avec un plafond de **+0.1**.
4. **Normalisation** : Les scores finaux après propagation sont bridés à un maximum de **1.0**.
5. **Filtrage des catégories** : Les catégories de base ou "racines" (où `parent IS NULL`) servent de conteneurs structurels et sont exclues de la liste de recommandations des produits, mais sont insérées sous forme de boutons d'exploration en bas d'e-mail.

---

## 📂 Structure du Projet

```text
Python_SalesFunnel/
├── alembic/                # Dossier de configuration et versions de migrations Alembic
│   ├── versions/           # Scripts de migration de la base de données
│   ├── env.py              # Configuration d'environnement pour Alembic
│   └── script.py.mako      # Template pour la création de migrations
├── analyse/                # Fichiers d'analyse conceptuelle et de démonstration
│   ├── ClassDiagram.drawio # Diagramme de classes Draw.io
│   └── DB_Inserts.sql      # Scripts SQL pour peupler la DB locale
├── docs/                   # Documentation HTML auto-générée
├── src/                    # Code source de l'application FastAPI
│   ├── controllers/        # Routeurs API FastAPI
│   │   ├── interest_controller.py  # Gestion des clics et redirections
│   │   └── workflow_controller.py  # Lancement des campagnes e-mail
│   ├── dto/                # Objets de Transfert de Données (DTO)
│   ├── models/             # Modèles de base de données SQLAlchemy (Base, Contact, Event...)
│   ├── repositories/       # Couche d'accès aux données (Patterns Repository)
│   ├── services/           # Logique métier (Envoi de mails, algorithme de scoring...)
│   ├── templates/          # Gabarits HTML Jinja2 (Mails responsive, page de redirection)
│   ├── __init__.py         # Imports dynamiques des modules du package
│   └── main.py             # Point d'entrée de l'application FastAPI
├── tests/                  # Fichiers de tests unitaires et d'intégration
│   ├── conftest.py         # Fixtures pytest et base SQLite en mémoire
│   └── test_*.py           # Suites de tests par composant
├── .env                    # Fichier de variables d'environnement (non commit sur git)
├── .gitignore              # Règles d'exclusion Git
├── alembic.ini             # Fichier de configuration globale d'Alembic
├── pytest.ini              # Configuration de pytest (déclaration du PYTHONPATH)
└── requirements.txt        # Liste des dépendances Python requises
```

---

## 🛠️ Installation & Configuration

### 1. Prérequis
Assurez-vous d'avoir installé sur votre machine :
- **Python 3.10** ou version supérieure.
- **PostgreSQL** avec une base de données créée (ex: `sales_funnel`).
- **Mailpit** (recommandé pour intercepter les emails envoyés localement en développement).

### 2. Cloner le projet & créer l'environnement virtuel
```bash
git clone https://github.com/votre-compte/Python_SalesFunnel.git
cd Python_SalesFunnel

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel (Windows)
.venv\Scripts\activate

# Activer l'environnement virtuel (macOS/Linux)
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement
Créez un fichier `.env` à la racine du projet sur le modèle suivant :
```env
PYTHONPATH=src
DB_URL=postgresql://postgres:super@localhost:5432/sales_funnel
SMTP_SERVER=localhost
SMTP_PORT=1025
```

### 4. Lancer les migrations de base de données
Appliquez les scripts Alembic pour créer la structure des tables PostgreSQL :
```bash
alembic upgrade head
```

### 5. Alimenter la base de données
Vous pouvez utiliser le fichier SQL fourni dans `analyse/DB_Inserts.sql` pour insérer les secteurs (Coiffure, Spa, Beauté, Barbier), des contacts exemples et l'arbre des intérêts :
```bash
psql -U postgres -d sales_funnel -f analyse/DB_Inserts.sql
```
*(Remplacez les paramètres `postgres` et `sales_funnel` par les identifiants configurés dans votre PostgreSQL).*

---

## 🖥️ Utilisation & Endpoints

### Lancement de l'application
Démarrez le serveur FastAPI avec Uvicorn :
```bash
uvicorn src.main:app --reload
```
Le serveur sera disponible sur `http://127.0.0.1:8000`. Vous pouvez accéder à la documentation interactive Swagger sur `http://127.0.0.1:8000/docs`.

### Points d'accès API

| Méthode | Route | Description |
| :--- | :--- | :--- |
| **GET** | `/workflow/send_to_all` | Génère les scores pour tous les contacts, compile les emails d'intérêts prioritaires, les envoie, et enregistre un événement `EMAIL_SENT` pour chaque succès. |
| **GET** | `/interest` | Paramètres requis : `contact_id` et `interest_id`. Simule un clic utilisateur : ajoute un événement `LINK_CLICKED` en DB, incrémente le score de l'intérêt ciblé de `+0.1` (clampé à `1.0`) et renvoie la page HTML de redirection. |

### Visualisation locale des e-mails (Mailpit)
Si vous utilisez Mailpit en local, lancez-le en tâche de fond. Vous pourrez voir tous les e-mails générés par le workflow sur l'interface web de Mailpit :
- SMTP : `localhost:1025`
- Web UI : `http://localhost:8025`

---

## 🧪 Exécution des Tests

Les tests unitaires et d'intégration couvrent la totalité du code métier et de la persistence. Ils s'exécutent sur une base **SQLite en mémoire** éphémère (configurée dans `tests/conftest.py`) et ne modifient donc pas votre base de données locale.

Pour lancer les tests :
```bash
pytest -v
```

Vous devriez obtenir une confirmation semblable à celle-ci :
```text
============================= 29 passed in 1.27s ==============================
```

---

## 🎓 Contexte du Projet

Ce projet a été réalisé dans le cadre de la formation **Odoo Developer** dispensée par **Technofutur TIC** (Belgique). L'objectif est d'explorer et d'implémenter les concepts d'algorithmes de scoring et d'automatisation marketing par e-mail en Python pur, en appliquant les bonnes pratiques de programmation orientée objet, de tests automatisés et d'architecture en couches avant de les interfacer ou de les transposer dans un écosystème ERP d'entreprise comme Odoo.
