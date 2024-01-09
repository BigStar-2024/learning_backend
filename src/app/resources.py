import tablib
from import_export.resources import ModelResource
from parler.utils.context import switch_language


class TranslatableModelResource(ModelResource):
    def export(self, queryset=None, *args, **kwargs):
        """
        Exports a resource.
        """

        self.before_export(queryset, *args, **kwargs)

        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)

        for obj in self.iter_queryset(queryset):
            for language in obj.get_available_languages():
                with switch_language(obj, language):
                    data.append(self.export_resource(obj))

        # This might be useful for a generalized version

        # for obj in self.iter_queryset(queryset):
        #     try:
        #         for language in obj.get_available_languages():
        #             with switch_language(obj, language):
        #                 data.append(self.export_resource(obj))
        #     except AttributeError:
        #         data.append(self.export_resource(obj))

        self.after_export(queryset, data, *args, **kwargs)

        return data
