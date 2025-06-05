# produtos/tests.py
import os
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import Categoria, Produto


class CategoriaModelTest(TestCase):
    """Testes para o modelo Categoria"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome='Eletrônicos',
            slug='eletronicos'
        )
    
    def test_categoria_creation(self):
        """Testa se a categoria é criada corretamente"""
        self.assertEqual(self.categoria.nome, 'Eletrônicos')
        self.assertEqual(self.categoria.slug, 'eletronicos')
        self.assertEqual(str(self.categoria), 'Eletrônicos')
    
    def test_categoria_str_method(self):
        """Testa o método __str__ da categoria"""
        self.assertEqual(str(self.categoria), 'Eletrônicos')
    
    def test_categoria_get_absolute_url(self):
        """Testa o método get_absolute_url da categoria"""
        expected_url = reverse('produtos:lista_por_categoria', args=[self.categoria.slug])
        self.assertEqual(self.categoria.get_absolute_url(), expected_url)
    
    def test_categoria_slug_unique(self):
        """Testa se o slug da categoria é único"""
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(
                nome='Eletrônicos 2',
                slug='eletronicos'  # Mesmo slug
            )
    
    def test_categoria_max_length_nome(self):
        """Testa o campo nome com tamanho máximo"""
        categoria = Categoria(
            nome='A' * 100,  # 100 caracteres (limite)
            slug='categoria-longa'
        )
        # Não deve gerar erro
        categoria.full_clean()
    
    def test_categoria_nome_too_long(self):
        """Testa nome da categoria muito longo"""
        from django.core.exceptions import ValidationError
        categoria = Categoria(
            nome='A' * 101,  # 101 caracteres (acima do limite)
            slug='categoria-muito-longa'
        )
        with self.assertRaises(ValidationError):
            categoria.full_clean()


class ProdutoModelTest(TestCase):
    """Testes para o modelo Produto"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome='Smartphones',
            slug='smartphones'
        )
        
        # Criar imagem fake para testes
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake_image_content',
            content_type='image/jpeg'
        )
        
        self.produto = Produto.objects.create(
            nome='iPhone 15',
            slug='iphone-15',
            descricao='Último modelo da Apple',
            preco=Decimal('2999.99'),
            estoque=10,
            disponivel=True,
            categoria=self.categoria,
            imagem=self.test_image
        )
    
    def tearDown(self):
        """Limpa arquivos de imagem criados nos testes"""
        if self.produto.imagem:
            if os.path.isfile(self.produto.imagem.path):
                os.remove(self.produto.imagem.path)
    
    def test_produto_creation(self):
        """Testa se o produto é criado corretamente"""
        self.assertEqual(self.produto.nome, 'iPhone 15')
        self.assertEqual(self.produto.slug, 'iphone-15')
        self.assertEqual(self.produto.descricao, 'Último modelo da Apple')
        self.assertEqual(self.produto.preco, Decimal('2999.99'))
        self.assertEqual(self.produto.estoque, 10)
        self.assertTrue(self.produto.disponivel)
        self.assertEqual(self.produto.categoria, self.categoria)
        self.assertIsNotNone(self.produto.data_criacao)
        self.assertIsNotNone(self.produto.data_atualizacao)
    
    def test_produto_str_method(self):
        """Testa o método __str__ do produto"""
        self.assertEqual(str(self.produto), 'iPhone 15')
    
    def test_produto_get_absolute_url(self):
        """Testa o método get_absolute_url do produto"""
        expected_url = reverse('produtos:detalhe', args=[self.produto.id, self.produto.slug])
        self.assertEqual(self.produto.get_absolute_url(), expected_url)
    
    def test_produto_slug_unique(self):
        """Testa se o slug do produto é único"""
        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                nome='iPhone 15 Pro',
                slug='iphone-15',  # Mesmo slug
                descricao='Versão Pro',
                preco=Decimal('3499.99'),
                estoque=5,
                categoria=self.categoria
            )
    
    def test_produto_preco_decimal_places(self):
        """Testa se o preço aceita 2 casas decimais"""
        produto = Produto.objects.create(
            nome='Produto Teste',
            slug='produto-teste',
            descricao='Teste de preço',
            preco=Decimal('99.99'),
            estoque=1,
            categoria=self.categoria
        )
        self.assertEqual(produto.preco, Decimal('99.99'))
    
    def test_produto_estoque_positive(self):
        """Testa se o estoque é um número positivo"""
        produto = Produto(
            nome='Produto Estoque',
            slug='produto-estoque',
            descricao='Teste estoque',
            preco=Decimal('50.00'),
            estoque=-1,  # Negativo
            categoria=self.categoria
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            produto.full_clean()
    
    def test_produto_disponivel_default(self):
        """Testa se o campo disponível tem valor padrão True"""
        produto = Produto.objects.create(
            nome='Produto Default',
            slug='produto-default',
            descricao='Teste default',
            preco=Decimal('100.00'),
            estoque=5,
            categoria=self.categoria
            # Não definindo disponivel
        )
        self.assertTrue(produto.disponivel)
    
    def test_produto_categoria_cascade_delete(self):
        """Testa se o produto é deletado quando a categoria é deletada"""
        categoria_temp = Categoria.objects.create(
            nome='Categoria Temp',
            slug='categoria-temp'
        )
        produto_temp = Produto.objects.create(
            nome='Produto Temp',
            slug='produto-temp',
            descricao='Produto temporário',
            preco=Decimal('50.00'),
            estoque=1,
            categoria=categoria_temp
        )
        
        # Deletar categoria deve deletar o produto
        categoria_temp.delete()
        self.assertFalse(Produto.objects.filter(id=produto_temp.id).exists())


class ProdutosViewsTest(TestCase):
    """Testes para as views do app produtos"""
    
    def setUp(self):
        self.client = Client()
        
        # Criar categorias
        self.categoria1 = Categoria.objects.create(
            nome='Eletrônicos',
            slug='eletronicos'
        )
        self.categoria2 = Categoria.objects.create(
            nome='Roupas',
            slug='roupas'
        )
        
        # Criar produtos
        self.produto1 = Produto.objects.create(
            nome='Smartphone',
            slug='smartphone',
            descricao='Um ótimo smartphone',
            preco=Decimal('999.99'),
            estoque=5,
            disponivel=True,
            categoria=self.categoria1
        )
        
        self.produto2 = Produto.objects.create(
            nome='Camiseta',
            slug='camiseta',
            descricao='Camiseta confortável',
            preco=Decimal('49.99'),
            estoque=10,
            disponivel=True,
            categoria=self.categoria2
        )
        
        self.produto_indisponivel = Produto.objects.create(
            nome='Produto Indisponível',
            slug='produto-indisponivel',
            descricao='Este produto não está disponível',
            preco=Decimal('199.99'),
            estoque=0,
            disponivel=False,
            categoria=self.categoria1
        )
    
    def test_lista_produtos_view(self):
        """Testa a view lista_produtos sem filtro de categoria"""
        url = reverse('produtos:lista')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'Camiseta')
        self.assertNotContains(response, 'Produto Indisponível')  # Não deve aparecer
        
        # Verificar contexto
        self.assertIn('produtos', response.context)
        self.assertIn('categorias', response.context)
        self.assertIsNone(response.context['categoria'])
        
        # Verificar se apenas produtos disponíveis estão no contexto
        produtos = response.context['produtos']
        self.assertEqual(produtos.count(), 2)
        self.assertIn(self.produto1, produtos)
        self.assertIn(self.produto2, produtos)
        self.assertNotIn(self.produto_indisponivel, produtos)
    
    def test_lista_produtos_por_categoria(self):
        """Testa a view lista_produtos filtrada por categoria"""
        url = reverse('produtos:lista_por_categoria', args=[self.categoria1.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertNotContains(response, 'Camiseta')  # Categoria diferente
        
        # Verificar contexto
        self.assertEqual(response.context['categoria'], self.categoria1)
        produtos = response.context['produtos']
        self.assertEqual(produtos.count(), 1)
        self.assertIn(self.produto1, produtos)
    
    def test_lista_produtos_categoria_inexistente(self):
        """Testa a view com categoria que não existe"""
        url = reverse('produtos:lista_por_categoria', args=['categoria-inexistente'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_detalhe_produto_view(self):
        """Testa a view detalhe_produto"""
        url = reverse('produtos:detalhe', args=[self.produto1.id, self.produto1.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'Um ótimo smartphone')
        self.assertContains(response, '999.99')
        
        # Verificar contexto
        self.assertEqual(response.context['produto'], self.produto1)
        self.assertIn('categorias', response.context)
    
    def test_detalhe_produto_indisponivel(self):
        """Testa a view detalhe_produto com produto indisponível"""
        url = reverse('produtos:detalhe', args=[
            self.produto_indisponivel.id, 
            self.produto_indisponivel.slug
        ])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_detalhe_produto_inexistente(self):
        """Testa a view detalhe_produto com produto que não existe"""
        url = reverse('produtos:detalhe', args=[9999, 'produto-inexistente'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_detalhe_produto_slug_incorreto(self):
        """Testa a view detalhe_produto com slug incorreto"""
        url = reverse('produtos:detalhe', args=[self.produto1.id, 'slug-errado'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_templates_utilizados(self):
        """Testa se os templates corretos são utilizados"""
        # Lista de produtos
        url = reverse('produtos:lista')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'produtos/lista.html')
        
        # Detalhe do produto
        url = reverse('produtos:detalhe', args=[self.produto1.id, self.produto1.slug])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'produtos/detalhe.html')
    
    def test_contexto_categorias_sempre_presente(self):
        """Testa se as categorias estão sempre presentes no contexto"""
        # Lista de produtos
        url = reverse('produtos:lista')
        response = self.client.get(url)
        categorias = response.context['categorias']
        self.assertEqual(categorias.count(), 2)
        self.assertIn(self.categoria1, categorias)
        self.assertIn(self.categoria2, categorias)
        
        # Detalhe do produto
        url = reverse('produtos:detalhe', args=[self.produto1.id, self.produto1.slug])
        response = self.client.get(url)
        categorias = response.context['categorias']
        self.assertEqual(categorias.count(), 2)


class ProdutosUrlsTest(TestCase):
    """Testes para as URLs do app produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome='Teste',
            slug='teste'
        )
        self.produto = Produto.objects.create(
            nome='Produto Teste',
            slug='produto-teste',
            descricao='Descrição teste',
            preco=Decimal('100.00'),
            estoque=1,
            categoria=self.categoria
        )
    
    def test_url_lista_produtos(self):
        """Testa a URL da lista de produtos"""
        url = reverse('produtos:lista')
        self.assertEqual(url, '/')
    
    def test_url_lista_por_categoria(self):
        """Testa a URL da lista por categoria"""
        url = reverse('produtos:lista_por_categoria', args=['teste'])
        self.assertEqual(url, '/categoria/teste/')
    
    def test_url_detalhe_produto(self):
        """Testa a URL do detalhe do produto"""
        url = reverse('produtos:detalhe', args=[1, 'produto-teste'])
        self.assertEqual(url, '/1/produto-teste/')
    
    def test_url_patterns_names(self):
        """Testa se os nomes das URLs estão corretos"""
        # Verificar se as URLs reversas funcionam
        try:
            reverse('produtos:lista')
            reverse('produtos:lista_por_categoria', args=['categoria'])
            reverse('produtos:detalhe', args=[1, 'produto'])
        except Exception as e:
            self.fail(f"URL reversa falhou: {e}")


class ProdutosIntegrationTest(TestCase):
    """Testes de integração para o app produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome='Livros',
            slug='livros'
        )
        
        self.produto = Produto.objects.create(
            nome='Django for Beginners',
            slug='django-for-beginners',
            descricao='Aprenda Django do zero',
            preco=Decimal('59.90'),
            estoque=3,
            disponivel=True,
            categoria=self.categoria
        )
    
    def test_fluxo_completo_navegacao(self):
        """Testa o fluxo completo de navegação"""
        client = Client()
        
        # 1. Acessar lista geral de produtos
        response = client.get(reverse('produtos:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django for Beginners')
        
        # 2. Acessar lista por categoria
        response = client.get(reverse('produtos:lista_por_categoria', args=['livros']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django for Beginners')
        
        # 3. Acessar detalhe do produto
        response = client.get(reverse('produtos:detalhe', args=[
            self.produto.id, 
            self.produto.slug
        ]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django for Beginners')
        self.assertContains(response, 'Aprenda Django do zero')
        self.assertContains(response, '59.90')
    
    def test_get_absolute_url_integration(self):
        """Testa se os métodos get_absolute_url funcionam com as URLs"""
        # Categoria
        categoria_url = self.categoria.get_absolute_url()
        response = self.client.get(categoria_url)
        self.assertEqual(response.status_code, 200)
        
        # Produto
        produto_url = self.produto.get_absolute_url()
        response = self.client.get(produto_url)
        self.assertEqual(response.status_code, 200)


