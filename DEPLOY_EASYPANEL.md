# Deploy da Demeter API no Easypanel

Guia completo para fazer deploy da API Demeter no Easypanel com PostgreSQL.

## 📋 Pré-requisitos

- Conta no Easypanel configurada
- Repositório Git da aplicação (GitHub, GitLab, etc.)
- Domínio configurado (ou usar o domínio padrão do Easypanel)

## 🚀 Passo a Passo

### 1️⃣ Criar Projeto no Easypanel

1. Acesse o dashboard do Easypanel
2. Clique em **Create New Project**
3. Nome do projeto: `demeter-api` (ou nome de sua preferência)
4. Clique em **Create**

### 2️⃣ Adicionar Serviço PostgreSQL

1. Dentro do projeto, clique em **Services** → **Create Service**
2. Selecione **Postgres**
3. Configurações:
   - **Service Name**: `demeter-db`
   - **Postgres Version**: `16` (ou latest)
   - **Database Name**: `demeter_db`
   - **Username**: `demeter`
   - **Password**: Gere uma senha forte (salve em local seguro)
4. Clique em **Deploy**
5. Aguarde o serviço iniciar

> **⚠️ IMPORTANTE**: Anote as credenciais do banco. Você precisará delas para configurar a API.

### 3️⃣ Adicionar Serviço da API

1. Ainda em **Services**, clique em **Create Service**
2. Selecione **App**
3. Configurações básicas:
   - **Service Name**: `demeter-api`
   - **Source**: Selecione seu repositório Git
   - **Branch**: `main` (ou branch de produção)
   - **Build Type**: `Dockerfile`
   - **Dockerfile Path**: `./docker/Dockerfile`

### 4️⃣ Configurar Variáveis de Ambiente

Na seção **Environment Variables**, adicione as seguintes variáveis:

```bash
# Application Settings
PROJECT_NAME=DEMETER-API
VERSION=1.0.0
DESCRIPTION=API para classificação de grãos com IA
API_V1_STR=/api/v1
ENVIRONMENT=production
DEBUG=false

# Database Settings
# ATENÇÃO: Substitua pelos valores do seu serviço Postgres
DATABASE_URL=postgresql+asyncpg://demeter:SUA_SENHA_AQUI@demeter-db:5432/demeter_db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Security & Authentication
# IMPORTANTE: Gere uma SECRET_KEY única e forte!
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_MINIMO_32_CARACTERES
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true

# CORS Settings
# IMPORTANTE: Adicione os domínios permitidos
ALLOWED_ORIGINS=https://seu-frontend.com,https://app.demeter.com
ALLOWED_METHODS=GET,POST,PATCH,DELETE
ALLOWED_HEADERS=Authorization,Content-Type
ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_LOGIN=5/15minute
RATE_LIMIT_AUTHENTICATED=100/minute
RATE_LIMIT_PUBLIC=20/minute

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DIR=logs

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg
UPLOAD_DIR=/app/uploads

# Admin User (criado automaticamente na primeira execução)
ADMIN_EMAIL=admin@demeter.com
ADMIN_NAME=Administrador
ADMIN_PASSWORD=SENHA_FORTE_ADMIN_123!
ADMIN_PHONE=11999999999

# ML API Settings
USE_REAL_ML_API=true
DEMETER_ML_API_URL=https://3kgtn4mls7.execute-api.us-east-2.amazonaws.com/upload
DEMETER_ML_TIMEOUT=30.0
ENABLE_ML_FALLBACK_TO_MOCK=false

# Supabase (se utilizar)
USE_SUPABASE_STORAGE=false
SUPABASE_URL=
SUPABASE_KEY=

# AWS S3 (se utilizar)
USE_S3=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
```

### 5️⃣ Configurar Volumes Persistentes

Na seção **Mounts**, adicione os volumes:

1. **Upload Directory**:
   - **Type**: Volume
   - **Name**: `uploads`
   - **Mount Path**: `/app/uploads`

2. **Logs Directory**:
   - **Type**: Volume
   - **Name**: `logs`
   - **Mount Path**: `/app/logs`

### 6️⃣ Configurar Rede e Portas

1. **Port Mapping**:
   - **Container Port**: `8000`
   - **Proxy Port**: `8000`

2. **Health Check** (já configurado no Dockerfile):
   - Interval: 30s
   - Timeout: 10s
   - Start Period: 40s
   - Retries: 3

### 7️⃣ Configurar Domínio

1. Na seção **Domains**, clique em **Add Domain**
2. Opções:
   - **Usar domínio do Easypanel**: Selecione o domínio padrão (ex: `demeter-api.easypanel.host`)
   - **Domínio customizado**: Adicione seu domínio e configure o DNS conforme instruções

