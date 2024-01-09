from import_export.widgets import ForeignKeyWidget


class TranslatableForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        translated_field = f'translations__{self.field}'
        if value:
            return self.get_queryset(value, row, *args, **kwargs).get(**{translated_field: value})
        else:
            return None
