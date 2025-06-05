# pedidos/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.conf import settings
from unittest.mock import patch, Mock, MagicMock
from decimal import Decimal
import json

from .models import Pedido, ItemPedido
from .forms import FormCriarPedido
from produtos.models import Produto, Categoria


class PedidoModelTest(TestCase):
    """Testes para o modelo Pedido"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nome='João Silva',
            email='joao@example.com',
            endereco='Rua Teste, 123',
            cep='12345-678',
            cidade='São Paulo',
            metodo_pagamento='pix'
        )
    
    def test_pedido_creation(self):
        """Testa se o pedido é criado corretamente"""
        self.assertEqual(self.pedido.nome, 'João Silva')
        self.assertEqual(self.pedido.usuario, self.user)
        self.assertEqual(self.pedido.status, 'pendente')  # valor padrão
        self.assertEqual(self.pedido.metodo_pagamento, 'pix')
    
    def test_pedido_str_representation(self):
        """Testa a representação string do pedido"""
        expected = f'Pedido {self.pedido.id}'
        self.assertEqual(str(self.pedido), expected)
    
    def test_status_choices(self):
        """Testa as opções de status"""
        status_values = [choice[0] for choice in Pedido.STATUS_CHOICES]
        expected_statuses = ['pendente', 'aguardando_pagamento', 'pago', 'enviado', 'entregue', 'cancelado']
        
        for status in expected_statuses:
            self.assertIn(status, status_values)
    
    def test_metodo_pagamento_choices(self):
        """Testa as opções de método de pagamento"""
        metodo_values = [choice[0] for choice in Pedido.METODO_PAGAMENTO_CHOICES]
        self.assertIn('pix', metodo_values)
    
    def test_pedido_default_values(self):
        """Testa valores padrão do pedido"""
        pedido = Pedido.objects.create(
            usuario=self.user,
            nome='Teste',
            email='teste@example.com',
            endereco='Endereço teste',
            cep='00000-000',
            cidade='Cidade teste'
        )
        
        self.assertEqual(pedido.status, 'pendente')
        self.assertEqual(pedido.metodo_pagamento, 'pix')
    
    def test_get_total_cost_empty(self):
        """Testa get_total_cost quando não há itens"""
        total = self.pedido.get_total_cost()
        self.assertEqual(total, 0)
    
    def test_pedido_with_user_cascade(self):
        """Testa se o pedido é deletado quando o usuário é deletado"""
        pedido_id = self.pedido.id
        self.user.delete()
        
        with self.assertRaises(Pedido.DoesNotExist):
            Pedido.objects.get(id=pedido_id)


class ItemPedidoModelTest(TestCase):
    """Testes para o modelo ItemPedido"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.categoria = Categoria.objects.create(nome='Eletrônicos')
        self.produto = Produto.objects.create(
            nome='Smartphone',
            preco=Decimal('999.99'),
            categoria=self.categoria
        )
        
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nome='João Silva',
            email='joao@example.com',
            endereco='Rua Teste, 123',
            cep='12345-678',
            cidade='São Paulo'
        )
        
        self.item_pedido = ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            preco=Decimal('999.99'),
            quantidade=2
        )
    
    def test_item_pedido_creation(self):
        """Testa criação do item de pedido"""
        self.assertEqual(self.item_pedido.pedido, self.pedido)
        self.assertEqual(self.item_pedido.produto, self.produto)
        self.assertEqual(self.item_pedido.preco, Decimal('999.99'))
        self.assertEqual(self.item_pedido.quantidade, 2)
    
    def test_item_pedido_str_representation(self):
        """Testa representação string do item de pedido"""
        self.assertEqual(str(self.item_pedido), str(self.item_pedido.id))
    
    def test_get_cost(self):
        """Testa cálculo do custo do item"""
        cost = self.item_pedido.get_cost()
        expected_cost = Decimal('999.99') * 2
        self.assertEqual(cost, expected_cost)
    
    def test_item_pedido_default_quantidade(self):
        """Testa quantidade padrão"""
        item = ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            preco=Decimal('100.00')
        )
        self.assertEqual(item.quantidade, 1)
    
    def test_pedido_get_total_cost_with_items(self):
        """Testa get_total_cost do pedido com itens"""
        # Adiciona outro item
        ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            preco=Decimal('50.00'),
            quantidade=1
        )
        
        total = self.pedido.get_total_cost()
        expected_total = (Decimal('999.99') * 2) + (Decimal('50.00') * 1)
        self.assertEqual(total, expected_total)
    
    def test_item_pedido_cascade_delete(self):
        """Testa se item é deletado quando pedido é deletado"""
        item_id = self.item_pedido.id
        self.pedido.delete()
        
        with self.assertRaises(ItemPedido.DoesNotExist):
            ItemPedido.objects.get(id=item_id)


