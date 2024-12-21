class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ParserNoMatchingInfoException(Exception):
    """Вызывается, когда не найдена запрашиваемая информация в теге."""
    def __init__(self, message, more_info):
        super().__init__(message)
        self.extra_info = more_info
