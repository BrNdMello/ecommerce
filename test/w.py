"""
Testes simples para wsgi.py - Garante 100% de coverage
"""
import os
import sys
from unittest.mock import patch, MagicMock
from django.test import TestCase


class WSGITestCase(TestCase):
    """Testes para garantir 100% coverage do wsgi.py"""
    
    def test_wsgi_import_and_execution(self):
        """Testa importação do módulo wsgi e execução de todas as linhas"""
        
        # Remove o módulo se já foi importado para forçar nova execução
        wsgi_module = 'ecommerce.wsgi'
        if wsgi_module in sys.modules:
            del sys.modules[wsgi_module]
        
        # Mock das funções para capturar as chamadas
        with patch('os.environ.setdefault') as mock_setdefault, \
             patch('django.core.wsgi.get_wsgi_application') as mock_get_wsgi:
            
            # Configura o mock da aplicação WSGI
            mock_app = MagicMock()
            mock_get_wsgi.return_value = mock_app
            
            # Importa o módulo wsgi (executa todas as linhas)
            from ecommerce import wsgi
            
            # Verifica se os.environ.setdefault foi chamado (linha 15)
            mock_setdefault.assert_called_once_with(
                'DJANGO_SETTINGS_MODULE', 
                'ecommerce.settings'
            )
            
            # Verifica se get_wsgi_application foi chamado (linha 16)
            mock_get_wsgi.assert_called_once()
            
            # Verifica se application foi definido (linha 16)
            self.assertEqual(wsgi.application, mock_app)
    
    def test_wsgi_module_attributes(self):
        """Testa se o módulo wsgi tem os atributos corretos"""
        from ecommerce import wsgi
        
        # Verifica se application existe e é callable
        self.assertTrue(hasattr(wsgi, 'application'))
        self.assertTrue(callable(wsgi.application))
        
        # Verifica se os imports estão disponíveis
        self.assertTrue(hasattr(wsgi, 'os'))
        self.assertTrue(hasattr(wsgi, 'get_wsgi_application'))
    
    def test_wsgi_docstring(self):
        """Testa se o módulo tem docstring apropriado"""
        from ecommerce import wsgi
        
        # Verifica se tem docstring
        self.assertIsNotNone(wsgi.__doc__)
        self.assertIn('WSGI config', wsgi.__doc__)


# Teste alternativo usando pytest (se você usar pytest em vez de unittest)
def test_wsgi_coverage():
    """Teste simples para coverage usando pytest"""
    # Remove módulo se já importado
    wsgi_module = 'ecommerce.wsgi'
    if wsgi_module in sys.modules:
        del sys.modules[wsgi_module]
    
    with patch('os.environ.setdefault') as mock_setdefault, \
         patch('django.core.wsgi.get_wsgi_application') as mock_get_wsgi:
        
        mock_app = MagicMock()
        mock_get_wsgi.return_value = mock_app
        
        # Importa e testa
        from ecommerce import wsgi
        
        # Assertions
        mock_setdefault.assert_called_once_with('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
        mock_get_wsgi.assert_called_once()
        assert wsgi.application == mock_app