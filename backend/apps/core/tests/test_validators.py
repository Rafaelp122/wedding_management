from unittest.mock import MagicMock, PropertyMock

import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import MaxFileSizeValidator


class TestMaxFileSizeValidator:
    def test_valid_file_under_limit_passes(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        file_mock.size = 5 * 1024 * 1024

        validator(file_mock)

    def test_file_exactly_at_limit_passes(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        file_mock.size = 10 * 1024 * 1024

        validator(file_mock)

    def test_file_over_limit_raises_validation_error(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        file_mock.size = 15 * 1024 * 1024

        with pytest.raises(ValidationError) as exc_info:
            validator(file_mock)

        assert exc_info.value.code == "max_file_size"
        assert "10MB" in str(exc_info.value)

    def test_size_none_bypasses_validation(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        file_mock.size = None

        validator(file_mock)

    def test_oserror_bypasses_validation(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        type(file_mock).size = PropertyMock(side_effect=OSError("storage offline"))

        validator(file_mock)

    def test_filenotfounderror_bypasses_validation(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        file_mock = MagicMock()
        type(file_mock).size = PropertyMock(
            side_effect=FileNotFoundError("file deleted from storage")
        )

        validator(file_mock)

    def test_equality_same_max_size(self):
        v1 = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        v2 = MaxFileSizeValidator(max_size=10 * 1024 * 1024)

        assert v1 == v2

    def test_equality_different_max_size(self):
        v1 = MaxFileSizeValidator(max_size=10 * 1024 * 1024)
        v2 = MaxFileSizeValidator(max_size=5 * 1024 * 1024)

        assert v1 != v2

    def test_equality_different_type(self):
        v1 = MaxFileSizeValidator(max_size=10 * 1024 * 1024)

        assert v1 != "not a validator"

    def test_deconstruct_returns_path_args_kwargs(self):
        validator = MaxFileSizeValidator(max_size=10 * 1024 * 1024)

        path, args, kwargs = validator.deconstruct()

        assert path == "apps.core.validators.MaxFileSizeValidator"
        assert args == (10 * 1024 * 1024,)
        assert kwargs == {}
