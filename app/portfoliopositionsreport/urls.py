from django.urls import path
from . import views
from .views import AllPortfolioRowsView, PortfolioRowChartsView

urlpatterns = [
path('', AllPortfolioRowsView.as_view(), name='portfolio_root'),
path('<int:pk>/', PortfolioRowChartsView.as_view(), name='row_charts'),
]
