"""
Configuración para pruebas de notificaciones por email
Actualiza las credenciales según tu proveedor de email
"""

# Para Gmail:
SMTP_CONFIG_GMAIL = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_user": "tu_email@gmail.com",
    "email_password": "tu_app_password",  # Usar App Password, no contraseña normal
    "use_tls": True
}

# Para Outlook/Hotmail:
SMTP_CONFIG_OUTLOOK = {
    "smtp_server": "smtp-mail.outlook.com", 
    "smtp_port": 587,
    "email_user": "tu_email@outlook.com",
    "email_password": "tu_contraseña",
    "use_tls": True
}

# Para otros proveedores, consulta la documentación específica

# Instrucciones para Gmail:
# 1. Activar autenticación de 2 pasos en tu cuenta Gmail
# 2. Generar una App Password específica para esta aplicación
# 3. Usar la App Password en lugar de tu contraseña normal

print("""
📧 Configuración de Email para CriptoAI

Para configurar las notificaciones por email:

1. Edita el archivo .env en la carpeta backend
2. Actualiza las siguientes variables:

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587  
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password

⚠️  IMPORTANTE: 
- Para Gmail, usa App Password, no tu contraseña normal
- Activa la autenticación de 2 pasos primero
- Para otros proveedores, consulta su documentación SMTP

🔧 Una vez configurado, las notificaciones automáticas funcionarán correctamente.
""")
