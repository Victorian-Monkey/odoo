Asociaciones Culturales
========================

Resumen
-------

El módulo **Asociaciones Culturales** para Odoo 19 proporciona una solución completa para la gestión de membresías en línea para todo tipo de asociaciones: culturales, deportivas, voluntarias, recreativas y otras.

Características principales:

* Gestión de asociaciones culturales con información completa
* Planes de membresía configurables (año solar o calendario)
* Sistema de membresía en línea integrado
* Pago en línea a través de proveedores de Odoo
* Área reservada para miembros ("Mis membresías")
* Gestión de datos fiscales y personales
* Integración con boletines y listas de correo

Instalación
-----------

1. Copie la carpeta del módulo en el directorio ``addons`` de su instalación de Odoo 19
2. Actualice la lista de aplicaciones: ``odoo-bin -u all -d your_database``
3. Active el modo desarrollador
4. Vaya a Aplicaciones > Actualizar lista de aplicaciones
5. Busque "Associazioni" e instale el módulo

Requisitos
-----------

* Odoo 19.0
* Módulos requeridos: ``base``, ``website``, ``auth_signup``, ``payment``, ``mail``, ``mass_mailing``

Configuración
-------------

Prerrequisitos
~~~~~~~~~~~~~~

1. Módulo ``payment`` instalado y configurado
2. Al menos un proveedor de pago activo y publicado (Stripe, PayPal, etc.)
3. Usuarios con permisos apropiados

Configuración inicial
~~~~~~~~~~~~~~~~~~~~~

1. **Crear asociaciones culturales**
   
   Vaya a Asociaciones > Asociaciones y cree las asociaciones que gestionará.

2. **Crear planes de membresía**
   
   Vaya a Asociaciones > Planes de Membresía y cree los planes disponibles:
   
   * **Año Solar**: Expira el 31 de diciembre del año de referencia
   * **Calendario**: Expira 12 meses después de la fecha de emisión

3. **Configurar proveedor de pago**
   
   Vaya a Sitio Web > Configuración > Proveedores de Pago y configure al menos un proveedor.

4. **Configurar trabajo cron (opcional)**
   
   El módulo incluye un trabajo cron para actualizar automáticamente el estado de las membresías expiradas.

Modelos Principales
--------------------

Asociación Cultural
~~~~~~~~~~~~~~~~~~~

El modelo ``associazione.culturale`` gestiona la información de la asociación:

* Nombre y enlace a una empresa (``res.partner``)
* Información fiscal (código fiscal, número de IVA)
* Datos de contacto (teléfono, email, sitio web)
* Dirección completa
* Logo/icono de la asociación
* Relación con las membresías emitidas

Plan de Membresía
~~~~~~~~~~~~~~~~~

El modelo ``piano.tesseramento`` define los planes disponibles:

* **Nombre**: Nombre del plan (ej. "Membresía Anual 2024")
* **Tipo**: 
  
  * ``annuale_solare``: Expira el 31 de diciembre del año de referencia
  * ``calendario``: Expira 12 meses después de la fecha de emisión
* **Costo**: Cuota de membresía
* **Año de referencia**: Solo para tipo año solar
* **Estado activo**: Si el plan está disponible para nuevas membresías

Tarjeta de Membresía
~~~~~~~~~~~~~~~~~~~~

El modelo ``tessera`` representa una tarjeta de membresía emitida:

* **Número de tarjeta**: Generado automáticamente (formato: ASOCIACIÓN-USUARIO-AÑO-NÚMERO)
* **Miembro**: Enlace al perfil del miembro
* **Asociación**: Asociación de referencia
* **Plan**: Plan de membresía utilizado
* **Fechas**: Fecha de emisión y fecha de expiración (calculadas automáticamente)
* **Estado**: 
  
  * ``attiva``: Membresía válida y no expirada
  * ``scaduta``: Fecha de expiración pasada
  * ``annullata``: Membresía cancelada manualmente
* **Importe pagado**: Importe pagado por la membresía

Miembro
~~~~~~~

El modelo ``associato`` representa un miembro:

* Datos personales (nombre legal, apellido legal, nombre elegido)
* Email (clave única)
* Código fiscal (con opción "No tengo código fiscal")
* Fecha y lugar de nacimiento
* Dirección completa
* Teléfono
* Enlace a ``res.users`` (si el usuario ha reclamado el perfil)

Flujo de Membresía
------------------

