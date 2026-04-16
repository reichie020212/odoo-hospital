FROM odoo:19.0

USER root
COPY --chown=odoo:odoo hms_base        /mnt/extra-addons/odoo-hospital/hms_base
COPY --chown=odoo:odoo hms_appointment /mnt/extra-addons/odoo-hospital/hms_appointment
COPY --chown=odoo:odoo hms_clinical    /mnt/extra-addons/odoo-hospital/hms_clinical
COPY --chown=odoo:odoo hms_billing     /mnt/extra-addons/odoo-hospital/hms_billing
USER odoo
