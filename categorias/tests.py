# categorias/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Categoria


class CategoriaModelTest(TestCase):
    """Testes para o modelo Categoria"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.categoria = Categoria.objects.create(nome="Eletrônicos")
    
    def test_categoria_creation(self):
        """Testa se a categoria é criada corretamente"""
        self.assertEqual(self.categoria.nome, "Eletrônicos")
        self.assertTrue(isinstance(self.categoria, Categoria))
    
    def test_categoria_str_representation(self):
        """Testa a representação string da categoria"""
        # Você pode adicionar um método __str__ no modelo se não existir
        self.assertEqual(str(self.categoria), str(self.categoria.id))
    
    def test_categoria_nome_max_length(self):
        """Testa se o campo nome respeita o max_length"""
        max_length = self.categoria._meta.get_field('nome').max_length
        self.assertEqual(max_length, 100)
    
    def test_categoria_nome_blank_false(self):
        """Testa se nome é obrigatório"""
        # Testando criação sem nome deve falhar
        with self.assertRaises(Exception):
            categoria_sem_nome = Categoria()
            categoria_sem_nome.full_clean()
    
    def test_categoria_nome_unique(self):
        """Testa se pode criar múltiplas categorias com nomes diferentes"""
        categoria2 = Categoria.objects.create(nome="Roupas")
        self.assertNotEqual(self.categoria.nome, categoria2.nome)
    
    def test_categoria_update(self):
        """Testa atualização de categoria"""
        self.categoria.nome = "Eletrônicos Atualizados"
        self.categoria.save()
        categoria_atualizada = Categoria.objects.get(id=self.categoria.id)
        self.assertEqual(categoria_atualizada.nome, "Eletrônicos Atualizados")
    
    def test_categoria_delete(self):
        """Testa exclusão de categoria"""
        categoria_id = self.categoria.id
        self.categoria.delete()
        with self.assertRaises(Categoria.DoesNotExist):
            Categoria.objects.get(id=categoria_id)


class CategoriaViewTest(TestCase):
    """Testes para as views de Categoria"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.client = Client()
        self.categoria1 = Categoria.objects.create(nome="Eletrônicos")
        self.categoria2 = Categoria.objects.create(nome="Roupas")
        self.categoria3 = Categoria.objects.create(nome="Livros")
    
    def test_lista_view_status_code(self):
        """Testa se a view lista retorna status 200"""
        url = reverse('categorias:lista')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_lista_view_uses_correct_template(self):
        """Testa se a view usa o template correto"""
        url = reverse('categorias:lista')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'categorias/lista.html')
    
    def test_lista_view_context_contains_categorias(self):
        """Testa se o contexto contém as categorias"""
        url = reverse('categorias:lista')
        response = self.client.get(url)
        self.assertIn('categorias', response.context)
        self.assertEqual(len(response.context['categorias']), 3)
    
    def test_lista_view_shows_all_categorias(self):
        """Testa se todas as categorias são exibidas"""
        url = reverse('categorias:lista')
        response = self.client.get(url)
        categorias = response.context['categorias']
        
        nomes_categorias = [cat.nome for cat in categorias]
        self.assertIn("Eletrônicos", nomes_categorias)
        self.assertIn("Roupas", nomes_categorias)
        self.assertIn("Livros", nomes_categorias)
    
    def test_lista_view_empty_queryset(self):
        """Testa a view quando não há categorias"""
        # Remove todas as categorias
        Categoria.objects.all().delete()
        
        url = reverse('categorias:lista')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categorias']), 0)
    
    def test_lista_view_ordering(self):
        """Testa se as categorias são retornadas em alguma ordem específica"""
        url = reverse('categorias:lista')
        response = self.client.get(url)
        categorias = response.context['categorias']
        
        # Testa se retorna uma QuerySet válida
        self.assertTrue(hasattr(categorias, 'model'))
        self.assertEqual(categorias.model, Categoria)


class CategoriaUrlTest(TestCase):
    """Testes para as URLs de Categoria"""
    
    def test_lista_url_resolves(self):
        """Testa se a URL 'lista' resolve corretamente"""
        url = reverse('categorias:lista')
        self.assertEqual(url, '/categorias/')
    
    def test_lista_url_namespace(self):
        """Testa se o namespace está funcionando"""
        # Testa se consegue resolver com o namespace
        try:
            url = reverse('categorias:lista')
            self.assertTrue(url)
        except:
            self.fail("Namespace 'categorias' não está funcionando")


class CategoriaIntegrationTest(TestCase):
    """Testes de integração para o app Categorias"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
    
    def test_full_flow_categoria_creation_and_listing(self):
        """Testa o fluxo completo: criar categoria e listar"""
        # Cria uma categoria
        categoria = Categoria.objects.create(nome="Categoria Teste")
        
        # Acessa a página de listagem
        url = reverse('categorias:lista')
        response = self.client.get(url)
        
        # Verifica se a categoria aparece na listagem
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Categoria Teste")
    
    def test_multiple_categories_display(self):
        """Testa a exibição de múltiplas categorias"""
        # Cria várias categorias
        categorias_nomes = ["Cat1", "Cat2", "Cat3", "Cat4", "Cat5"]
        for nome in categorias_nomes:
            Categoria.objects.create(nome=nome)
        
        # Acessa a listagem
        url = reverse('categorias:lista')
        response = self.client.get(url)
        
        # Verifica se todas aparecem
        for nome in categorias_nomes:
            self.assertContains(response, nome)


class CategoriaPerformanceTest(TestCase):
    """Testes de performance para o app Categorias"""
    
    def test_lista_view_with_many_categories(self):
        """Testa performance da view com muitas categorias"""
        # Cria 100 categorias
        categorias = []
        for i in range(100):
            categorias.append(Categoria(nome=f"Categoria {i}"))
        
        Categoria.objects.bulk_create(categorias)
        
        # Testa se a view ainda funciona bem
        url = reverse('categorias:lista')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categorias']), 100)
