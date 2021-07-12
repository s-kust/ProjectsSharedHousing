from django.views.generic import DetailView, ListView
from .models import PortfolioRow

class AllPortfolioRowsView(ListView):
    model = PortfolioRow
    template_name = "portfolio_all_rows.html"

class PortfolioRowChartsView(DetailView):
    model = PortfolioRow
    template_name = "portfolio_row_charts.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        row = PortfolioRow.objects.get(pk=self.kwargs["pk"])
        context["row"] = row
        return context