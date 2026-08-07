# Adotar recursos existentes nos states Terraform

Este runbook descreve a migração controlada do prefixo legado para os roots `shared`, `staging` e `production`. Ele não provisiona recursos novos.

## Pré-requisitos

- Terraform `1.7.5`.
- Credenciais GCP, Vercel e Cloudflare válidas, fornecidas por variáveis de ambiente e nunca pela linha de comando.
- `TERRAFORM_PRODUCTION_APPLY_ENABLED` ausente ou `false`.
- Janela sem alterações manuais de infraestrutura.
- Versionamento e soft delete confirmados no bucket `gen-lang-client-0194045282-tfstate`.

## Regras de segurança

- Nunca grave state, plans ou tokens no repositório.
- Nunca publique plans como artifacts do GitHub Actions.
- Nunca use `-lock=false`, `force-unlock`, `state push -force`, `init -force-copy` ou `init -migrate-state` no root legado.
- Não execute o root legado depois de iniciar os imports.
- Interrompa diante de qualquer `create`, `update`, `replace` ou `destroy` inesperado.

## 1. Congelar e registrar o legado

O state legado está em:

```text
gs://gen-lang-client-0194045282-tfstate/terraform/state/default.tfstate
```

Registre a geração GCS atual e crie uma cópia privada criptografada fora do repositório e dos logs. Calcule seu checksum e registre `lineage` e `serial` sem publicar o conteúdo.

Liste somente os endereços:

```bash
terraform state list
```

Monte a tabela operacional:

```text
address legado → provider ID → state destino → existe no provider → observações
```

## 2. Validar a configuração sem backend

```bash
terraform fmt -check -recursive terraform
terraform -chdir=terraform/shared init -backend=false
terraform -chdir=terraform/shared validate
terraform -chdir=terraform/staging init -backend=false
terraform -chdir=terraform/staging validate
terraform -chdir=terraform/production init -backend=false
terraform -chdir=terraform/production validate
```

## 3. Inicializar os novos prefixes

Inicialize um root por vez com `-reconfigure`. Confirme visualmente o diretório e o prefixo antes de responder à inicialização:

```bash
terraform -chdir=terraform/shared init -reconfigure
terraform -chdir=terraform/staging init -reconfigure
terraform -chdir=terraform/production init -reconfigure
```

Não copie automaticamente o state legado para os novos prefixes.

## 4. Importar shared

Ordem de adoção:

1. bucket GCS de state;
2. Artifact Registry `wedding-management-repo`;
3. WIF pool `github-pool`;
4. WIF provider `github-provider`;
5. Service Account `github-actions-deployer`;
6. binding `workloadIdentityUser`;
7. IAM atual do deployer e da runtime Service Account;
8. projetos Vercel `wedding-management` e `landing`.

Para cada item, obtenha o ID diretamente do provider, importe e valide antes de continuar:

```bash
terraform -chdir=terraform/shared import '<address>' '<provider-id>'
terraform -chdir=terraform/shared state show '<address>'
terraform -chdir=terraform/shared plan -detailed-exitcode
```

Exit code `0` significa convergência; `2` significa diferenças que precisam ser revisadas; `1` significa erro.

## 5. Importar staging

Importe, nesta ordem:

1. `wedding-backend-staging` e seu binding público;
2. containers `neon-database-staging` e `django-secret-staging`;
3. bindings `secretAccessor` do deployer e da runtime SA;
4. bucket R2 `wedding-management-staging`, se já existir;
5. `VITE_API_URL` Preview restrita à branch `develop`.

Se o bucket R2 staging não existir, conclua primeiro todos os imports. Sua criação deve aparecer isoladamente em um plano posterior e aprovado.

Valide health, conexão com o Neon staging, OAuth e upload/download R2 antes de continuar.

## 6. Importar production

Repita o processo para:

1. `wedding-backend` e seu binding público;
2. containers `neon-database` e `django-secret`;
3. bindings `secretAccessor`;
4. bucket R2 `wedding-management-prod`;
5. `VITE_API_URL` Production.

Não prossiga se o plano mencionar objetos de staging.

## 7. Cutover

Após três planos convergentes:

1. confirme que nenhum workflow referencia `terraform/state`;
2. preserve o objeto legado como backup inativo;
3. execute os workflows de plan em `develop` e `main`;
4. valide Cloud Run, Vercel, WIF e R2;
5. restrinja o Environment `Production` à branch `main`;
6. habilite `TERRAFORM_PRODUCTION_APPLY_ENABLED=true` somente após aprovação explícita;
7. confirme que o primeiro apply é no-op.

## Rollback

- Antes de qualquer alteração real: desabilite os workflows novos e volte a apontar a configuração para o prefixo legado.
- Migração incompleta: mantenha o apply bloqueado e reconstrua os bindings a partir da tabela e do backup.
- State corrompido: restaure uma geração GCS em prefixo temporário e valide antes de promovê-la.
- Apply acidental: bloqueie o opt-in imediatamente. O backup do state não restaura infraestrutura; use revisão anterior do Cloud Run e snapshots de IAM/Vercel.
