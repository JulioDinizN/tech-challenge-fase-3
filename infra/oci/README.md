# OCI Terraform infrastructure

This directory defines the cloud infrastructure used by ToggleMaster on Oracle Cloud Infrastructure. The authorized Ashburn stack has been applied with a private remote state backend and is temporarily active for the Group 100 demonstration. Do not run another full apply or destroy before the recording is complete.

## Challenge mapping

| Phase 2 requirement | Terraform resource |
| --- | --- |
| Kubernetes cluster and worker nodes | OKE cluster and managed node pool |
| Five image repositories | Five private OCIR repositories |
| Three independent PostgreSQL databases | Three OCI Database with PostgreSQL systems |
| Redis cache | One non-sharded OCI Cache cluster |
| Standard message queue | One OCI Queue |
| Analytics NoSQL table | One OCI NoSQL table keyed by `event_id` |
| External ingress network | Public load-balancer subnet and NSG for the later Nginx deployment |
| Segredos da aplicação | OCI Vault `DEFAULT`, chave AES-256 de software e oito segredos gerados pelo OCI |
| Secure service access | OKE Workload Identity para Queue, NoSQL e o provider CSI do Vault |

The Terraform also creates a VCN, an internet gateway, a NAT gateway, a service gateway, public API/load-balancer subnets, private worker/data subnets, route tables, and network security groups.

## Deliberate boundaries

O Terraform provisiona recursos OCI e seus metadados. Deliberadamente, ele não:

- build or push the five images;
- instala Metrics Server, Secrets Store CSI ou NGINX Ingress;
- aplica manifests Kubernetes;
- cria bancos/schemas dentro dos três PostgreSQL;
- recebe o token do OCIR ou gera o image pull Secret;
- executa comandos locais por `local-exec`.

Essas tarefas estão em `k8s/` e `scripts/`. Separar a infraestrutura do deploy mantém o plano legível, permite gravar cada etapa e evita armazenar credenciais locais no state.

## Architecture decisions

- The OKE API endpoint is public but restricted to `api_allowed_cidrs`; worker and data resources have no public IPs.
- Uma security list vazia explícita evita herdar regras da VCN; os NSGs versionados permitem os fluxos exigidos pelo OKE entre workers e o endpoint Kubernetes (`6443`, `12250` e retorno do control plane), além de `10256` entre o Load Balancer e o `kube-proxy`.
- OKE uses the Flannel overlay CNI to keep the initial student deployment small and straightforward.
- O node pool usa o padrão OCI de volumes paravirtualizados sem a opção adicional de criptografia PV em trânsito; os volumes permanecem criptografados em repouso e trafegam na rede interna da OCI. Durante o primeiro deploy do OKE 1.34.2, workers E5 com imagens Oracle Linux 9.7 e 8.10 build 1505 não registraram; um worker E3/AD-3 com a mesma build 1505 repetiu o problema. A1/AD-1 e E3/AD-1/AD-2 foram rejeitados por falta de capacidade física. As rotas, DNS, NAT, Service Gateway, NSGs e o vínculo da VNIC foram verificados diretamente, e a tenancy não possuía dynamic groups nem políticas OSMS/OSMH. O teste E3/AD-3 com a imagem Oracle Linux 8.10 build 1462 registrou no OKE e apareceu como Ready no Kubernetes; essa é a configuração validada para a demonstração.
- The default is an Enhanced OKE cluster because OCI workload identity and node cycling are enhanced-cluster features. A Basic cluster is possible only when `create_workload_identity_policy = false`; the applications would then need a different authentication design, such as instance principals.
- O F5 NGINX Ingress Controller OSS cria dinamicamente um Load Balancer flexível de 10 Mbps na subnet pública e usa os NSGs expostos no output `network`. Esse Load Balancer não pertence ao state do Terraform; o teardown o remove e espera sua exclusão antes do `terraform destroy`.
- O Terraform cria um Vault do tipo `DEFAULT` e uma chave `SOFTWARE`, opções dentro do Always Free, em vez de um Virtual Private Vault pago.
- O OCI Vault gera três senhas administrativas de PostgreSQL, três senhas de aplicação, uma `MASTER_KEY` e uma chave interna usando o formato padrão de passphrase do serviço. O conteúdo não é informado ao Terraform, não aparece em `.tfvars` e não é exportado; somente nomes, OCIDs e regras de geração fazem parte do plano/state.
- Cada PostgreSQL recebe seu próprio segredo administrativo e versão atual. No cluster, Jobs criam usuários de aplicação restritos; os Deployments não recebem a senha administrativa.
- OCI Cache is private and TLS-only. The future application value should use the output `redis.tls_url` (`rediss://`).
- The default one-node Redis cluster is a cost-conscious development setting, not a high-availability topology. OCI recommends at least three nodes for reliability; set `redis_node_count = 3` before a production-style deployment if the budget permits.
- Queue producer and consumer access is separated with `queue-push` and `queue-pull`; analytics receives row-level NoSQL access. Para o Vault, o provider CSI solicita o token da ServiceAccount do pod que monta cada `SecretProviderClass`; por isso a policy autoriza somente `auth-service`, `flag-service`, `targeting-service`, `evaluation-service` e `database-init`, no namespace e cluster esperados, a ler bundles do Vault deste stack.
- O Load Balancer do Ingress usa `security-rule-management-mode=None`: as regras necessárias já pertencem aos NSGs gerenciados pelo Terraform, evitando conceder permissões amplas de alteração de rede ao controller. As imagens do NGINX e dos Jobs usam nomes totalmente qualificados (`docker.io/...`) porque o CRI-O do worker não aceita referências curtas sem registry.
- O administrador do OCI Database with PostgreSQL possui `CREATEROLE`, mas não é superusuário. Os Jobs concedem associação temporária ao usuário de aplicação para atribuir ownership do banco, executam o schema com o próprio usuário e removem a associação administrativa ao final.
- Os três PostgreSQL mantêm uma instância, mas usam famílias E5, E6 e Standard3 independentes por padrão. Auth e flags usam 1 OCPU/16 GB; targeting usa 2 OCPUs/32 GB porque esses são os mínimos aceitos pela família Standard3. Isso preserva o isolamento exigido e respeita o limite de um DB System por família disponível na tenancy estudantil; shapes, OCPUs e memória continuam configuráveis por serviço para outras regiões ou quotas.
- PostgreSQL, Redis, and OKE sizes are variables because service availability, quotas, and cost differ by tenancy and region.

