# LoanApplication

LoanApplication est une application complète de gestion de prêts. Elle se compose de deux parties :  

1. **Backend / Admin** (`loan-app-admin`) : Gestion des prêts, base de données et tableau de bord.  
2. **Frontend / Client** (`loan-app-client`) : Interface utilisateur pour demander et suivre des prêts.  

---

## Structure du projet

loanapplication/
│
├─ loan-app-admin/ # Backend Python (Flask)
│ ├─ app.py
│ ├─ dashboard.py
│ ├─ database.py
│ ├─ models.py
│ ├─ uploads/ # Dossiers pour fichiers uploadés
│ ├─ pycache/
│ ├─ loan_applications.db
│ ├─ loan_applications_v2.db
│ └─ requirements.txt
│
└─ loan-app-client/ # Frontend Node.js
├─ server.js
├─ package.json
├─ package-lock.json
├─ .env
├─ public/ # Fichiers statiques
├─ model/ # JSON de workflow et OCR
│ ├─ campagnyhouses.json
│ ├─ demoworkflow.json
│ └─ OCR.json
└─ node_modules/

yaml
Copier le code

---

## Prérequis

- Python 3.10 ou plus
- Node.js 18 ou plus
- npm ou yarn
- SQLite (optionnel, les fichiers `.db` sont fournis)

---

## Installation

### Backend / Admin

1. Aller dans le dossier `loan-app-admin` :
```bash
cd loan-app-admin
Créer un environnement virtuel (optionnel) :

bash
Copier le code
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
Installer les dépendances :

bash
Copier le code
pip install -r requirements.txt
Lancer le serveur Flask :

bash
Copier le code
python app.py
Dashboard admin : http://localhost:5000

Frontend / Client
Aller dans le dossier loan-app-client :

bash
Copier le code
cd loan-app-client
Installer les dépendances :

bash
Copier le code
npm install
Lancer le serveur Node.js :

bash
Copier le code
node server.js
Application client : http://localhost:3000


Utilisation
Admin : gérer les demandes de prêts et consulter les données.

Client : créer un compte, soumettre un prêt, suivre le statut.
