from django.urls import path
from . import views
from .views import PortfolioRootView

urlpatterns = [
path('', PortfolioRootView.as_view(), name='portfolio_root'),
]