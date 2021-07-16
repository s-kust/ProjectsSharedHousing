from django.conf import settings
from django.views.generic import DetailView, ListView
from .models import PortfolioRow, Portfolio

class AllPortfolioRowsView(ListView):
    model = PortfolioRow
    template_name = "portfolio_all_rows.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio_objects = Portfolio.objects.all()
        assert len(portfolio_objects) == 1
        context["modified_date"] = portfolio_objects[0].modified.date()
        return context

class PortfolioRowChartsView(DetailView):
    model = PortfolioRow
    template_name = "portfolio_row_charts.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        row = PortfolioRow.objects.get(pk=self.kwargs["pk"])
        context["row"] = row
        return context