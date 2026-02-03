Associations Culturelles
========================

Vue d'ensemble
--------------

Le module **Associations Culturelles** pour Odoo 19 fournit une solution complète pour la gestion des adhésions en ligne pour tous types d'associations : culturelles, sportives, bénévoles, récréatives et autres.

Fonctionnalités principales :

* Gestion des associations culturelles avec informations complètes
* Plans d'adhésion configurables (année solaire ou calendrier)
* Système d'adhésion en ligne intégré
* Paiement en ligne via les fournisseurs Odoo
* Zone réservée pour les membres ("Mes adhésions")
* Gestion des données fiscales et personnelles
* Intégration avec newsletter et listes de diffusion

Installation
------------

1. Copiez le dossier du module dans le répertoire ``addons`` de votre installation Odoo 19
2. Mettez à jour la liste des applications : ``odoo-bin -u all -d your_database``
3. Activez le mode développeur
4. Allez dans Applications > Mettre à jour la liste des applications
5. Recherchez "Associazioni" et installez le module

Exigences
---------

* Odoo 19.0
* Modules requis : ``base``, ``website``, ``auth_signup``, ``payment``, ``mail``, ``mass_mailing``

Configuration
-------------

Prérequis
~~~~~~~~~

1. Module ``payment`` installé et configuré
2. Au moins un fournisseur de paiement actif et publié (Stripe, PayPal, etc.)
3. Utilisateurs avec les permissions appropriées

Configuration initiale
~~~~~~~~~~~~~~~~~~~~~~

1. **Créer des associations culturelles**
   
   Allez dans Associations > Associations et créez les associations que vous gérerez.

2. **Créer des plans d'adhésion**
   
   Allez dans Associations > Plans d'adhésion et créez les plans disponibles :
   
   * **Année solaire** : Expire le 31 décembre de l'année de référence
   * **Calendrier** : Expire 12 mois après la date d'émission

3. **Configurer le fournisseur de paiement**
   
   Allez dans Site Web > Configuration > Fournisseurs de paiement et configurez au moins un fournisseur.

4. **Configurer le travail cron (optionnel)**
   
   Le module inclut un travail cron pour mettre à jour automatiquement le statut des adhésions expirées.

Modèles principaux
------------------

Association Culturelle
~~~~~~~~~~~~~~~~~~~~~~

Le modèle ``associazione.culturale`` gère les informations de l'association :

* Nom et lien vers une entreprise (``res.partner``)
* Informations fiscales (code fiscal, numéro de TVA)
* Coordonnées (téléphone, email, site web)
* Adresse complète
* Logo/icône de l'association
* Relation avec les adhésions émises

Plan d'Adhésion
~~~~~~~~~~~~~~~

Le modèle ``piano.tesseramento`` définit les plans disponibles :

* **Nom** : Nom du plan (ex. "Adhésion annuelle 2024")
* **Type** : 
  
  * ``annuale_solare`` : Expire le 31 décembre de l'année de référence
  * ``calendario`` : Expire 12 mois après la date d'émission
* **Coût** : Frais d'adhésion
* **Année de référence** : Uniquement pour le type année solaire
* **Statut actif** : Si le plan est disponible pour de nouvelles adhésions

Carte d'Adhésion
~~~~~~~~~~~~~~~~

Le modèle ``tessera`` représente une carte d'adhésion émise :

* **Numéro de carte** : Généré automatiquement (format : ASSOCIATION-UTILISATEUR-ANNÉE-NUMÉRO)
* **Membre** : Lien vers le profil du membre
* **Association** : Association de référence
* **Plan** : Plan d'adhésion utilisé
* **Dates** : Date d'émission et date d'expiration (calculées automatiquement)
* **Statut** : 
  
  * ``attiva`` : Adhésion valide et non expirée
  * ``scaduta`` : Date d'expiration dépassée
  * ``annullata`` : Adhésion annulée manuellement
* **Montant payé** : Montant payé pour l'adhésion

Membre
~~~~~~

Le modèle ``associato`` représente un membre :

