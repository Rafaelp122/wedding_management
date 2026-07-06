import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.logistics.schemas import ContractOut
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.tenants.models import Company
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
def test_contract_out_resolvers_no_extra_queries():
    """
    Verifies that ContractOut resolvers do NOT trigger extra queries when
    annotated data is available.
    """
    company = Company.objects.create(name="Bolt Performance", slug="bolt-perf")
    wedding = WeddingFactory(company=company)
    supplier = SupplierFactory(company=company)

    # Create 5 contracts
    ContractFactory.create_batch(5, wedding=wedding, company=company, supplier=supplier)

    # Get contracts via service which annotates fields
    qs = ContractService.list(company, wedding_id=wedding.uuid)
    contract_list = list(qs)

    # Measure queries during serialization
    with CaptureQueriesContext(connection) as ctx:
        for obj in contract_list:
            data = ContractOut.from_orm(obj)
            # Verify data integrity
            assert data.supplier_name == supplier.name
            assert data.addendums_count == 0

    print(f"\nQueries captured during serialization: {len(ctx)}")
    assert len(ctx) == 0, f"Expected 0 queries during serialization, but got {len(ctx)}"


@pytest.mark.django_db
def test_contract_service_list_annotations():
    """
    Verifies that addendums_count is correctly calculated using Subquery.
    """
    company = Company.objects.create(name="Bolt Performance", slug="bolt-perf")
    wedding = WeddingFactory(company=company)

    parent = ContractFactory(wedding=wedding, company=company)
    ContractFactory.create_batch(3, wedding=wedding, company=company, parent=parent)

    qs = ContractService.list(company, wedding_id=wedding.uuid)
    parent_contract = next(c for c in qs if c.uuid == parent.uuid)

    assert parent_contract.addendums_count == 3
    print(f"\nAddendums count verified: {parent_contract.addendums_count}")
