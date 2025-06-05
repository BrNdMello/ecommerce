# pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Pedido, ItemPedido
from .forms import FormCriarPedido
from carrinho.cart import Carrinho
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Importações para gerar Pix QR Code
try:
    from pixqrcodegen import Payload
    import qrcode
    import base64
    from io import BytesIO
    PIX_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Bibliotecas PIX não instaladas: {e}")
    PIX_AVAILABLE = False
    Payload = None

@login_required
def criar_pedido(request):
    carrinho = Carrinho(request)
    
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('produtos:lista')

    if request.method == 'POST':
        form = FormCriarPedido(request.POST)
        if form.is_valid():
            try:
                # Criar o pedido
                pedido = form.save(commit=False)
                pedido.usuario = request.user
                pedido.metodo_pagamento = 'pix'
                pedido.status = 'aguardando_pagamento'
                pedido.save()

                # Criar itens do pedido
                for item_data in carrinho:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=item_data['produto'],
                        preco=item_data['preco'],
                        quantidade=item_data['quantidade']
                    )
                
                # Limpar carrinho após criar pedido
                carrinho.limpar()

                # Gerar PIX se disponível
                if PIX_AVAILABLE:
                    try:
                        context_confirmacao = gerar_pix_pedido(pedido)
                        
                        # Enviar email de confirmação (opcional)
                        enviar_email_confirmacao_pedido(pedido)
                        
                        return render(request, 'pedidos/confirmacao_pedido_pix.html', context_confirmacao)
                    
                    except Exception as e:
                        logger.error(f"Erro ao gerar PIX para pedido {pedido.id}: {e}")
                        messages.error(request, "Pedido criado, mas houve um erro ao gerar o PIX. Entre em contato conosco.")
                        return redirect('pedidos:lista_meus_pedidos')
                else:
                    messages.error(request, "Sistema PIX indisponível. Entre em contato conosco.")
                    return redirect('pedidos:lista_meus_pedidos')
                    
            except Exception as e:
                logger.error(f"Erro ao criar pedido: {e}")
                messages.error(request, "Erro interno. Tente novamente ou entre em contato conosco.")
                return redirect('carrinho:detalhe')
        else:
            messages.error(request, "Houve um erro nos dados do pedido. Por favor, verifique e tente novamente.")
    
    else:  # GET
        initial_data = {}
        if request.user.is_authenticated:
            full_name = request.user.get_full_name()
            initial_data['nome'] = full_name if full_name else request.user.username
            initial_data['email'] = request.user.email
        form = FormCriarPedido(initial=initial_data)
    
    return render(request, 'pedidos/criar.html', {
        'carrinho': carrinho, 
        'form': form,
        'pix_available': PIX_AVAILABLE
    })

def gerar_pix_pedido(pedido):
    """Gera o PIX QR Code e payload para um pedido"""
    chave_pix = getattr(settings, 'MINHA_CHAVE_PIX', 'CHAVE_PIX_NAO_CONFIGURADA')
    nome_beneficiario = getattr(settings, 'NOME_BENEFICIARIO_PIX', 'NOME_BENEFICIARIO_NAO_CONFIGURADO')
    cidade_beneficiario = getattr(settings, 'CIDADE_BENEFICIARIO_PIX', 'CIDADE')
    
    valor_pedido = float(pedido.get_total_cost())
    identificador_transacao = f"PEDIDO{pedido.id}"

    # Criar payload PIX
    payload_pix = Payload(
        nome_beneficiario,
        chave_pix,
        valor_pedido,
        cidade_beneficiario,
        identificador_transacao
    )
    
    brcode_string = payload_pix.gerarPayload()

    # Gerar QR Code
    qr_img = qrcode.make(brcode_string)
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return {
        'pedido': pedido,
        'chave_pix_copia_cola': brcode_string,
        'nome_beneficiario': nome_beneficiario,
        'qr_code_base64': qr_code_base64,
        'valor_formatado': f"R$ {valor_pedido:.2f}"
    }

def enviar_email_confirmacao_pedido(pedido):
    """Envia email de confirmação do pedido"""
    try:
        subject = f'Confirmação do Pedido #{pedido.id}'
        html_message = render_to_string('pedidos/email_confirmacao.html', {
            'pedido': pedido,
            'usuario': pedido.usuario
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email de confirmação enviado para pedido {pedido.id}")
    except Exception as e:
        logger.error(f"Erro ao enviar email para pedido {pedido.id}: {e}")

@login_required
def lista_meus_pedidos(request):
    """Lista os pedidos do usuário logado"""
    meus_pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    context = {
        'pedidos': meus_pedidos
    }
    return render(request, 'pedidos/lista_meus_pedidos.html', context)

@login_required
def detalhe_pedido(request, pedido_id):
    """Mostra detalhes de um pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
        'items': pedido.items.all()
    }
    return render(request, 'pedidos/detalhe_pedido.html', context)

def registrar_view(request):
    """View para registro de novos usuários"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.username}! Seu registro foi concluído com sucesso.')
            return redirect('produtos:lista')
        else:
            messages.error(request, 'Houve um erro no seu registro. Por favor, verifique os dados abaixo.')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registrar.html', {'form': form})

# View para webhook PIX (caso você implemente verificação automática)
def webhook_pix(request):
    """Webhook para receber notificações de pagamento PIX"""
    if request.method == 'POST':
        # Implementar lógica de verificação do pagamento
        # Isso depende do seu provedor de pagamentos PIX
        pass
    
    return JsonResponse({'status': 'ok'})