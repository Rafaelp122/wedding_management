from django.urls import path

from .views import (CancelContractView, ContractsPartialView, EditContractView,
                    GenerateSignatureLinkView, SignContractExternalView,
                    UploadContractView, download_contract_pdf)

app_name = "contracts"

urlpatterns = [
    path("partial/<int:wedding_id>/", ContractsPartialView.as_view(), name="partial_contracts"),
    path("generate-link/<int:contract_id>/", GenerateSignatureLinkView.as_view(), name="generate_link"),
    path("sign/<uuid:token>/", SignContractExternalView.as_view(), name="sign_contract"),
    path("download-pdf/<int:contract_id>/", download_contract_pdf, name="download_pdf"),
    path("cancel/<int:contract_id>/", CancelContractView.as_view(), name="cancel_contract"),
    path("edit/<int:contract_id>/", EditContractView.as_view(), name="edit_contract"),
    path("upload/<int:contract_id>/", UploadContractView.as_view(), name="upload_contract"),
]
