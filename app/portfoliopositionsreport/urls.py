from django.urls import path
from . import views
from .views import AllPortfolioRowsView, PortfolioRowChartsView
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
path('', AllPortfolioRowsView.as_view(), name='portfolio_root'),
path('<int:pk>/', PortfolioRowChartsView.as_view(), name='row_charts'),
]
# urlpatterns += staticfiles_urlpatterns()