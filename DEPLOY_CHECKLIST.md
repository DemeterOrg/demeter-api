# ✅ Checklist de Deploy - Easypanel

Use este checklist para garantir que não esqueceu nada durante o deploy.

## 🔧 Preparação

- [ ] Código commitado e pushado para o repositório Git
- [ ] Branch de produção escolhida (ex: `main` ou `production`)
- [ ] Conta no Easypanel criada e configurada
- [ ] Acesso ao dashboard do Easypanel

## 📦 Configuração no Easypanel

### Projeto
- [ ] Projeto criado com nome significativo (ex: `demeter-api`)

### Serviço PostgreSQL
- [ ] Serviço Postgres criado (ex: `demeter-db`)
- [ ] Versão PostgreSQL 16 selecionada
- [ ] Database name definido: `demeter_db`
- [ ] Username definido: `demeter`
- [ ] Senha forte gerada e **SALVA EM LOCAL SEGURO**
- [ ] Serviço deployed e healthy ✅

### Serviço da API
- [ ] Serviço App criado (ex: `demeter-api`)
- [ ] Repositório Git conectado
- [ ] Branch correta selecionada
- [ ] Build Type: `Dockerfile`
- [ ] Dockerfile path: `./docker/Dockerfile`

### Variáveis de Ambiente
- [ ] `DATABASE_URL` configurada com credenciais corretas do Postgres
- [ ] `SECRET_KEY` gerada (32+ caracteres aleatórios)
- [ ] `ADMIN_EMAIL` alterado (não usar padrão)
- [ ] `ADMIN_PASSWORD` alterado (senha forte)
- [ ] `ALLOWED_ORIGINS` configurado com domínios corretos
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `false`
- [ ] Todas as variáveis do `.env.production.example` preenchidas

### Volumes Persistentes
- [ ] Volume `uploads` criado → Mount path: `/app/uploads`
- [ ] Volume `logs` criado → Mount path: `/app/logs`

### Rede e Portas
- [ ] Container Port: `8000`
- [ ] Proxy Port: `8000`

### Domínio
- [ ] Domínio adicionado (Easypanel padrão ou customizado)
- [ ] DNS configurado (se domínio customizado)
- [ ] HTTPS/SSL certificado configurado automaticamente ✅

## 🚀 Deploy

- [ ] Revisão final de todas as configurações
- [ ] Clicado em **Deploy**
- [ ] Build completou sem erros
- [ ] Container iniciou com sucesso

## ✅ Verificação Pós-Deploy

### Health Checks
- [ ] Health check endpoint respondendo: `/health`
- [ ] Status: `healthy`
- [ ] Database: `connected`

### Documentação
- [ ] Swagger acessível: `/docs`
- [ ] ReDoc acessível: `/redoc`
- [ ] Schemas carregando corretamente

### Autenticação
- [ ] Login com credenciais admin funcionando
- [ ] Token JWT sendo gerado
- [ ] Refresh token funcionando
- [ ] Logout funcionando

### Funcionalidades
- [ ] Criação de classificação funcionando
- [ ] Upload de imagem funcionando
- [ ] Listagem de classificações funcionando
- [ ] API de ML respondendo (se `USE_REAL_ML_API=true`)

### Logs
- [ ] Logs da API aparecendo no dashboard
- [ ] Logs do Postgres aparecendo no dashboard
- [ ] Nível de log correto (`INFO` em produção)

## 🔒 Segurança

- [ ] SECRET_KEY única e não exposta
- [ ] Senhas fortes utilizadas
- [ ] CORS configurado apenas para domínios necessários
- [ ] Rate limiting ativo
- [ ] HTTPS funcionando corretamente
- [ ] Credenciais do banco não expostas em logs

## 🔄 Automação (Opcional)

- [ ] Auto-deploy configurado
- [ ] Webhook do GitHub/GitLab configurado
- [ ] Teste de push → auto-deploy realizado

## 📊 Monitoramento

- [ ] Backups do PostgreSQL configurados
- [ ] Frequência de backup definida
- [ ] Local de armazenamento de backups configurado
- [ ] Teste de restore de backup realizado

## 📝 Documentação

- [ ] URLs de produção documentadas
- [ ] Credenciais salvas em gerenciador de senhas
- [ ] Equipe notificada sobre novo ambiente
- [ ] Documentação da API compartilhada

## 🎉 Finalização

- [ ] Todos os itens acima verificados
- [ ] Aplicação rodando em produção
- [ ] Testes de integração end-to-end realizados
- [ ] Monitoramento ativo

---

## 🆘 Em caso de problemas

### API não inicia
1. Verifique logs da API no Easypanel
2. Confirme `DATABASE_URL` correta
3. Verifique se PostgreSQL está healthy

### Erro 502
1. Confirme porta 8000 configurada
2. Verifique health check
3. Veja logs de erro

### Migrations não aplicadas
1. Acesse console da API
2. Execute: `alembic upgrade head`

### Banco não conecta
1. Verifique nome do serviço (`demeter-db`)
2. Confirme credenciais
3. Verifique se ambos serviços estão no mesmo projeto

---

**Data do Deploy**: ___/___/______
**Responsável**: ________________
**Ambiente**: Produção - Easypanel
**Status**: ⬜ Em progresso | ⬜ Completo ✅
