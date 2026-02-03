Cultural Associations
======================

Overview
--------

The **Cultural Associations** module for Odoo 19 provides a complete solution for managing online membership subscriptions for all types of associations: cultural, sports, volunteer, recreational, and others.

Main features:

* Management of cultural associations with complete information
* Configurable membership plans (solar year or calendar)
* Integrated online membership system
* Online payment via Odoo providers
* Reserved area for members ("My Memberships")
* Management of tax and personal data
* Integration with newsletter and mailing lists

Installation
------------

1. Copy the module folder to the ``addons`` directory of your Odoo 19 installation
2. Update the app list: ``odoo-bin -u all -d your_database``
3. Enable developer mode
4. Go to Apps > Update Apps List
5. Search for "Associazioni" and install the module

Requirements
------------

* Odoo 19.0
* Required modules: ``base``, ``website``, ``auth_signup``, ``payment``, ``mail``, ``mass_mailing``

Configuration
-------------

Prerequisites
~~~~~~~~~~~~~

1. ``payment`` module installed and configured
2. At least one active and published payment provider (Stripe, PayPal, etc.)
3. Users with appropriate permissions

Initial Setup
~~~~~~~~~~~~~

1. **Create cultural associations**
   
   Go to Associations > Associations and create the associations you will manage.

2. **Create membership plans**
   
   Go to Associations > Membership Plans and create the available plans:
   
   * **Solar Year**: Expires on December 31 of the reference year
   * **Calendar**: Expires 12 months after the issue date

3. **Configure payment provider**
   
   Go to Website > Configuration > Payment Providers and configure at least one provider.

4. **Configure cron job (optional)**
   
   The module includes a cron job to automatically update the status of expired memberships.

Main Models
-----------

Cultural Association
~~~~~~~~~~~~~~~~~~~~

The ``associazione.culturale`` model manages association information:

* Name and link to a company (``res.partner``)
* Tax information (tax code, VAT number)
* Contact details (phone, email, website)
* Complete address
* Association logo/icon
* Relationship with issued memberships

Membership Plan
~~~~~~~~~~~~~~~

The ``piano.tesseramento`` model defines available plans:

* **Name**: Plan name (e.g., "Annual Membership 2024")
* **Type**: 
  
  * ``annuale_solare``: Expires on December 31 of the reference year
  * ``calendario``: Expires 12 months after the issue date
* **Cost**: Membership fee
* **Reference year**: Only for solar year type
* **Active status**: Whether the plan is available for new memberships

Membership Card
~~~~~~~~~~~~~~

The ``tessera`` model represents an issued membership card:

* **Card number**: Automatically generated (format: ASSOCIATION-USER-YEAR-NUMBER)
* **Member**: Link to the member profile
* **Association**: Reference association
* **Plan**: Membership plan used
* **Dates**: Issue date and expiration date (automatically calculated)
* **Status**: 
  
  * ``attiva``: Valid and not expired membership
  * ``scaduta``: Expiration date passed
  * ``annullata``: Manually cancelled membership
* **Amount paid**: Amount paid for the membership

Member
~~~~~~

The ``associato`` model represents a member:

* Personal data (legal name, legal surname, chosen name)
* Email (unique key)
* Tax code (with "I don't have a tax code" option)
* Date and place of birth
* Complete address
* Phone
* Link to ``res.users`` (if the user has claimed the profile)

Membership Flow
---------------

1. Membership Form (``/tesseramento``)
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   The user must be authenticated and fills in:
   
   * Association
   * Membership plan
   * Complete tax data (required)
   
   Tax data is saved in the user (``res.users``).

2. Create Pending Membership
   ~~~~~~~~~~~~~~~~~~~~~~~~~~

   A ``tesseramento.pending`` record is created with ``pending`` status and a payment transaction. The user is redirected to the payment page.

3. Payment
   ~~~~~~~~

   The user completes payment via the configured provider. The provider handles payment and calls the callback.

4. Payment Callback
   ~~~~~~~~~~~~~~~~~

   Route: ``/tesseramento/payment/return``
   
   If payment is completed:
   
   * Updates ``tesseramento.pending`` to ``paid`` status
   * Calls ``action_completa_tessera()`` which creates the membership
   * Updates status to ``completed``
   * Redirects to ``/tesseramento/success``

5. Success Page
   ~~~~~~~~~~~~~

   Shows details of the created membership: card number, association, plan, dates, amount.

User Reserved Area
-----------------

"My Memberships" View (``/my/tessere``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Available features:

* **Current Membership**: Shows the active membership with warning if expiring (within 30 days)
* **Renewal Form**: Allows renewing the membership by selecting a new plan
* **Past Memberships**: Table with all expired or cancelled memberships
* **Claim Profile**: Allows linking an existing member profile to your user account

Expiration Date Calculation
---------------------------

Solar Year Plan
~~~~~~~~~~~~~~~

The membership always expires on **December 31** of the reference year, regardless of the issue date.

Example:
  
  * Issue: 15/06/2024
  * Reference year: 2024
  * Expiration: 31/12/2024

Calendar Plan
~~~~~~~~~~~~~

The membership expires **365 days** after the issue date.

Example:
  
  * Issue: 15/06/2024
  * Expiration: 15/06/2025

Membership Status
-----------------

Automatic Calculation
~~~~~~~~~~~~~~~~~~~~~

Status is automatically calculated based on expiration date:

* If ``expiration_date < today`` → ``scaduta``
* If ``expiration_date >= today`` → ``attiva``
* If status = ``annullata``, it is not automatically modified

Cron Job
~~~~~~~~

The module includes a cron job (``_cron_aggiorna_stati``) that automatically updates expired memberships. Configure as a scheduled action in Odoo.

Payment Integration
-------------------

Supported Providers
~~~~~~~~~~~~~~~~~~~

Any provider configured in Odoo that supports the plan currency:

* Stripe
* PayPal
* Other providers compatible with Odoo Payment

The first active and published provider is automatically used.

Payment Flow
~~~~~~~~~~~~

1. Create transaction with reference ``TESS-{pending_id}``
2. Redirect to provider payment page
3. Automatic callback after payment
4. Automatic membership completion

Error Handling
~~~~~~~~~~~~~~

If payment fails or is cancelled:

* ``tesseramento.pending`` is marked as ``cancelled``
* User sees an error message
* Can retry the membership process

Newsletter Integration
----------------------

During the membership process, the user can select mailing lists to subscribe to. Selected lists are automatically associated with the mailing contact.

Permissions and Security
------------------------

The module includes:

* Security groups to manage permissions
* Controlled access to member data
* Protection of tax data
* Differentiated permissions for backend and frontend

Support and Assistance
----------------------

For technical support or questions:

* Website: https://www.vicedominisoftworks.com
* Email: Contact via website

License
-------

Other proprietary

Author
------

Vicedomini Softworks
