FROM odoo:19.0

USER root

# MVP modules
COPY --chown=odoo:odoo hms_base             /mnt/extra-addons/odoo-hospital/hms_base
COPY --chown=odoo:odoo hms_appointment      /mnt/extra-addons/odoo-hospital/hms_appointment
COPY --chown=odoo:odoo hms_clinical         /mnt/extra-addons/odoo-hospital/hms_clinical
COPY --chown=odoo:odoo hms_billing          /mnt/extra-addons/odoo-hospital/hms_billing

# Phase 2 modules
COPY --chown=odoo:odoo hms_pharmacy         /mnt/extra-addons/odoo-hospital/hms_pharmacy
COPY --chown=odoo:odoo hms_lab              /mnt/extra-addons/odoo-hospital/hms_lab
COPY --chown=odoo:odoo hms_inpatient        /mnt/extra-addons/odoo-hospital/hms_inpatient
COPY --chown=odoo:odoo hms_portal           /mnt/extra-addons/odoo-hospital/hms_portal

# Billing bridges (auto-install)
COPY --chown=odoo:odoo hms_lab_billing      /mnt/extra-addons/odoo-hospital/hms_lab_billing
COPY --chown=odoo:odoo hms_pharmacy_billing /mnt/extra-addons/odoo-hospital/hms_pharmacy_billing

# Insurance
COPY --chown=odoo:odoo hms_insurance        /mnt/extra-addons/odoo-hospital/hms_insurance

# Public website
COPY --chown=odoo:odoo hms_website          /mnt/extra-addons/odoo-hospital/hms_website

# Security policy (admin-only password management)
COPY --chown=odoo:odoo hms_lockdown         /mnt/extra-addons/odoo-hospital/hms_lockdown

# Config
COPY --chown=odoo:odoo odoo.conf            /etc/odoo/odoo.conf

USER odoo
