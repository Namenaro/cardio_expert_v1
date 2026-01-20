import pytest
import sys
import os

# Добавляем путь к run_pazzle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'run_pazzle'))

try:
    from pazzle_factory import factory

    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORT_SUCCESS = False
    factory = None


class TestPuzzleFactory:

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_factory_exists(self):
        """Тест, что фабрика существует"""
        assert factory is not None

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_available_classes(self):
        """Тест, что фабрика загрузила классы"""
        classes = factory.get_available_classes()
        print(f"Available classes: {classes}")
        assert isinstance(classes, list)
        assert len(classes) > 0

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_gaussian_smooth_exists(self):
        """Тест, что класс GaussianSmooth зарегистрирован"""
        classes = factory.get_available_classes()
        assert 'GaussianSmooth' in classes

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_create_gaussian_smooth_default(self):
        """Тест создания GaussianSmooth с параметрами по умолчанию"""
        # Главное - что создание проходит без ошибок
        puzzle = factory.create('GaussianSmooth', {})
        assert puzzle is not None
        print(f"GaussianSmooth created successfully with default params")

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_create_gaussian_smooth_custom(self):
        """Тест создания GaussianSmooth с кастомными параметрами"""
        args = {'sigma': '3.0', 'kernel_size_t': '0.5'}
        puzzle = factory.create('GaussianSmooth', args)
        assert puzzle is not None
        print(f"GaussianSmooth created successfully with custom params")

    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Cannot import factory")
    def test_create_gaussian_smooth_wrong_type(self):
        """Тест на ошибку при неверном типе параметра"""
        args = {'sigma': 'not_a_number', 'kernel_size_t': '0.3'}

        with pytest.raises(ValueError) as exc_info:
            factory.create('GaussianSmooth', args)

        # Проверяем что ошибка содержит информацию о преобразовании
        error_msg = str(exc_info.value)
        assert 'Failed to convert' in error_msg or 'cannot convert' in error_msg
        print(f"Got expected error: {error_msg}")