* Données personnelles (nom légal, prénom légal, nom choisi)
* Email (clé unique)
* Code fiscal (avec option "Je n'ai pas de code fiscal")
* Date et lieu de naissance
* Adresse complète
* Téléphone
* Lien vers ``res.users`` (si l'utilisateur a réclamé le profil)

Flux d'Adhésion
---------------

1. Formulaire d'Adhésion (``/tesseramento``)
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   L'utilisateur doit être authentifié et remplit :
   
   * Association
   * Plan d'adhésion
   * Données fiscales complètes (requises)
   
   Les données fiscales sont enregistrées dans l'utilisateur (``res.users``).

2. Création d'Adhésion en Attente
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Un enregistrement ``tesseramento.pending`` est créé avec le statut ``pending`` et une transaction de paiement. L'utilisateur est redirigé vers la page de paiement.

3. Paiement
   ~~~~~~~~

   L'utilisateur complète le paiement via le fournisseur configuré. Le fournisseur gère le paiement et appelle le callback.

4. Callback de Paiement
   ~~~~~~~~~~~~~~~~~~~~

   Route : ``/tesseramento/payment/return``
   
   Si le paiement est complété :
   
   * Met à jour ``tesseramento.pending`` au statut ``paid``
   * Appelle ``action_completa_tessera()`` qui crée l'adhésion
   * Met à jour le statut à ``completed``
   * Redirige vers ``/tesseramento/success``

5. Page de Succès
   ~~~~~~~~~~~~~~~

   Affiche les détails de l'adhésion créée : numéro de carte, association, plan, dates, montant.

Zone Réservée Utilisateur
--------------------------

Vue "Mes Adhésions" (``/my/tessere``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fonctionnalités disponibles :

* **Adhésion Actuelle** : Affiche l'adhésion active avec avertissement si expirant (dans les 30 jours)
* **Formulaire de Renouvellement** : Permet de renouveler l'adhésion en sélectionnant un nouveau plan
* **Adhésions Passées** : Tableau avec toutes les adhésions expirées ou annulées
* **Réclamer le Profil** : Permet de lier un profil de membre existant à votre compte utilisateur

Calcul de la Date d'Expiration
-------------------------------

Plan Année Solaire
~~~~~~~~~~~~~~~~~~

L'adhésion expire toujours le **31 décembre** de l'année de référence, quelle que soit la date d'émission.

Exemple :
  
  * Émission : 15/06/2024
  * Année de référence : 2024
  * Expiration : 31/12/2024

Plan Calendrier
~~~~~~~~~~~~~~~

L'adhésion expire **365 jours** après la date d'émission.

Exemple :
  
  * Émission : 15/06/2024
  * Expiration : 15/06/2025

Statut d'Adhésion
-----------------

Calcul Automatique
~~~~~~~~~~~~~~~~~~

Le statut est automatiquement calculé en fonction de la date d'expiration :

* Si ``date_expiration < aujourd'hui`` → ``scaduta``
* Si ``date_expiration >= aujourd'hui`` → ``attiva``
* Si statut = ``annullata``, il n'est pas modifié automatiquement

Travail Cron
~~~~~~~~~~~~

Le module inclut un travail cron (``_cron_aggiorna_stati``) qui met à jour automatiquement les adhésions expirées. Configurer comme action planifiée dans Odoo.

Intégration Paiement
--------------------

Fournisseurs Supportés
~~~~~~~~~~~~~~~~~~~~~~

Tout fournisseur configuré dans Odoo qui supporte la devise du plan :

* Stripe
* PayPal
* Autres fournisseurs compatibles avec Odoo Payment

Le premier fournisseur actif et publié est automatiquement utilisé.

Flux de Paiement
~~~~~~~~~~~~~~~~

1. Création d'une transaction avec référence ``TESS-{pending_id}``
2. Redirection vers la page de paiement du fournisseur
3. Callback automatique après le paiement
4. Complétion automatique de l'adhésion

Gestion des Erreurs
~~~~~~~~~~~~~~~~~~~

Si le paiement échoue ou est annulé :

* ``tesseramento.pending`` est marqué comme ``cancelled``
* L'utilisateur voit un message d'erreur
* Peut réessayer le processus d'adhésion

Intégration Newsletter
-----------------------

Pendant le processus d'adhésion, l'utilisateur peut sélectionner les listes de diffusion auxquelles s'abonner. Les listes sélectionnées sont automatiquement associées au contact de diffusion.

Permissions et Sécurité
-----------------------

Le module inclut :

* Groupes de sécurité pour gérer les permissions
* Accès contrôlé aux données des membres
* Protection des données fiscales
* Permissions différenciées pour le backend et le frontend

Support et Assistance
----------------------

Pour le support technique ou les questions :

* Site Web : https://www.vicedominisoftworks.com
* Email : Contacter via le site web

Licence
-------

Autre propriétaire

Auteur
------

Vicedomini Softworks