class FormCriarPedidoTest(TestCase):
    """Testes para o formulário de criar pedido"""
    
    def test_form_fields(self):
        """Testa se o formulário tem os campos corretos"""
        form = FormCriarPedido()
        expected_fields = ['nome', 'email', 'endereco', 'cep', 'cidade']
        
        for field in expected_fields:
            self.assertIn(field, form.fields)
    
    def test_form_valid_data(self):
        """Testa formulário com dados válidos"""
        form_data = {
            'nome': 'João Silva',
            'email': 'joao@example.com',
            'endereco': 'Rua Teste, 123',
            'cep': '12345-678',
            'cidade': 'São Paulo'
        }
        
        form = FormCriarPedido(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_email(self):
        """Testa formulário com email inválido"""
        form_data = {
            'nome': 'João Silva',
            'email': 'email_invalido',
            'endereco': 'Rua Teste, 123',
            'cep': '12345-678',
            'cidade': 'São Paulo'
        }
        
        form = FormCriarPedido(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_required_fields(self):
        """Testa campos obrigatórios"""
        form = FormCriarPedido(data={})
        self.assertFalse(form.is_valid())
        
        required_fields = ['nome', 'email', 'endereco', 'cep', 'cidade']
        for field in required_fields:
            self.assertIn(field, form.errors)


class PedidoViewTest(TestCase):
    """Testes para as views de pedidos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.categoria = Categoria.objects.create(nome='Eletrônicos')
        self.produto = Produto.objects.create(
            nome='Smartphone',
            preco=Decimal('999.99'),
            categoria=self.categoria
        )
        
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nome='João Silva',
            email='joao@example.com',
            endereco='Rua Teste, 123',
            cep='12345-678',
            cidade='São Paulo'
        )
    
    def test_criar_pedido_requires_login(self):
        """Testa se criar pedido requer login"""
        url = reverse('pedidos:criar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect para login
    
    def test_criar_pedido_get_authenticated(self):
        """Testa GET na view criar pedido autenticado"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pedidos:criar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'carrinho')
    
    @patch('pedidos.views.Carrinho')
    def test_criar_pedido_carrinho_vazio(self, mock_carrinho):
        """Testa criar pedido com carrinho vazio"""
        mock_carrinho_instance = Mock()
        mock_carrinho_instance.__bool__ = Mock(return_value=False)
        mock_carrinho.return_value = mock_carrinho_instance
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pedidos:criar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
    
    @patch('pedidos.views.PIX_AVAILABLE', True)
    @patch('pedidos.views.Carrinho')
    @patch('pedidos.views.gerar_pix_pedido')
    @patch('pedidos.views.enviar_email_confirmacao_pedido')
    def test_criar_pedido_post_success(self, mock_email, mock_gerar_pix, mock_carrinho):
        """Testa POST bem-sucedido para criar pedido"""
        # Mock do carrinho
        mock_carrinho_instance = Mock()
        mock_carrinho_instance.__bool__ = Mock(return_value=True)
        mock_carrinho_instance.__iter__ = Mock(return_value=iter([
            {
                'produto': self.produto,
                'preco': Decimal('999.99'),
                'quantidade': 1
            }
        ]))
        mock_carrinho_instance.limpar = Mock()
        mock_carrinho.return_value = mock_carrinho_instance
        
        # Mock do PIX
        mock_gerar_pix.return_value = {
            'pedido': Mock(),
            'chave_pix_copia_cola': 'test_pix_code',
            'qr_code_base64': 'test_qr_code'
        }
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pedidos:criar')
        
        form_data = {
            'nome': 'João Silva',
            'email': 'joao@example.com',
            'endereco': 'Rua Teste, 123',
            'cep': '12345-678',
            'cidade': 'São Paulo'
        }
        
        response = self.client.post(url, form_data)
        
        # Verifica se pedido foi criado
        pedido_criado = Pedido.objects.filter(usuario=self.user).first()
        self.assertIsNotNone(pedido_criado)
        self.assertEqual(pedido_criado.status, 'aguardando_pagamento')
        
        # Verifica se carrinho foi limpo
        mock_carrinho_instance.limpar.assert_called_once()
    
    def test_lista_meus_pedidos_requires_login(self):
        """Testa se lista de pedidos requer login"""
        url = reverse('pedidos:lista_meus_pedidos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_lista_meus_pedidos_authenticated(self):
        """Testa lista de pedidos autenticado"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pedidos:lista_meus_pedidos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pedidos')
        self.assertIn(self.pedido, response.context['pedidos'])
    
    def test_detalhe_pedido_requires_login(self):
        """Testa se detalhe do pedido requer login"""
        url = reverse('pedidos:detalhe_pedido', kwargs={'pedido_id': self.pedido.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_detalhe_pedido_authenticated(self):
        """Testa detalhe do pedido autenticado"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pedidos:detalhe_pedido', kwargs={'pedido_id': self.pedido.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pedido'], self.pedido)
    
    def test_detalhe_pedido_outro_usuario(self):
        """Testa acesso ao pedido de outro usuário"""
        outro_user = User.objects.create_user(
            username='outro_user',
            password='testpass123'
        )
        
        self.client.login(username='outro_user', password='testpass123')
        url = reverse('pedidos:detalhe_pedido', kwargs={'pedido_id': self.pedido.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_registrar_view_get(self):
        """Testa GET na view de registro"""
        url = reverse('pedidos:registrar')  # Assumindo que existe esta URL
        response = self.client.get(url)
        
        # Como a view não está nas URLs fornecidas, vamos testar diretamente
        from pedidos.views import registrar_view
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.method = 'GET'
        response = registrar_view(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_webhook_pix_post(self):
        """Testa webhook PIX"""
        url = reverse('pedidos:webhook_pix')
        response = self.client.post(url, {}, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'ok')


class PedidoPixTest(TestCase):
    """Testes para funcionalidades PIX"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nome='João Silva',
            email='joao@example.com',
            endereco='Rua Teste, 123',
            cep='12345-678',
            cidade='São Paulo'
        )
    
    @patch('pedidos.views.PIX_AVAILABLE', True)
    @patch('pedidos.views.Payload')
    @patch('pedidos.views.qrcode.make')
    def test_gerar_pix_pedido(self, mock_qrcode, mock_payload):
        """Testa geração de PIX para pedido"""
        from pedidos.views import gerar_pix_pedido
        
        # Mock do payload PIX
        mock_payload_instance = Mock()
        mock_payload_instance.gerarPayload.return_value = 'mock_pix_code'
        mock_payload.return_value = mock_payload_instance
        
        # Mock do QR code
        mock_qr_img = Mock()
        mock_qr_img.save = Mock()
        mock_qrcode.return_value = mock_qr_img
        
        # Configura settings para teste
        with self.settings(
            MINHA_CHAVE_PIX='test_key',
            NOME_BENEFICIARIO_PIX='Test Beneficiary',
            CIDADE_BENEFICIARIO_PIX='Test City'
        ):
            result = gerar_pix_pedido(self.pedido)
        
        self.assertIn('pedido', result)
        self.assertIn('chave_pix_copia_cola', result)
        self.assertEqual(result['pedido'], self.pedido)
    
    @patch('pedidos.views.send_mail')
    @patch('pedidos.views.render_to_string')
    def test_enviar_email_confirmacao(self, mock_render, mock_send_mail):
        """Testa envio de email de confirmação"""
        from pedidos.views import enviar_email_confirmacao_pedido
        
        mock_render.return_value = '<html>Test email</html>'
        
        with self.settings(DEFAULT_FROM_EMAIL='test@example.com'):
            enviar_email_confirmacao_pedido(self.pedido)
        
        mock_send_mail.assert_called_once()


class PedidoUrlTest(TestCase):
    """Testes para URLs de pedidos"""
    
    def test_urls_resolve(self):
        """Testa se as URLs resolvem corretamente"""
        urls_to_test = [
            ('pedidos:criar', [], {}),
            ('pedidos:lista_meus_pedidos', [], {}),
            ('pedidos:detalhe_pedido', [], {'pedido_id': 1}),
            ('pedidos:webhook_pix', [], {}),
        ]
        
        for url_name, args, kwargs in urls_to_test:
            try:
                url = reverse(url_name, args=args, kwargs=kwargs)
                self.assertTrue(url)
            except:
                self.fail(f"URL {url_name} não resolve corretamente")


class PedidoIntegrationTest(TestCase):
    """Testes de integração para pedidos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.categoria = Categoria.objects.create(nome='Eletrônicos')
        self.produto = Produto.objects.create(
            nome='Smartphone',
            preco=Decimal('999.99'),
            categoria=self.categoria
        )
    
    def test_fluxo_completo_pedido(self):
        """Testa fluxo completo: login -> criar pedido -> listar -> ver detalhes"""
        # 1. Login
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success)
        
        # 2. Criar pedido (simulado - sem carrinho real)
        pedido = Pedido.objects.create(
            usuario=self.user,
            nome='João Silva',
            email='joao@example.com',
            endereco='Rua Teste, 123',
            cep='12345-678',
            cidade='São Paulo'
        )
        
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto,
            preco=self.produto.preco,
            quantidade=1
        )
        
        # 3. Listar pedidos
        url_lista = reverse('pedidos:lista_meus_pedidos')
        response_lista = self.client.get(url_lista)
        self.assertEqual(response_lista.status_code, 200)
        self.assertContains(response_lista, 'João Silva')
        
        # 4. Ver detalhes
        url_detalhe = reverse('pedidos:detalhe_pedido', kwargs={'pedido_id': pedido.id})
        response_detalhe = self.client.get(url_detalhe)
        self.assertEqual(response_detalhe.status_code, 200)
        self.assertEqual(response_detalhe.context['pedido'], pedido)
        
        # 5. Verificar total do pedido
        total = pedido.get_total_cost()
        self.assertEqual(total, self.produto.preco)


# Mock para testes sem dependências externas
class MockCarrinho:
    """Mock da classe Carrinho para testes"""
    
    def __init__(self, items=None):
        self.items = items or []
    
    def __bool__(self):
        return len(self.items) > 0
    
    def __iter__(self):
        return iter(self.items)
    
    def limpar(self):
        self.items = []