## Prerequisites for a future plan

1. Terraform 1.6 or newer and OCI CLI installed.
2. An OCI CLI profile with permission to manage networking, OKE, OCIR, PostgreSQL, Cache, Queue, NoSQL, and IAM policies in the chosen compartment.
3. A compartment and a supported OCI region.
4. Limites suficientes para três PostgreSQL, um OCI Cache, workers OKE, Load Balancer e rede.
5. Estimativa de custo revisada. PostgreSQL, Cache, workers e Load Balancer podem consumir o crédito de US$ 300; Vault `DEFAULT`, uma chave de software e oito segredos cabem nos limites Always Free documentados pela Oracle.
6. Um backend remoto privado e versionado para o state antes do primeiro apply real.

## Local development validation (safe; no deployment)

These commands do not create cloud resources:

```bash
cd infra/oci
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

The provider is pinned in `versions.tf`, and `.terraform.lock.hcl` is committed for reproducibility.

## Prepare inputs later

Copy the example without committing the resulting file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Confirm current OKE versions and images instead of trusting the example placeholders:

```bash
oci ce cluster-options get \
  --cluster-option-id all \
  --compartment-id <compartment-ocid> \
  --profile <profile>

oci ce node-pool-options get \
  --node-pool-option-id all \
  --compartment-id <compartment-ocid> \
  --node-pool-k8s-version <kubernetes-version> \
  --profile <profile>
```

Set `node_image_id` to an OKE image that matches both the selected Kubernetes version and node shape. Terraform preconditions reject unsupported versions, shapes, and image IDs during planning.

The worker configuration validated in Ashburn uses `Oracle-Linux-8.10-2026.04.30-3-OKE-1.34.2-1462` (`ocid1.image.oc1.iad.aaaaaaaauedaaoleflnipq4s6u37rb3wcu6xmod4eln6xrcc3h3hwtmswzyq`) with Kubernetes `v1.34.2` and the `VM.Standard.E3.Flex` shape. Image OCIDs are regional, so discover a matching image again if `region` changes.

`node_pool_name` normally remains `null`, which produces `<project_name>-workers`. Set an explicit name only for a controlled blue/green node-pool replacement when an existing OCI work request prevents an in-place repair. Validate the replacement pool first, then delete the superseded pool so duplicate compute capacity does not remain billable.

`node_availability_domain_count` normally remains `null`, allowing OKE to use every availability domain returned by the region. Set it to `1` only for a minimal diagnostic or short-lived demonstration pool when isolating availability-domain capacity or host boot behavior.

`node_availability_domain_start_index` defaults to `0`. Change it only with an explicit `node_availability_domain_count` when testing capacity in a different availability domain; return it to `0` for the normal multi-AD pool.

## Preview the infrastructure without deploying

After replacing every value in the ignored `terraform.tfvars`, generate and inspect a saved plan:

```bash
terraform plan \
  -input=false \
  -out=togglemaster.tfplan

