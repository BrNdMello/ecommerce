# carrinho/tests.py
from decimal import Decimal
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
from unittest.mock import patch, MagicMock
from produtos.models import Produto
from .cart import Carrinho
from .forms import FormAdicionarProdutoCarrinho


class CarrinhoClassTest(TestCase):
    """Testes para a classe Carrinho"""
    
    def setUp(self):
        self.factory = RequestFactory()
        # Criar produto de teste
        self.produto = Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('10.50'),
            slug="produto-teste"
        )
        
    def get_request_with_session(self, session_data=None):
        """Helper para criar request com sessão"""
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        
        if session_data:
            for key, value in session_data.items():
                request.session[key] = value
            request.session.save()
        
        return request
    
    def test_carrinho_init_nova_sessao(self):
        """Testa inicialização do carrinho com sessão nova"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        self.assertEqual(carrinho.carrinho, {})
        self.assertIn(settings.CARRINHO_SESSION_ID, request.session)
    
    def test_carrinho_init_sessao_existente(self):
        """Testa inicialização do carrinho com sessão existente"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                '1': {'quantidade': 2, 'preco': '10.50'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        self.assertEqual(carrinho.carrinho['1']['quantidade'], 2)
        self.assertEqual(carrinho.carrinho['1']['preco'], '10.50')
    
    def test_adicionar_produto_novo(self):
        """Testa adicionar produto novo ao carrinho"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        carrinho.adicionar(self.produto, quantidade=2)
        
        produto_id = str(self.produto.id)
        self.assertIn(produto_id, carrinho.carrinho)
        self.assertEqual(carrinho.carrinho[produto_id]['quantidade'], 2)
        self.assertEqual(carrinho.carrinho[produto_id]['preco'], str(self.produto.preco))
    
    def test_adicionar_produto_existente_somar(self):
        """Testa adicionar produto existente (somar quantidades)"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        carrinho.adicionar(self.produto, quantidade=3)
        
        produto_id = str(self.produto.id)
        self.assertEqual(carrinho.carrinho[produto_id]['quantidade'], 5)
    
    def test_adicionar_produto_existente_override(self):
        """Testa adicionar produto existente com override"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        carrinho.adicionar(self.produto, quantidade=3, override_quantidade=True)
        
        produto_id = str(self.produto.id)
        self.assertEqual(carrinho.carrinho[produto_id]['quantidade'], 3)
    
    def test_salvar(self):
        """Testa método salvar"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        # Verificar que modified é False inicialmente
        self.assertFalse(request.session.modified)
        
        carrinho.salvar()
        
        # Verificar que modified foi setado para True
        self.assertTrue(request.session.modified)
    
    def test_remover_produto_existente(self):
        """Testa remoção de produto existente"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        carrinho.remover(self.produto)
        
        produto_id = str(self.produto.id)
        self.assertNotIn(produto_id, carrinho.carrinho)
    
    def test_remover_produto_inexistente(self):
        """Testa remoção de produto que não está no carrinho"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        # Não deve gerar erro
        carrinho.remover(self.produto)
        self.assertEqual(len(carrinho.carrinho), 0)
    
    def test_iter(self):
        """Testa iteração sobre o carrinho"""
        produto2 = Produto.objects.create(
            nome="Produto 2",
            preco=Decimal('20.00'),
            slug="produto-2"
        )
        
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'},
                str(produto2.id): {'quantidade': 1, 'preco': '20.00'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        items = list(carrinho)
        
        self.assertEqual(len(items), 2)
        
        # Verificar se os produtos foram adicionados aos items
        produto_ids = [str(item['produto'].id) for item in items]
        self.assertIn(str(self.produto.id), produto_ids)
        self.assertIn(str(produto2.id), produto_ids)
        
        # Verificar cálculos
        for item in items:
            self.assertIsInstance(item['preco'], Decimal)
            self.assertEqual(item['preco_total'], item['preco'] * item['quantidade'])
    
    def test_len(self):
        """Testa método __len__"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'},
                '999': {'quantidade': 3, 'preco': '5.00'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        self.assertEqual(len(carrinho), 5)  # 2 + 3
    
    def test_len_carrinho_vazio(self):
        """Testa método __len__ com carrinho vazio"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        self.assertEqual(len(carrinho), 0)
    
    def test_get_total_price(self):
        """Testa cálculo do preço total"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'},
                '999': {'quantidade': 1, 'preco': '15.00'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        total = carrinho.get_total_price()
        expected = Decimal('10.50') * 2 + Decimal('15.00') * 1
        self.assertEqual(total, expected)
    
    def test_get_total_price_carrinho_vazio(self):
        """Testa preço total com carrinho vazio"""
        request = self.get_request_with_session()
        carrinho = Carrinho(request)
        
        self.assertEqual(carrinho.get_total_price(), Decimal('0'))
    
    def test_limpar(self):
        """Testa limpeza do carrinho"""
        session_data = {
            settings.CARRINHO_SESSION_ID: {
                str(self.produto.id): {'quantidade': 2, 'preco': '10.50'}
            }
        }
        request = self.get_request_with_session(session_data)
        carrinho = Carrinho(request)
        
        carrinho.limpar()
        
        self.assertNotIn(settings.CARRINHO_SESSION_ID, request.session)


class CarrinhoViewsTest(TestCase):
    """Testes para as views do carrinho"""
    
    def setUp(self):
        self.client = Client()
        self.produto = Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('10.50'),
            slug="produto-teste"
        )
    
    def test_detalhe_carrinho_get(self):
        """Testa view de detalhe do carrinho"""
        response = self.client.get(reverse('carrinho:detalhe'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'carrinho')
        self.assertIn('carrinho', response.context)
    
    def test_adicionar_carrinho_post(self):
        """Testa adição de produto ao carrinho via POST"""
        response = self.client.post(
            reverse('carrinho:adicionar', kwargs={'produto_id': self.produto.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('carrinho:detalhe'))
        
        # Verificar se produto foi adicionado à sessão
        session = self.client.session
        carrinho_data = session.get(settings.CARRINHO_SESSION_ID, {})
        self.assertIn(str(self.produto.id), carrinho_data)
    
    def test_adicionar_carrinho_get_nao_permitido(self):
        """Testa que GET não é permitido para adicionar produto"""
        response = self.client.get(
            reverse('carrinho:adicionar', kwargs={'produto_id': self.produto.id})
        )
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_adicionar_carrinho_produto_inexistente(self):
        """Testa adição de produto inexistente"""
        response = self.client.post(
            reverse('carrinho:adicionar', kwargs={'produto_id': 999})
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_remover_carrinho_post(self):
        """Testa remoção de produto do carrinho via POST"""
        # Primeiro adicionar produto
        self.client.post(
            reverse('carrinho:adicionar', kwargs={'produto_id': self.produto.id})
        )
        
        # Depois remover
        response = self.client.post(
            reverse('carrinho:remover', kwargs={'produto_id': self.produto.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('carrinho:detalhe'))
        
        # Verificar se produto foi removido da sessão
        session = self.client.session
        carrinho_data = session.get(settings.CARRINHO_SESSION_ID, {})
        self.assertNotIn(str(self.produto.id), carrinho_data)
    
    def test_remover_carrinho_get_nao_permitido(self):
        """Testa que GET não é permitido para remover produto"""
        response = self.client.get(
            reverse('carrinho:remover', kwargs={'produto_id': self.produto.id})
        )
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_remover_carrinho_produto_inexistente(self):
        """Testa remoção de produto inexistente"""
        response = self.client.post(
            reverse('carrinho:remover', kwargs={'produto_id': 999})
        )
        
        self.assertEqual(response.status_code, 404)


class CarrinhoFormsTest(TestCase):
    """Testes para os formulários do carrinho"""
    
    def test_form_adicionar_produto_valido(self):
        """Testa formulário válido"""
        form_data = {
            'quantidade': 5,
            'override': False
        }
        form = FormAdicionarProdutoCarrinho(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['quantidade'], 5)
        self.assertEqual(form.cleaned_data['override'], False)
    
    def test_form_adicionar_produto_quantidade_invalida(self):
        """Testa formulário com quantidade inválida"""
        form_data = {
            'quantidade': 25,  # Fora do range 1-20
            'override': False
        }
        form = FormAdicionarProdutoCarrinho(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)
    
    def test_form_adicionar_produto_quantidade_string(self):
        """Testa formulário com quantidade como string"""
        form_data = {
            'quantidade': 'abc',
            'override': False
        }
        form = FormAdicionarProdutoCarrinho(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)
    
    def test_form_adicionar_produto_valores_iniciais(self):
        """Testa valores iniciais do formulário"""
        form = FormAdicionarProdutoCarrinho()
        
        self.assertEqual(form.fields['quantidade'].initial, 1)
        self.assertEqual(form.fields['override'].initial, False)
    
    def test_form_adicionar_produto_sem_override(self):
        """Testa formulário sem campo override (opcional)"""
        form_data = {
            'quantidade': 3
            # override não é obrigatório
        }
        form = FormAdicionarProdutoCarrinho(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['quantidade'], 3)
        self.assertEqual(form.cleaned_data['override'], False)  # Valor padrão
    
    def test_form_choices_quantidade(self):
        """Testa as opções disponíveis para quantidade"""
        form = FormAdicionarProdutoCarrinho()
        choices = form.fields['quantidade'].choices
        
        # Verificar se tem 20 opções (1 a 20)
        self.assertEqual(len(choices), 20)
        
        # Verificar primeira e última opção
        self.assertEqual(choices[0], (1, '1'))
        self.assertEqual(choices[19], (20, '20'))
    
    def test_form_widget_override_hidden(self):
        """Testa se campo override é hidden"""
        form = FormAdicionarProdutoCarrinho()
        
        from django import forms
        self.assertIsInstance(
            form.fields['override'].widget, 
            forms.HiddenInput
        )


class CarrinhoURLsTest(TestCase):
    """Testes para URLs do carrinho"""
    
    def test_url_detalhe(self):
        """Testa URL de detalhe do carrinho"""
        url = reverse('carrinho:detalhe')
        self.assertEqual(url, '/carrinho/')
    
    def test_url_adicionar(self):
        """Testa URL para adicionar produto"""
        url = reverse('carrinho:adicionar', kwargs={'produto_id': 1})
        self.assertEqual(url, '/carrinho/adicionar/1/')
    
    def test_url_remover(self):
        """Testa URL para remover produto"""
        url = reverse('carrinho:remover', kwargs={'produto_id': 1})
        self.assertEqual(url, '/carrinho/remover/1/')


class CarrinhoIntegrationTest(TestCase):
    """Testes de integração do carrinho"""
    
    def setUp(self):
        self.client = Client()
        self.produto1 = Produto.objects.create(
            nome="Produto 1",
            preco=Decimal('10.00'),
            slug="produto-1"
        )
        self.produto2 = Produto.objects.create(
            nome="Produto 2",
            preco=Decimal('20.00'),
            slug="produto-2"
        )
    
    def test_fluxo_completo_carrinho(self):
        """Testa fluxo completo: adicionar, visualizar, remover"""
        # 1. Carrinho vazio
        response = self.client.get(reverse('carrinho:detalhe'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Adicionar produto 1
        self.client.post(
            reverse('carrinho:adicionar', kwargs={'produto_id': self.produto1.id})
        )
        
        # 3. Adicionar produto 2
        self.client.post(
            reverse('carrinho:adicionar', kwargs={'produto_id': self.produto2.id})
        )
        
        # 4. Verificar carrinho
        response = self.client.get(reverse('carrinho:detalhe'))
        carrinho = response.context['carrinho']
        self.assertEqual(len(carrinho), 2)  # 2 produtos
        
        # 5. Remover produto 1
        self.client.post(
            reverse('carrinho:remover', kwargs={'produto_id': self.produto1.id})
        )
        
        # 6. Verificar carrinho após remoção
        response = self.client.get(reverse('carrinho:detalhe'))
        carrinho = response.context['carrinho']
        self.assertEqual(len(carrinho), 1)  # 1 produto restante
    
    def test_adicionar_mesmo_produto_multiplas_vezes(self):
        """Testa adicionar o mesmo produto várias vezes"""
        produto_id = self.produto1.id
        
        # Adicionar 3 vezes
        for _ in range(3):
            self.client.post(
                reverse('carrinho:adicionar', kwargs={'produto_id': produto_id})
            )
        
        # Verificar quantidade
        session = self.client.session
        carrinho_data = session.get(settings.CARRINHO_SESSION_ID, {})
        self.assertEqual(carrinho_data[str(produto_id)]['quantidade'], 3)


# Para executar os testes:
# python manage.py test carrinho

# Para ver coverage:
# coverage run --source='.' manage.py test carrinho
# coverage report -m
# coverage html