3. **HTTPS**: O Easypanel configurará automaticamente o certificado Let's Encrypt

### 8️⃣ Deploy da Aplicação

1. Revise todas as configurações
2. Clique em **Deploy**
3. Acompanhe os logs durante o build e deploy

### 9️⃣ Verificar Deploy

Após o deploy, verifique:

1. **Health Check**:
   ```bash
   curl https://seu-dominio.com/health
   ```
   Resposta esperada:
   ```json
   {
     "status": "healthy",
     "database": "connected"
   }
   ```

2. **Documentação da API**:
   - Swagger: `https://seu-dominio.com/docs`
   - ReDoc: `https://seu-dominio.com/redoc`

3. **Login Admin**:
   Use as credenciais configuradas em `ADMIN_EMAIL` e `ADMIN_PASSWORD`

## 🔟 Auto-Deploy (Opcional)

Para configurar deploy automático a cada push:

1. No serviço da API, vá em **Settings**
2. Ative **Auto Deploy**
3. O Easypanel criará um webhook no GitHub
4. Cada push na branch configurada disparará um novo deploy

## 🔒 Segurança Importante

### ⚠️ Antes de ir para produção:

1. **SECRET_KEY**: Gere uma chave única e forte:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **DATABASE_URL**: Use a senha forte gerada para o PostgreSQL

3. **ADMIN_PASSWORD**: Altere a senha padrão do admin

4. **CORS**: Configure apenas os domínios realmente necessários

5. **Backups**: Configure backups automáticos do PostgreSQL no Easypanel

## 📊 Monitoramento

### Ver Logs da API
1. Acesse o serviço `demeter-api`
2. Vá na aba **Logs**
3. Logs em tempo real estarão disponíveis

### Ver Logs do Banco
1. Acesse o serviço `demeter-db`
2. Vá na aba **Logs**

### Console da API
Para executar comandos dentro do container:
1. Acesse o serviço `demeter-api`
2. Vá na aba **Console**
3. Você terá um terminal bash/sh

## 🛠️ Comandos Úteis no Console

### Criar novo admin
```bash
python -m src.cli.create_admin \
  --email "novo@admin.com" \
  --name "Nome Admin" \
  --password "SenhaSegura123!" \
  --phone "11999999999"
```

### Verificar migrations
```bash
alembic current
alembic history
```

### Aplicar migrations manualmente (se necessário)
```bash
alembic upgrade head
```

## 🔄 Atualizar a Aplicação

### Manual
1. Acesse o serviço `demeter-api`
2. Clique em **Redeploy**
3. O Easypanel fará pull do código e rebuild

### Automático
Se configurou Auto Deploy, apenas faça push para a branch configurada.

## 📝 Troubleshooting

### API não inicia
1. Verifique os logs: pode ser erro de conexão com banco
2. Confirme que `DATABASE_URL` está correto
3. Verifique se o serviço `demeter-db` está healthy

### Erro de conexão com banco
1. Verifique se os serviços estão no mesmo projeto
2. Confirme o nome do serviço PostgreSQL (deve ser `demeter-db`)
3. Formato correto: `postgresql+asyncpg://user:pass@demeter-db:5432/dbname`

### Migrations não aplicadas
1. Acesse o console da API
2. Execute manualmente: `alembic upgrade head`

### Erro 502 Bad Gateway
1. Verifique se a porta 8000 está configurada
2. Confirme que o health check está passando
3. Veja os logs da aplicação

## 🌐 Estrutura de URLs

Após deploy, você terá:

```
https://seu-dominio.com/              → API root
https://seu-dominio.com/health        → Health check
https://seu-dominio.com/docs          → Swagger UI
https://seu-dominio.com/redoc         → ReDoc
https://seu-dominio.com/api/v1/...    → Endpoints da API
```

## 📚 Recursos Adicionais

- [Documentação Easypanel](https://easypanel.io/docs)
- [Postgres Service](https://easypanel.io/docs/services/postgres)
- [App Service](https://easypanel.io/docs/services/app)

## ✅ Checklist Final

Antes de considerar o deploy completo:

- [ ] PostgreSQL rodando e healthy
- [ ] API rodando e healthy
- [ ] Health check respondendo
- [ ] Documentação acessível (/docs e /redoc)
- [ ] Login com admin funcionando
- [ ] SECRET_KEY alterada
- [ ] ADMIN_PASSWORD alterada
- [ ] CORS configurado corretamente
- [ ] HTTPS configurado
- [ ] Backups configurados
- [ ] Auto-deploy configurado (se desejado)
- [ ] Logs sendo gerados corretamente
- [ ] Upload de imagens funcionando

---

**Pronto!** Sua API Demeter está no ar com HTTPS, banco de dados PostgreSQL, e pronta para uso em produção! 🎉
