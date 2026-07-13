import { test, expect } from "../fixtures/auth.fixture";
import { faker } from "@faker-js/faker";
import { WeddingsListPage, generateWeddingData } from "../pages/weddings-list.page";
import { WeddingDetailPage } from "../pages/wedding-detail.page";

test.describe("Weddings CRUD", () => {
  test("@critical Criar casamento com dados válidos aparece na listagem", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();
    const data = generateWeddingData();
    await weddingsList.createWedding(data);

    const fullName = `${data.groom_name} & ${data.bride_name}`;
    await weddingsList.expectToastSuccess(/Casamento criado com sucesso!/);
    await weddingsList.expectRowVisible(fullName);
  });

  test("@critical Editar casamento reflete dados atualizados", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();
    const data = generateWeddingData();
    await weddingsList.createWedding(data);

    const oldName = `${data.groom_name} & ${data.bride_name}`;
    const newGroom = "Editado " + faker.person.fullName();
    await weddingsList.editWedding(oldName, { groom_name: newGroom });

    const newName = `${newGroom} & ${data.bride_name}`;
    await weddingsList.expectRowVisible(newName);
  });

  test("@critical Deletar casamento via diálogo de confirmação o remove da listagem", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();
    const data = generateWeddingData();
    await weddingsList.createWedding(data);

    const name = `${data.groom_name} & ${data.bride_name}`;
    await weddingsList.deleteWedding(name);

    await weddingsList.expectToastSuccess(/Casamento deletado com sucesso!/);
    await weddingsList.expectRowNotVisible(name);
  });

  test("@critical Navegar da listagem para detail page com dados corretos", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);
    const weddingDetail = new WeddingDetailPage(page);

    await weddingsList.goto();
    const data = generateWeddingData();
    await weddingsList.createWedding(data);

    const name = `${data.groom_name} & ${data.bride_name}`;
    await weddingsList.viewWedding(name);

    await weddingDetail.expectHeading(data.groom_name, data.bride_name);
    await weddingDetail.expectUrlMatch();

    await weddingDetail.goBack();
    await expect(page).toHaveURL(/\/weddings/);
  });

  test("@regression Paginação da listagem funcional", async ({ authenticatedPage }) => {
    test.setTimeout(60_000);
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();

    // Create enough weddings to span at least 2 pages
    for (let i = 0; i < 6; i++) {
      const data = generateWeddingData();
      await weddingsList.createWedding(data, { focusRow: false });
    }

    // Page 1: next button visible, previous not
    await weddingsList.expectHasNext();
    await weddingsList.expectNotHasPrevious();

    // Navigate forward and backward
    await weddingsList.nextPage();
    await weddingsList.expectHasPrevious();

    await weddingsList.previousPage();
    await weddingsList.expectNotHasPrevious();
  });

  test("@regression Filtros de status aplicados corretamente", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();

    const data1 = generateWeddingData();
    await weddingsList.createWedding(data1);
    const name1 = `${data1.groom_name} & ${data1.bride_name}`;

    const data2 = generateWeddingData();
    await weddingsList.createWedding(data2);
    const name2 = `${data2.groom_name} & ${data2.bride_name}`;

    await weddingsList.filterByStatus("Em Andamento");
    await weddingsList.expectRowVisible(name1);
    await weddingsList.expectRowVisible(name2);

    await weddingsList.filterByStatus("Concluído");
    await weddingsList.expectRowNotVisible(name1);
    await weddingsList.expectRowNotVisible(name2);
  });

  test("@critical Enviar formulário vazio mostra erros de validação", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();

    // Open dialog and submit without filling
    await page.getByRole("button", { name: "Novo Casamento" }).click();
    await weddingsList.formDialog.expectVisible("Novo Casamento");
    await weddingsList.formDialog.submit();

    // Dialog stays open with validation errors
    await weddingsList.formDialog.expectValidationError();
    await weddingsList.formDialog.expectVisible("Novo Casamento");
  });
});
