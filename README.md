   # DEMETER API

   API para classificação de grãos utilizando Machine Learning e visão computacional.

   ### Mebros da Equipe:
   - Emanuel Mascarenhas Rodrigues
   - Luis Eduardo Rodrigues Miranda
   - Vinicius Abreu Silva Franco


   ## Documentação no POSTMAN
   A documentação completa e interativa está disponível em:

   👉 [![View in Postman](https://run.pstmn.io/button.svg)](https://documenter.getpostman.com/view/49559946/2sB3WmS2Ww)

   Essa documentação foi gerada a partir do esquema OpenAPI da aplicação FastAPI.

   ## 🚀 Quick Start

   ### Pré-requisitos

   - Docker e Docker Compose instalados
   - Git

   ### Primeira Execução

   ```bash
   # 1. Clone o repositório
   git clone <repo-url>
   cd demeter-api

   # 2. Inicie os containers
   cd docker
   docker-compose up -d

   # 3. Aguarde ~30 segundos para inicialização completa
   # A API estará disponível em: http://localhost:8000
   ```

   **Pronto!** O sistema está rodando com:
   - ✅ Banco de dados criado e migrado
   - ✅ Roles e permissions configuradas
   - ✅ Usuário admin criado automaticamente

   ### Credenciais Padrão - Crendenciais disponibilizadas somente para fins de teste local.

   ```
   Email: admin@demeter.local
   Senha: Admin123!
   ```

   ---

   ## 📚 Documentação da API

   Após iniciar os containers, acesse:

   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

   ---

   ## 🧪 Executando Testes

   ### Todos os testes (38 testes)

   ```bash
   # Certifique-se que os containers estão rodando
   pytest tests/ -v
   ```

   ### Apenas testes unitários (7 testes)

   ```bash
   pytest tests/unit/ -v
   ```

   ### Apenas testes de integração (31 testes)

   ```bash
   pytest tests/integration/ -v
   ```

   ---

   ## 🛠️ Desenvolvimento

   ### Estrutura do Projeto

   ```
   demeter-api/
   ├── src/
   │   ├── application/       # Casos de uso
   │   ├── domain/           # Entidades e regras de negócio
   │   ├── infrastructure/   # Implementações (DB, repositórios)
   │   ├── presentation/     # Controllers e rotas
   │   └── config/          # Configurações (DB, segurança, logs)
   ├── tests/
   │   ├── unit/            # Testes unitários
   │   └── integration/     # Testes de integração
   ├── alembic/             # Migrations do banco de dados
   └── docker/              # Docker e scripts
   ```

   ### Comandos Úteis

   #### Acessar o container da API

   ```bash
   docker exec -it demeter-api bash
   ```

   #### Ver logs da API

   ```bash
   docker logs demeter-api -f
   ```

   #### Acessar o banco de dados

   ```bash
   docker exec -it demeter-db psql -U demeter -d demeter_db
   ```

   #### Criar nova migration

   ```bash
   # Dentro do container
   docker exec -it demeter-api alembic revision --autogenerate -m "descrição"

   # Aplicar migrations
   docker exec -it demeter-api alembic upgrade head
   ```

   #### Criar novo admin

   ```bash
   docker exec -it demeter-api python -m src.cli.create_admin \
     --email "novo@admin.com" \
     --name "Nome Admin" \
     --password "SenhaSegura123!" \
     --phone "11999999999"
   ```

   ---

   ## 🔄 Recriando o Ambiente

   Se precisar limpar tudo e começar do zero:

   ```bash
   cd docker

   # Para containers e remove volumes (apaga todos os dados)
   docker-compose down -v

   # Rebuilda e inicia novamente
   docker-compose up -d --build
   ```

   **Nota**: Todos os dados serão perdidos, incluindo usuários e classificações.

   ---

   ## 🐳 Containers

   O projeto utiliza 3 containers:

   | Container | Porta | Descrição |
   |-----------|-------|-----------|
   | \`demeter-api\` | 8000 | API FastAPI |
   | \`demeter-db\` | 5432 | PostgreSQL 16 |
   | \`demeter-adminer\` | 8080 | Interface web para banco |

   ### Adminer (Interface do Banco)

   Acesse: http://localhost:8080

   ```
   Sistema: PostgreSQL
   Servidor: demeter-db
   Usuário: demeter
   Senha: demeter_dev
   Base de dados: demeter_db
   ```

   ---

   ## 🔐 Segurança

   ### Variáveis de Ambiente

   Configure no arquivo \`docker/docker-compose.yml\`:

   ```yaml
   environment:
     - SECRET_KEY=sua-chave-super-secreta-aqui
     - ADMIN_EMAIL=admin@demeter.local
     - ADMIN_PASSWORD=SuaSenhaSegura123!
   ```

   ### Roles e Permissions

   O sistema implementa RBAC (Role-Based Access Control):

   **Roles:**
   - \`classificador\`: Usuário padrão que pode criar e gerenciar suas próprias classificações
   - \`admin\`: Administrador com acesso total

   **Permissions:**
   - \`classifications:create:own\` - Criar classificação própria
   - \`classifications:read:own\` - Ler classificações próprias
   - \`classifications:update:own\` - Atualizar classificações próprias
   - \`classifications:delete:own\` - Deletar classificações próprias
   - \`classifications:read:all\` - Ler todas as classificações (admin)
   - \`classifications:delete:all\` - Deletar qualquer classificação (admin)

   ---

   ## 📊 Status do Projeto

   ### Implementado ✅

   - [x] Autenticação JWT (login, register, refresh, logout)
   - [x] RBAC (Roles e Permissions)
   - [x] CRUD de Classificações com soft delete
   - [x] Health check endpoint
   - [x] Audit logs
   - [x] Migrations automáticas na inicialização
   - [x] Seed de dados inicial (roles e admin)
   - [x] Testes (38 testes passando)
   - [x] Documentação Swagger/OpenAPI

   ### Em Desenvolvimento 🚧

   - [ ] Integração com modelo de ML real
   - [ ] Upload e processamento de imagens
   - [ ] Métricas e estatísticas
   - [ ] Exportação de dados
   - [ ] API de relatórios

   ---
