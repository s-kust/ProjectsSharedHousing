from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.decorators.http import require_POST
from django.http import HttpResponseServerError
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from schemas.models import *
from .forms import DataSchemaForm


class AllSchemasView(ListView):
    model = DataSchemas
    template_name = "all_schemas.html"


@require_POST
def delete_schema(request, primary_key):
    if request.method:
        query = get_object_or_404(DataSchemas, pk=primary_key)
        query.delete()
    return redirect("all_schemas")


class SchemaView(TemplateView):
    template_name = "schema_create_update.html"

    subclasses = [
        str(subClass).split(".")[-1][:-2].lower()
        for subClass in SchemaColumn.__subclasses__()
    ]
    # currently, ['integerColumn', 'fullnameColumn', 'jobColumn', 'companyColumn', 'phoneColumn']

    column_type_switcher = {
        "integercolumn": INTEGER_CH,
        "fullnamecolumn": FULLNAME_CH,
        "jobcolumn": JOB_CH,
        "companycolumn": COMPANY_CH,
        "phonecolumn": PHONE_CH,
    }

    @classmethod
    def _determine_primary_key(cls, input_data):
        numbers_filtered = [int(s) for s in input_data.split("_") if s.isdigit()]
        return numbers_filtered[0]

    def save_schema_columns(self, schema, form):
        # print("Inside save_schema_columns function")
        # print(self.subclasses)
        schema_columns = schema.schemacolumn_set.all()
        for column in schema_columns:
            column_name_field_name = "col_name_%s" % (column.pk,)
            column_order_field_name = "col_order_%s" % (column.pk,)
            column_type_field_name = "col_type_%s" % (column.pk,)
            type_form = form.cleaned_data[column_type_field_name]
            type_changed = False
            for subclass in self.subclasses:
                if not hasattr(column, subclass):
                    continue
                type_db = self.column_type_switcher.get(subclass)
                if type_db == type_form:
                    break
                new_class = globals()[type_form]
                new_column = new_class()
                new_column.schema = schema
                column.delete()
                self._coumn_fill_save(new_column, form, column_name_field_name, column_order_field_name)
                type_changed = True
                break
            if not type_changed:
                self._coumn_fill_save(column, form, column_name_field_name, column_order_field_name)

    @classmethod
    def _coumn_fill_save(cls, column_input, form_input, name_field_name_input, order_field_name_input):
        column_input.name = form_input.cleaned_data[name_field_name_input]
        column_input.order = form_input.cleaned_data[order_field_name_input]
        column_input.save()

    def get_general_column_form(self, model_class, column_pk):
        class ColumnFormGeneral(ModelForm):
            def __init__(self, *args, **kwargs):
                super(ColumnFormGeneral, self).__init__(*args, **kwargs)
                self.helper = FormHelper(self)
                save_chng_btn = "save_schema_columns_chng_btn_%s" % (column_pk,)
                self.helper.layout.append(Submit(save_chng_btn, "Save changes"))

            class Meta:
                model = model_class
                exclude = ["schema", "order"]

        return ColumnFormGeneral

    def process_btn_add_column(self, elem, form_data):
        # print('Add Column button processing')
        primary_key_determined = self._determine_primary_key(elem)
        form = DataSchemaForm(form_data, schema_pk=primary_key_determined)
        if form.is_valid():
            schema = get_object_or_404(DataSchemas, pk=primary_key_determined)
            new_column_type = form.cleaned_data["add_column_type"]
            new_column = globals()[new_column_type]()
            new_column.name = form.cleaned_data["add_column_name"]
            new_column.order = form.cleaned_data["add_column_order"]
            new_column.schema = schema
            try:
                new_column.save()
            except Exception:
                pass
        else:
            return HttpResponseServerError()
        return (primary_key_determined, None)

    def process_btn_delete_column(self, elem, form_data):
        # print('Delete Column button processing')
        column_pk = self._determine_primary_key(elem)
        primary_key_to_return = SchemaColumn.objects.get(pk=column_pk).schema.pk
        # self.pk = SchemaColumn.objects.get(pk=column_pk).schema.pk
        SchemaColumn.objects.get(pk=column_pk).delete()
        return (primary_key_to_return, None)

    def process_btn_edit_column_details(self, elem, form_data):
        # print('Edit Column details button processing')
        column_pk = self._determine_primary_key(elem)
        column = get_object_or_404(SchemaColumn, pk=column_pk)
        # self.pk = column.schema.pk
        for subclass in self.subclasses:
            if hasattr(column, subclass):
                column_model = apps.get_model("schemas", subclass)
                column = get_object_or_404(column_model, pk=column_pk)

                # from pprint import pprint
                # print()
                # pprint(vars(column))
                # print()
                # print(model_to_dict(column, fields=[field.name for field in column._meta.fields]))

                form_class = self.get_general_column_form(column_model, column_pk)
                form = form_class(
                    initial=model_to_dict(
                        column, fields=[field.name for field in column._meta.fields]
                    )
                )
                break
        return (None, form)

    def process_btn_submit_form(self, elem, form_data):
        # print('Submit Form button processing')
        determined_primary_key = self._determine_primary_key(elem)
        form = DataSchemaForm(form_data, schema_pk=determined_primary_key)
        if form.is_valid():
            schema = get_object_or_404(DataSchemas, pk=determined_primary_key)
            schema.name = form.cleaned_data["name"]
            schema.column_separator = form.cleaned_data["column_separator"]
            schema.string_character = form.cleaned_data["string_character"]
            schema.save()
            self.save_schema_columns(schema, form)
        else:
            return HttpResponseServerError()
        return (determined_primary_key, None)

    def process_btn_save_chng_column(self, elem, form_data):
        # print('Save Changes in Column button processing')
        column_pk = self._determine_primary_key(elem)
        column = get_object_or_404(SchemaColumn, pk=column_pk)
        determined_primary_key = column.schema.pk
        # self.pk = column.schema.pk
        for subclass in self.subclasses:
            if not hasattr(column, subclass):
                continue
            column_model = apps.get_model("schemas", subclass)
            column = get_object_or_404(column_model, pk=column_pk)
            form_class = self.get_general_column_form(column_model, column_pk)
            form = form_class(data=form_data, instance=column)

            # from pprint import pprint
            # print()
            # print('Before form save')
            # pprint(vars(column))
            # print()

            if form.is_valid():
                form.save()
            else:
                return (determined_primary_key, form)

            # from pprint import pprint
            # print()
            # print('After form save')
            # pprint(vars(column))
            # print()
        return (determined_primary_key, None)

    btn_functions = {
        "add_new_col": process_btn_add_column,
        "delete_col": process_btn_delete_column,
        "edit_col": process_btn_edit_column_details,
        "submit_form": process_btn_submit_form,
        "save_schema_columns_chng": process_btn_save_chng_column,
    }

    def post(self, request, *args, **kwargs):
        # print()
        # print('Inside SchemaView post')
        # print(request.POST)
        # print()
        # print(self.kwargs)
        # print()
        context = self.get_context_data()
        determined_primary_key = self.kwargs.get("pk", None)
        if determined_primary_key is not None:
            try:
                _ = DataSchemas.objects.get(pk=determined_primary_key)
            except ObjectDoesNotExist:
                return redirect("all_schemas")
        form = None
        btn_pressed = None
        for key in request.POST:
            btn_pressed = self._determine_button_type(key)
            if btn_pressed is None:
                continue            
            funt_to_call = self.btn_functions.get(btn_pressed)
            determined_primary_key, form = funt_to_call(self, key, form_data=request.POST)
            break
        if form is None:
            form = DataSchemaForm(schema_pk=determined_primary_key)
        context["form"] = form
        return super().render_to_response({"form": context["form"]})

    @classmethod
    def _determine_button_type(cls, input_key):
        if input_key.startswith("delete_col_"):
            return "delete_col"
        if input_key.startswith("edit_col_"):
            return "edit_col"
        if input_key.startswith("add_column_btn_"):
            return "add_new_col"
        if input_key.startswith("submit_form_"):
            return "submit_form"
        if input_key.startswith("save_schema_columns_chng_btn_"):
            return "save_schema_columns_chng"
        return None
    
    def get_context_data(self, **kwargs):
        context = super(SchemaView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return redirect("all_schemas")