1. Formulario de Membresía (``/tesseramento``)
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   El usuario debe estar autenticado y completa:
   
   * Asociación
   * Plan de membresía
   * Datos fiscales completos (requeridos)
   
   Los datos fiscales se guardan en el usuario (``res.users``).

2. Crear Membresía Pendiente
   ~~~~~~~~~~~~~~~~~~~~~~~~~~

   Se crea un registro ``tesseramento.pending`` con estado ``pending`` y una transacción de pago. El usuario es redirigido a la página de pago.

3. Pago
   ~~~~~

   El usuario completa el pago a través del proveedor configurado. El proveedor gestiona el pago y llama al callback.

4. Callback de Pago
   ~~~~~~~~~~~~~~~~~

   Ruta: ``/tesseramento/payment/return``
   
   Si el pago se completa:
   
   * Actualiza ``tesseramento.pending`` al estado ``paid``
   * Llama a ``action_completa_tessera()`` que crea la membresía
   * Actualiza el estado a ``completed``
   * Redirige a ``/tesseramento/success``

5. Página de Éxito
   ~~~~~~~~~~~~~~~

   Muestra los detalles de la membresía creada: número de tarjeta, asociación, plan, fechas, importe.

Área Reservada del Usuario
---------------------------

Vista "Mis Membresías" (``/my/tessere``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Características disponibles:

* **Membresía Actual**: Muestra la membresía activa con advertencia si está por expirar (dentro de 30 días)
* **Formulario de Renovación**: Permite renovar la membresía seleccionando un nuevo plan
* **Membresías Pasadas**: Tabla con todas las membresías expiradas o canceladas
* **Reclamar Perfil**: Permite vincular un perfil de miembro existente a su cuenta de usuario

Cálculo de Fecha de Expiración
-------------------------------

Plan Año Solar
~~~~~~~~~~~~~~

La membresía siempre expira el **31 de diciembre** del año de referencia, independientemente de la fecha de emisión.

Ejemplo:
  
  * Emisión: 15/06/2024
  * Año de referencia: 2024
  * Expiración: 31/12/2024

Plan Calendario
~~~~~~~~~~~~~~~

La membresía expira **365 días** después de la fecha de emisión.

Ejemplo:
  
  * Emisión: 15/06/2024
  * Expiración: 15/06/2025

Estado de Membresía
--------------------

Cálculo Automático
~~~~~~~~~~~~~~~~~~

El estado se calcula automáticamente según la fecha de expiración:

* Si ``fecha_expiración < hoy`` → ``scaduta``
* Si ``fecha_expiración >= hoy`` → ``attiva``
* Si estado = ``annullata``, no se modifica automáticamente

Trabajo Cron
~~~~~~~~~~~~

El módulo incluye un trabajo cron (``_cron_aggiorna_stati``) que actualiza automáticamente las membresías expiradas. Configurar como acción programada en Odoo.

Integración de Pagos
--------------------

Proveedores Soportados
~~~~~~~~~~~~~~~~~~~~~~~

Cualquier proveedor configurado en Odoo que soporte la moneda del plan:

* Stripe
* PayPal
* Otros proveedores compatibles con Odoo Payment

El primer proveedor activo y publicado se utiliza automáticamente.

Flujo de Pago
~~~~~~~~~~~~~

1. Creación de transacción con referencia ``TESS-{pending_id}``
2. Redirección a la página de pago del proveedor
3. Callback automático después del pago
4. Finalización automática de la membresía

Manejo de Errores
~~~~~~~~~~~~~~~~~

Si el pago falla o se cancela:

* ``tesseramento.pending`` se marca como ``cancelled``
* El usuario ve un mensaje de error
* Puede reintentar el proceso de membresía

Integración de Boletín
-----------------------

Durante el proceso de membresía, el usuario puede seleccionar las listas de correo a las que suscribirse. Las listas seleccionadas se asocian automáticamente con el contacto de correo.

Permisos y Seguridad
--------------------

El módulo incluye:

* Grupos de seguridad para gestionar permisos
* Acceso controlado a los datos de miembros
* Protección de datos fiscales
* Permisos diferenciados para backend y frontend

Soporte y Asistencia
--------------------

Para soporte técnico o preguntas:

* Sitio Web: https://www.vicedominisoftworks.com
* Email: Contactar a través del sitio web

Licencia
---------

Otra propietaria

Autor
-----

Vicedomini Softworks
