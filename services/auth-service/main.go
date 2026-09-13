package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	_ "github.com/jackc/pgx/v4/stdlib"
	"github.com/joho/godotenv"
)

// App struct (para injeção de dependência)
type App struct {
	DB        *sql.DB
	MasterKey string
}

func main() {
	// Carrega o .env para desenvolvimento local. Em produção, isso não fará nada.
	_ = godotenv.Load()

	// --- Configuração ---
	port := os.Getenv("PORT")
	if port == "" {
		port = "8001" // Porta padrão
	}

	databaseURL, err := databaseDSN()
	if err != nil {
		log.Fatalf("Configuração do PostgreSQL inválida: %v", err)
	}

	masterKey := os.Getenv("MASTER_KEY")
	if masterKey == "" {
		log.Fatal("MASTER_KEY deve ser definida")
	}

	// --- Conexão com o Banco ---
	db, err := connectDB(databaseURL)
	if err != nil {
		log.Fatalf("Não foi possível conectar ao banco de dados: %v", err)
	}
	defer func() {
		if err := db.Close(); err != nil {
			log.Printf("Unable to close database: %v", err)
		}
	}()

	if err := bootstrapAPIKey(db); err != nil {
		log.Fatalf("Não foi possível criar a chave inicial da API: %v", err)
	}

	app := &App{
		DB:        db,
		MasterKey: masterKey,
	}

	// --- Rotas da API ---
	mux := http.NewServeMux()
	mux.HandleFunc("/health", app.healthHandler)

	// Endpoint público para validar uma chave
	mux.HandleFunc("/validate", app.validateKeyHandler)

	// Endpoints de "admin" para criar/gerenciar chaves
	// Eles são protegidos pelo middleware de autenticação
	mux.Handle("/admin/keys", app.masterKeyAuthMiddleware(http.HandlerFunc(app.createKeyHandler)))

	log.Printf("Serviço de Autenticação (Go) rodando na porta %s", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatal(err)
	}
}

// connectDB inicializa e testa a conexão com o PostgreSQL
func connectDB(databaseURL string) (*sql.DB, error) {
	db, err := sql.Open("pgx", databaseURL)
	if err != nil {
		return nil, err
	}

	if err = db.Ping(); err != nil {
		return nil, err
	}

	log.Println("Conectado ao PostgreSQL com sucesso!")
	return db, nil
}

func bootstrapAPIKey(db *sql.DB) error {
	bootstrapKey := os.Getenv("BOOTSTRAP_API_KEY")
	if bootstrapKey == "" {
		return nil
	}

	keyName := os.Getenv("BOOTSTRAP_API_KEY_NAME")
	if keyName == "" {
		keyName = "bootstrap-service-key"
	}

	_, err := db.Exec(
		"INSERT INTO api_keys (name, key_hash) VALUES ($1, $2) ON CONFLICT (key_hash) DO NOTHING",
		keyName,
		hashAPIKey(bootstrapKey),
	)
	if err != nil {
		return err
	}

	log.Printf("Chave inicial da API disponível (Name: %s)", keyName)
	return nil
}
