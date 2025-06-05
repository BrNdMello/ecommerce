# Adicione essas configurações no seu settings.py

# ===== CONFIGURAÇÕES PIX =====
# Substitua pelos seus dados reais
MINHA_CHAVE_PIX = "sua-chave-pix@email.com"  # ou CPF, CNPJ, telefone, chave aleatória
NOME_BENEFICIARIO_PIX = "SEU NOME OU EMPRESA"  # Máximo 25 caracteres
CIDADE_BENEFICIARIO_PIX = "SAO PAULO"  # Máximo 15 caracteres, sem acentos

# ===== CONFIGURAÇÕES DE EMAIL (para notificações de pedidos) =====
# Configure seu provedor de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou seu provedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'  # Use senha de aplicativo, não a senha normal
DEFAULT_FROM_EMAIL = 'seu-email@gmail.com'

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
# Para produção, configure essas variáveis
if not DEBUG:
    ALLOWED_HOSTS = ['seudominio.com', 'www.seudominio.com']
    CSRF_TRUSTED_ORIGINS = ['https://seudominio.com', 'https://www.seudominio.com']