terraform show togglemaster.tfplan
```

Planning reads OCI metadata to validate current regions, availability domains, Kubernetes versions, node images, and shapes, but it does not create resources. Both `terraform.tfvars` and `*.tfplan` are ignored by Git.

O plano cria o Vault e todos os segredos; não existe mais OCID fictício de segredo em `terraform.tfvars`. Ainda assim, nunca aplique um plano antigo: gere um novo plano depois de qualquer alteração, revise a quantidade de recursos e confira preços/quotas no Console OCI.

## Remote state before the first apply

Real state can contain sensitive infrastructure metadata. Create a versioned, private OCI Object Storage bucket outside this stack, then:

```bash
cp backend.tf.example backend.tf
terraform init -migrate-state
```

Edit `backend.tf` first. Do not place OCI keys or tokens in it; use the OCI profile or environment authentication. The native OCI backend provides state locking.

## Deployment and teardown workflow

Para uma recriação futura, revise inputs/custos e gere novamente o plano em vez de aplicar qualquer preview antigo:

```bash
terraform plan -out=togglemaster.tfplan
terraform show togglemaster.tfplan
terraform apply togglemaster.tfplan
```

Applying can create billable resources. A human must review the saved plan and OCI pricing before the final command.

No ambiente atual, as etapas de apply, publicação, add-ons, deploy, smoke e carga já foram validadas. Em uma recriação autorizada:

1. execute `terraform output -raw kubeconfig_command` e rode o comando exibido;
2. defina `IMAGE_TAG`, `OCIR_USERNAME` e `OCIR_AUTH_TOKEN` somente no shell;
3. use `scripts/build-push-images.sh` e `scripts/deploy-oke.sh`;
4. execute `scripts/smoke-oke.sh` e `scripts/load-test-oke.sh` e registre no vídeo o Ingress, os HPAs e a persistência;
5. execute `scripts/destroy-oci.sh` ao finalizar.

O output `vault` contém somente o OCID do Vault e os nomes dos segredos; `deployment_context`, `network`, `postgresql_systems`, `redis`, `evaluation_queue`, `analytics_table` e `ocir_repositories` alimentam a renderização. Terraform não altera o kubeconfig nem lê o conteúdo dos segredos.

## State e ciclo de vida dos segredos

Mesmo sem valores secretos, trate o state como confidencial porque ele registra OCIDs, endpoints privados e topologia. O backend nativo OCI deve usar bucket privado, versionamento e locking.

Na destruição, Vault, chaves e segredos entram nas janelas de exclusão programada exigidas pelo OCI. Eles ficam inacessíveis, mas podem continuar aparecendo como `PENDING_DELETION`; os componentes pagos devem ser conferidos separadamente no Cost Analysis.

## Referências oficiais

- [OCI Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm): limites gratuitos de Vault, chaves de software e segredos.
- [Terraform `oci_vault_secret`](https://docs.oracle.com/en-us/iaas/tools/terraform-provider-oci/latest/docs/r/vault_secret.html): geração automática e outputs de metadados.
- [Terraform `oci_psql_db_system`](https://docs.oracle.com/en-us/iaas/tools/terraform-provider-oci/latest/docs/r/psql_db_system.html): senha por Vault Secret e versão.
- [OCI Secrets Store CSI Driver Provider](https://github.com/oracle/oci-secrets-store-csi-driver-provider/blob/main/GettingStarted.md): Workload Identity, sincronização de Secrets e rotação.
- [Anotações do OCI Load Balancer](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer_topic-Summaryofannotations.htm): subnet, NSGs e shape flexível.
- [Pull de imagens privadas do OCIR no OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengpullingimagesfromocir.htm): token e `imagePullSecrets`.
- [Instalação do F5 NGINX Ingress Controller OSS](https://docs.nginx.com/nginx-ingress-controller/install/helm/open-source/): chart OCI usado pelo script.
