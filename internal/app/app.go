package app

import (
	"context"
	"log"

	"chemmaster/internal/chemistry"
	"chemmaster/internal/database"
	"chemmaster/internal/encryption"
	"chemmaster/internal/plugin"
	"chemmaster/internal/provider"
)

// App is the main application struct bound to the Wails runtime.
type App struct {
	ctx          context.Context
	db           *database.DB
	formulaEng   *chemistry.FormulaEngine
	balancer     *chemistry.EquationBalancer
	reactionEng  *chemistry.ReactionEngine
	ionEng       *chemistry.IonEngine
	renderer     *chemistry.Renderer
	pluginMgr    *plugin.Manager
	providerMgr  *provider.Manager
	encMgr       *encryption.Manager
}

// NewApp creates a new App instance.
func NewApp() *App {
	return &App{}
}

// Startup is called when the app starts.
func (a *App) Startup(ctx context.Context) {
	a.ctx = ctx
	log.Println("ChemMaster starting...")

	// Initialize encryption manager
	a.encMgr = encryption.NewManager()

	// Initialize database
	db, err := database.NewDB("")
	if err != nil {
		log.Printf("Database init error: %v", err)
	} else {
		a.db = db
	}

	// Initialize chemistry engines
	a.formulaEng = chemistry.NewFormulaEngine()
	a.balancer = chemistry.NewEquationBalancer()
	a.reactionEng = chemistry.NewReactionEngine()
	a.ionEng = chemistry.NewIonEngine()
	a.renderer = chemistry.NewRenderer()

	// Initialize plugin manager
	a.pluginMgr = plugin.NewManager()

	// Initialize provider manager
	a.providerMgr = provider.NewManager(a.db)

	log.Println("ChemMaster started successfully")
}

// Shutdown is called when the app shuts down.
func (a *App) Shutdown(ctx context.Context) {
	if a.db != nil {
		a.db.Close()
	}
	log.Println("ChemMaster shut down")
}
