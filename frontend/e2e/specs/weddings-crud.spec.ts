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
    const weddingDetail = new WeddingDetailPage(page);

    await weddingsList.goto();
    const data = generateWeddingData();
    await weddingsList.createWedding(data);

    const oldName = `${data.groom_name} & ${data.bride_name}`;
    const newGroom = "Editado " + faker.person.fullName();
    await weddingsList.editWedding(oldName, { groom_name: newGroom });

    const newName = `${newGroom} & ${data.bride_name}`;
    await weddingsList.expectToastSuccess(/Casamento atualizado com sucesso!/);
    await weddingsList.expectRowVisible(newName);

    await weddingsList.viewWedding(newName);
    await weddingDetail.expectHeading(newGroom, data.bride_name);
    await weddingDetail.expectUrlMatch();
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
    const page = authenticatedPage;
    const weddingsList = new WeddingsListPage(page);

    await weddingsList.goto();

    // Create 6 weddings (pageSize is 5)
    const weddingNames: string[] = [];
    for (let i = 0; i < 6; i++) {
      const data = generateWeddingData();
      await weddingsList.createWedding(data);
      weddingNames.push(`${data.groom_name} & ${data.bride_name}`);
    }

    // Page 1 should show 5 weddings
    for (let i = 0; i < 5; i++) {
      await weddingsList.expectRowVisible(weddingNames[i]);
    }

    // Navigate to page 2
    await weddingsList.nextPage();
    await weddingsList.expectRowVisible(weddingNames[5]);

    // Navigate back to page 1
    await weddingsList.previousPage();
    for (let i = 0; i < 5; i++) {
      await weddingsList.expectRowVisible(weddingNames[i]);
    }
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

    // Filter by "Em Andamento" — default status, both should appear
    await weddingsList.filterByStatus("Em Andamento");
    await weddingsList.expectRowVisible(name1);
    await weddingsList.expectRowVisible(name2);

    // Filter by "Concluído" — none should appear
    await page.getByRole("combobox", { name: "Filtrar por status" }).click();
    await page.getByRole("option", { name: "Concluído" }).click();
    await weddingsList.expectRowNotVisible(name1);
    await weddingsList.expectRowNotVisible(name2);
  });
});
