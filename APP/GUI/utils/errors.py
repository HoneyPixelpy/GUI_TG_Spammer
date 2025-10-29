class ConfigDataError(Exception):
    """
    Переносит данные ошибки в конфигурационном файле
    """
    def __init__(self, description, *args):
        super().__init__(*args)
        self.title = "Ошибка в конфигурационном файле."
        self.description = description


class SettingsDataError(Exception):
    """
    Переносит данные ошибки в файле со стороними настройками
    """
    def __init__(self, description, *args):
        super().__init__(*args)
        self.title = "Ошибка в файле со стороними настройками."
        self.description = description


class AccountDataError(Exception):
    """
    Переносит данные ошибки в данных с аккаунтом
    """
    def __init__(self, description, *args):
        super().__init__(*args)
        self.title = "Ошибка в данных аккаунта."
        self.description = description


