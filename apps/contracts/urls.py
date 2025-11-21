from django.urls import path
from .views import (
    ContractsPartialView, 
    GenerateSignatureLinkView, 
    SignContractExternalView,
    download_contract_pdf # <--- Importe a nova view
)

app_name = "contracts"

urlpatterns = [
    path(
        "partial/<int:wedding_id>/",
        ContractsPartialView.as_view(),
        name="partial_contracts",
    ),
    path(
        "generate-link/<int:contract_id>/",
        GenerateSignatureLinkView.as_view(),
        name="generate_link",
    ),
    path(
        "sign/<uuid:token>/",
        SignContractExternalView.as_view(),
        name="sign_contract",
    ),
    # NOVA ROTA DE PDF
    path(
        "download-pdf/<int:contract_id>/",
        download_contract_pdf,
        name="download_pdf",
    ),
]