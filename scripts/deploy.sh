#!/bin/bash

# Script di deploy automatico per il Bot Telegram
# Supporta Railway, Render, e Heroku

set -e

echo "🚀 Deploy Bot Telegram Personalizzato"
echo "===================================="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni helper
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Controlla se i file necessari esistono
check_files() {
    print_info "Controllo file necessari..."
    
    required_files=("Dockerfile" "requirements.txt" "main_cloud.py" "config.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "File mancante: $file"
            exit 1
        fi
    done
    
    print_success "Tutti i file necessari sono presenti"
}

# Controlla variabili d'ambiente
check_env() {
    print_info "Controllo variabili d'ambiente..."
    
    if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
        print_error "TELEGRAM_BOT_TOKEN non configurato"
        echo "Ottieni il token da @BotFather su Telegram"
        exit 1
    fi
    
    if [[ -z "$ADMIN_USER_ID" ]]; then
        print_error "ADMIN_USER_ID non configurato"
        echo "Ottieni il tuo user ID da @userinfobot su Telegram"
        exit 1
    fi
    
    print_success "Variabili d'ambiente configurate"
}

# Deploy su Railway
deploy_railway() {
    print_info "Deploy su Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI non installato"
        echo "Installa con: npm install -g @railway/cli"
        exit 1
    fi
    
    # Login se necessario
    if ! railway whoami &> /dev/null; then
        print_info "Effettua il login su Railway..."
        railway login
    fi
    
    # Crea progetto se non esiste
    if [[ ! -f "railway.json" ]]; then
        print_error "File railway.json mancante"
        exit 1
    fi
    
    # Deploy
    print_info "Deploying su Railway..."
    railway up
    
    # Configura variabili d'ambiente
    print_info "Configurazione variabili d'ambiente..."
    railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
    railway variables set ADMIN_USER_ID="$ADMIN_USER_ID"
    railway variables set ENVIRONMENT="production"
    
    # Aggiungi database PostgreSQL
    railway add postgresql
    
    print_success "Deploy su Railway completato!"
    railway status
}

# Deploy su Render
deploy_render() {
    print_info "Deploy su Render..."
    
    if [[ ! -f "render.yaml" ]]; then
        print_error "File render.yaml mancante"
        exit 1
    fi
    
    print_info "Per deployare su Render:"
    echo "1. Vai su https://render.com"
    echo "2. Connetti il tuo repository GitHub"
    echo "3. Crea un nuovo Web Service"
    echo "4. Seleziona questo repository"
    echo "5. Render rileverà automaticamente il render.yaml"
    echo "6. Configura le variabili d'ambiente nel dashboard:"
    echo "   - TELEGRAM_BOT_TOKEN: $TELEGRAM_BOT_TOKEN"
    echo "   - ADMIN_USER_ID: $ADMIN_USER_ID"
    
    print_success "Istruzioni per Render fornite!"
}

# Deploy su Heroku
deploy_heroku() {
    print_info "Deploy su Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI non installato"
        echo "Installa da: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Login se necessario
    if ! heroku whoami &> /dev/null; then
        print_info "Effettua il login su Heroku..."
        heroku login
    fi
    
    # Crea app se non esiste
    APP_NAME="telegram-bot-$(date +%s)"
    print_info "Creazione app Heroku: $APP_NAME"
    heroku create "$APP_NAME" --region eu
    
    # Aggiungi PostgreSQL addon
    print_info "Aggiunta database PostgreSQL..."
    heroku addons:create heroku-postgresql:mini -a "$APP_NAME"
    
    # Configura variabili d'ambiente
    print_info "Configurazione variabili d'ambiente..."
    heroku config:set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" -a "$APP_NAME"
    heroku config:set ADMIN_USER_ID="$ADMIN_USER_ID" -a "$APP_NAME"
    heroku config:set ENVIRONMENT="production" -a "$APP_NAME"
    
    # Deploy
    print_info "Deploy dell'applicazione..."
    git add .
    git commit -m "Deploy to Heroku" || true
    heroku git:remote -a "$APP_NAME"
    git push heroku main
    
    print_success "Deploy su Heroku completato!"
    heroku open -a "$APP_NAME"
}

# Deploy locale con Docker
deploy_local() {
    print_info "Deploy locale con Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker non installato"
        echo "Installa Docker da: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose non installato"
        exit 1
    fi
    
    # Crea file .env se non esiste
    if [[ ! -f ".env" ]]; then
        print_info "Creazione file .env..."
        cat > .env << EOF
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ADMIN_USER_ID=$ADMIN_USER_ID
DB_PASSWORD=secure_password_123
ENVIRONMENT=development
EOF
        print_success "File .env creato"
    fi
    
    # Build e avvio
    print_info "Build dell'immagine Docker..."
    docker-compose build
    
    print_info "Avvio dei servizi..."
    docker-compose up -d
    
    print_success "Deploy locale completato!"
    print_info "Servizi disponibili:"
    echo "- Bot: http://localhost:8000"
    echo "- Database: localhost:5432"
    echo "- Redis: localhost:6379"
    
    print_info "Per vedere i logs: docker-compose logs -f"
    print_info "Per fermare: docker-compose down"
}

# Test del deployment
test_deployment() {
    print_info "Test del deployment..."
    
    # Test health check
    if command -v curl &> /dev/null; then
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Health check OK"
        else
            print_warning "Health check fallito (normale se non locale)"
        fi
    fi
    
    print_info "Verifica manualmente che il bot risponda su Telegram"
}

# Menu principale
show_menu() {
    echo ""
    echo "Scegli la piattaforma di deploy:"
    echo "1) Railway (Raccomandato - Gratuito)"
    echo "2) Render (Gratuito con limitazioni)"
    echo "3) Heroku (Gratuito limitato)"
    echo "4) Locale con Docker"
    echo "5) Solo test"
    echo "0) Esci"
    echo ""
}

# Main
main() {
    check_files
    
    # Carica variabili d'ambiente se .env esiste
    if [[ -f ".env" ]]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    check_env
    
    while true; do
        show_menu
        read -p "Scelta: " choice
        
        case $choice in
            1)
                deploy_railway
                test_deployment
                break
                ;;
            2)
                deploy_render
                break
                ;;
            3)
                deploy_heroku
                test_deployment
                break
                ;;
            4)
                deploy_local
                test_deployment
                break
                ;;
            5)
                test_deployment
                break
                ;;
            0)
                print_info "Uscita..."
                exit 0
                ;;
            *)
                print_error "Scelta non valida"
                ;;
        esac
    done
    
    print_success "Deploy completato! 🎉"
    echo ""
    echo "Prossimi passi:"
    echo "1. Testa il bot inviando /start su Telegram"
    echo "2. Monitora i logs per eventuali errori"
    echo "3. Configura il monitoraggio se necessario"
}

# Esegui solo se chiamato direttamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
