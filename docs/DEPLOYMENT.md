# 🚀 Guida al Deployment Cloud

Questa guida ti mostra come deployare il bot Telegram in modo professionale su piattaforme cloud gratuite.

## 🎯 Opzioni di Deployment

### 1. **Railway** (⭐ Raccomandato)
- ✅ **Gratuito**: $5/mese di crediti gratuiti
- ✅ **Facile**: Deploy automatico da GitHub
- ✅ **Database**: PostgreSQL incluso
- ✅ **Monitoraggio**: Dashboard integrato

### 2. **Render**
- ✅ **Gratuito**: Piano free disponibile
- ✅ **Affidabile**: Uptime elevato
- ⚠️ **Limitazioni**: Sleep dopo inattività

### 3. **Heroku**
- ⚠️ **Limitato**: Piano gratuito ridotto
- ✅ **Maturo**: Piattaforma consolidata
- ⚠️ **Sleep**: App si addormenta

## 🛠️ Setup Iniziale

### 1. Preparazione Repository
```bash
# Clona o crea il repository
git init
git add .
git commit -m "Initial commit"

# Crea repository su GitHub
gh repo create telegram-bot --public
git push origin main
```

### 2. Variabili d'Ambiente Necessarie
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_ID=123456789
DATABASE_URL=postgresql://user:pass@host:port/db
ENVIRONMENT=production
```

## 🚂 Deploy su Railway

### Metodo 1: Dashboard Web
1. Vai su [railway.app](https://railway.app)
2. Connetti GitHub account
3. Clicca "New Project" → "Deploy from GitHub repo"
4. Seleziona il tuo repository
5. Railway rileva automaticamente il `Dockerfile`
6. Aggiungi le variabili d'ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_USER_ID`
7. Aggiungi database PostgreSQL:
   - Clicca "New" → "Database" → "Add PostgreSQL"
   - Railway configura automaticamente `DATABASE_URL`

### Metodo 2: CLI
```bash
# Installa Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Aggiungi database
railway add postgresql

# Configura variabili
railway variables set TELEGRAM_BOT_TOKEN="your_token"
railway variables set ADMIN_USER_ID="your_id"
```

## 🎨 Deploy su Render

### Setup
1. Vai su [render.com](https://render.com)
2. Connetti GitHub account
3. Clicca "New" → "Web Service"
4. Seleziona il repository
5. Render rileva automaticamente `render.yaml`
6. Configura variabili d'ambiente nel dashboard
7. Il database PostgreSQL viene creato automaticamente

### Configurazione Manuale
Se `render.yaml` non viene rilevato:
- **Build Command**: `docker build -t bot .`
- **Start Command**: `python main_cloud.py`
- **Environment**: `Docker`

## 🟣 Deploy su Heroku

### Prerequisiti
```bash
# Installa Heroku CLI
# Windows: scaricare da heroku.com
# Mac: brew install heroku/brew/heroku
# Linux: snap install heroku --classic

# Login
heroku login
```

### Deploy
```bash
# Crea app
heroku create your-bot-name --region eu

# Aggiungi PostgreSQL
heroku addons:create heroku-postgresql:mini

# Configura variabili
heroku config:set TELEGRAM_BOT_TOKEN="your_token"
heroku config:set ADMIN_USER_ID="your_id"

# Deploy
git push heroku main
```

## 🐳 Deploy Locale con Docker

### Sviluppo
```bash
# Crea file .env
cp .env.example .env
# Modifica .env con i tuoi dati

# Avvia tutti i servizi
docker-compose up -d

# Verifica stato
docker-compose ps

# Logs
docker-compose logs -f bot
```

### Produzione
```bash
# Build ottimizzata
docker build -t telegram-bot:prod .

# Avvia con database esterno
docker run -d \
  --name telegram-bot \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  -e ADMIN_USER_ID="your_id" \
  -e DATABASE_URL="postgresql://..." \
  -p 8000:8000 \
  telegram-bot:prod
```

## 📊 Monitoraggio e Maintenance

### Health Checks
Tutti i deployment includono endpoint di monitoraggio:

- **Health**: `https://your-app.com/health`
- **Metrics**: `https://your-app.com/metrics`
- **Stats**: `https://your-app.com/stats`

### Logs
```bash
# Railway
railway logs

# Render
# Logs disponibili nel dashboard

# Heroku
heroku logs --tail -a your-app-name

# Docker
docker-compose logs -f
```

### Database Maintenance
```bash
# Backup (PostgreSQL)
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql

# Cleanup automatico
# Il bot esegue cleanup ogni 24 ore automaticamente
```

## 🔧 Troubleshooting

### Problemi Comuni

#### Bot non risponde
1. Controlla logs per errori
2. Verifica `TELEGRAM_BOT_TOKEN`
3. Controlla connessione database
4. Verifica health check: `/health`

#### Database connection error
1. Controlla `DATABASE_URL`
2. Verifica che il database sia attivo
3. Controlla firewall/network

#### Out of memory
1. Ottimizza query database
2. Aumenta limiti container
3. Implementa caching con Redis

#### App si addormenta (Render/Heroku)
1. Configura cron job per ping periodico
2. Usa servizio di uptime monitoring
3. Considera upgrade a piano paid

### Debug Commands
```bash
# Test connessione database
python -c "import asyncpg; asyncio.run(asyncpg.connect('$DATABASE_URL'))"

# Test bot token
curl -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Test health endpoint
curl https://your-app.com/health
```

## 🔐 Sicurezza

### Best Practices
1. **Mai committare** token o password
2. **Usa variabili d'ambiente** per tutti i segreti
3. **Abilita HTTPS** (automatico su tutte le piattaforme)
4. **Limita accesso admin** solo al tuo user ID
5. **Monitora logs** per attività sospette

### Configurazione Sicura
```bash
# Genera password sicure
openssl rand -base64 32

# Verifica variabili d'ambiente
env | grep -E "(TOKEN|PASSWORD|SECRET)"

# Controlla permessi
ls -la .env
# Dovrebbe essere: -rw------- (600)
```

## 📈 Scaling e Performance

### Ottimizzazioni
1. **Connection Pooling**: Già implementato in PostgreSQL
2. **Redis Caching**: Configurato in docker-compose
3. **Async Operations**: Tutto il codice è asincrono
4. **Database Indexes**: Creati automaticamente

### Monitoring
```bash
# Metriche Prometheus
curl https://your-app.com/metrics

# Statistiche bot
curl https://your-app.com/stats

# Health check
curl https://your-app.com/health
```

## 🎉 Post-Deploy Checklist

- [ ] Bot risponde a `/start`
- [ ] Database connesso e funzionante
- [ ] Health check restituisce 200
- [ ] Logs non mostrano errori
- [ ] Variabili d'ambiente configurate
- [ ] Backup database schedulato
- [ ] Monitoring attivo
- [ ] Domain personalizzato (opzionale)

## 🆘 Supporto

### Risorse Utili
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Heroku Docs](https://devcenter.heroku.com/)
- [Docker Docs](https://docs.docker.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Community
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Railway Discord](https://discord.gg/railway)
- [Render Community](https://community.render.com/)

---

**Il tuo bot è ora pronto per il mondo! 🌍🤖**
