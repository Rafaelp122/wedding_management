from django.urls import path

from .views import (ContractsPartialView, DownloadContractPDFView,
                    GenerateSignatureLinkView, SignContractExternalView)

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
    path(
        "download-pdf/<int:contract_id>/",
        DownloadContractPDFView.as_view(),
        name="download_pdf",
    ),
]
