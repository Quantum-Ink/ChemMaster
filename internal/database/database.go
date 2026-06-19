package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"

	_ "modernc.org/sqlite"
)

// DB wraps the SQLite database connection.
type DB struct {
	conn *sql.DB
	path string
}

// NewDB creates or opens the SQLite database.
func NewDB(dbPath string) (*DB, error) {
	if dbPath == "" {
		home, _ := os.UserHomeDir()
		dbPath = filepath.Join(home, ".chemmaster", "chemmaster.db")
	}

	// Ensure directory exists
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("create db directory: %w", err)
	}

	conn, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("open database: %w", err)
	}

	// Enable WAL mode for better concurrency
	if _, err := conn.Exec("PRAGMA journal_mode=WAL"); err != nil {
		conn.Close()
		return nil, fmt.Errorf("set WAL mode: %w", err)
	}

	db := &DB{conn: conn, path: dbPath}
	if err := db.createTables(); err != nil {
		conn.Close()
		return nil, fmt.Errorf("create tables: %w", err)
	}

	if err := db.seedData(); err != nil {
		log.Printf("Warning: seed data error: %v", err)
	}

	log.Printf("Database initialized at %s", dbPath)
	return db, nil
}

// Close closes the database connection.
func (db *DB) Close() {
	if db.conn != nil {
		db.conn.Close()
	}
}

// createTables creates all required tables.
func (db *DB) createTables() error {
	schema := `
	CREATE TABLE IF NOT EXISTS elements (
		symbol TEXT PRIMARY KEY,
		name_en TEXT NOT NULL,
		name_cn TEXT NOT NULL,
		atomic_number INTEGER NOT NULL UNIQUE,
		atomic_mass REAL NOT NULL,
		electron_config TEXT,
		category TEXT,
		period INTEGER,
		group_num INTEGER
	);

	CREATE TABLE IF NOT EXISTS compounds (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		name_cn TEXT,
		formula TEXT NOT NULL,
		molecular_weight REAL,
		cas_number TEXT,
		smiles TEXT,
		description TEXT,
		source TEXT DEFAULT 'local',
		cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(formula, name)
	);

	CREATE TABLE IF NOT EXISTS reactions (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		equation TEXT NOT NULL UNIQUE,
		reactants TEXT,
		products TEXT,
		reaction_type TEXT,
		conditions TEXT,
		source TEXT DEFAULT 'local'
	);

	CREATE TABLE IF NOT EXISTS api_cache (
		key TEXT PRIMARY KEY,
		value TEXT NOT NULL,
		source TEXT,
		cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		expires_at REAL
	);

	CREATE TABLE IF NOT EXISTS settings (
		key TEXT PRIMARY KEY,
		value TEXT NOT NULL
	);

	CREATE INDEX IF NOT EXISTS idx_compounds_formula ON compounds(formula);
	CREATE INDEX IF NOT EXISTS idx_compounds_name ON compounds(name);
	CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at);
	`
	_, err := db.conn.Exec(schema)
	return err
}

// seedData populates initial element data.
func (db *DB) seedData() error {
	// Check if elements table is already populated
	var count int
	err := db.conn.QueryRow("SELECT COUNT(*) FROM elements").Scan(&count)
	if err != nil {
		return err
	}
	if count > 0 {
		return nil // Already seeded
	}

	// Seed elements from the periodic table
	elements := []struct {
		Symbol       string
		NameEN       string
		NameCN       string
		AtomicNumber int
		AtomicMass   float64
	}{
		{"H", "Hydrogen", "氢", 1, 1.008},
		{"He", "Helium", "氦", 2, 4.003},
		{"Li", "Lithium", "锂", 3, 6.941},
		{"Be", "Beryllium", "铍", 4, 9.012},
		{"B", "Boron", "硼", 5, 10.81},
		{"C", "Carbon", "碳", 6, 12.011},
		{"N", "Nitrogen", "氮", 7, 14.007},
		{"O", "Oxygen", "氧", 8, 15.999},
		{"F", "Fluorine", "氟", 9, 18.998},
		{"Ne", "Neon", "氖", 10, 20.180},
		{"Na", "Sodium", "钠", 11, 22.990},
		{"Mg", "Magnesium", "镁", 12, 24.305},
		{"Al", "Aluminium", "铝", 13, 26.982},
		{"Si", "Silicon", "硅", 14, 28.086},
		{"P", "Phosphorus", "磷", 15, 30.974},
		{"S", "Sulfur", "硫", 16, 32.065},
		{"Cl", "Chlorine", "氯", 17, 35.453},
		{"Ar", "Argon", "氩", 18, 39.948},
		{"K", "Potassium", "钾", 19, 39.098},
		{"Ca", "Calcium", "钙", 20, 40.078},
		{"Fe", "Iron", "铁", 26, 55.845},
		{"Cu", "Copper", "铜", 29, 63.546},
		{"Zn", "Zinc", "锌", 30, 65.380},
		{"Ag", "Silver", "银", 47, 107.87},
		{"Au", "Gold", "金", 79, 196.97},
		{"Hg", "Mercury", "汞", 80, 200.59},
		{"Pb", "Lead", "铅", 82, 207.20},
	}

	tx, err := db.conn.Begin()
	if err != nil {
		return err
	}

	stmt, err := tx.Prepare("INSERT OR IGNORE INTO elements (symbol, name_en, name_cn, atomic_number, atomic_mass) VALUES (?, ?, ?, ?, ?)")
	if err != nil {
		tx.Rollback()
		return err
	}
	defer stmt.Close()

	for _, e := range elements {
		if _, err := stmt.Exec(e.Symbol, e.NameEN, e.NameCN, e.AtomicNumber, e.AtomicMass); err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit()
}

// Query methods exposed to frontend

// ElementResult represents an element query result.
type ElementResult struct {
	Symbol       string  `json:"symbol"`
	NameEN       string  `json:"nameEn"`
	NameCN       string  `json:"nameCn"`
	AtomicNumber int     `json:"atomicNumber"`
	AtomicMass   float64 `json:"atomicMass"`
}

// GetElement queries an element by symbol.
func (db *DB) GetElement(symbol string) (*ElementResult, error) {
	row := db.conn.QueryRow(
		"SELECT symbol, name_en, name_cn, atomic_number, atomic_mass FROM elements WHERE symbol = ?",
		symbol,
	)
	var e ElementResult
	err := row.Scan(&e.Symbol, &e.NameEN, &e.NameCN, &e.AtomicNumber, &e.AtomicMass)
	if err != nil {
		return nil, err
	}
	return &e, nil
}

// SearchElements searches elements by name or symbol.
func (db *DB) SearchElements(query string) ([]ElementResult, error) {
	rows, err := db.conn.Query(
		"SELECT symbol, name_en, name_cn, atomic_number, atomic_mass FROM elements WHERE symbol LIKE ? OR name_en LIKE ? OR name_cn LIKE ?",
		"%"+query+"%", "%"+query+"%", "%"+query+"%",
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []ElementResult
	for rows.Next() {
		var e ElementResult
		if err := rows.Scan(&e.Symbol, &e.NameEN, &e.NameCN, &e.AtomicNumber, &e.AtomicMass); err != nil {
			continue
		}
		results = append(results, e)
	}
	return results, nil
}

// CompoundResult represents a compound query result.
type CompoundResult struct {
	ID             int     `json:"id"`
	Name           string  `json:"name"`
	NameCN         string  `json:"nameCn"`
	Formula        string  `json:"formula"`
	MolecularWeight float64 `json:"molecularWeight"`
	CASNumber      string  `json:"casNumber"`
	Source          string  `json:"source"`
}

// SearchCompounds searches compounds by name or formula.
func (db *DB) SearchCompounds(query string) ([]CompoundResult, error) {
	rows, err := db.conn.Query(
		"SELECT id, name, name_cn, formula, molecular_weight, cas_number, source FROM compounds WHERE name LIKE ? OR formula LIKE ? OR name_cn LIKE ?",
		"%"+query+"%", "%"+query+"%", "%"+query+"%",
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []CompoundResult
	for rows.Next() {
		var c CompoundResult
		var nameCN, cas, source sql.NullString
		if err := rows.Scan(&c.ID, &c.Name, &nameCN, &c.Formula, &c.MolecularWeight, &cas, &source); err != nil {
			continue
		}
		c.NameCN = nameCN.String
		c.CASNumber = cas.String
		c.Source = source.String
		results = append(results, c)
	}
	return results, nil
}

// GetSetting retrieves a setting value.
func (db *DB) GetSetting(key string) (string, error) {
	var value string
	err := db.conn.QueryRow("SELECT value FROM settings WHERE key = ?", key).Scan(&value)
	if err == sql.ErrNoRows {
		return "", nil
	}
	return value, err
}

// SetSetting stores a setting value.
func (db *DB) SetSetting(key, value string) error {
	_, err := db.conn.Exec(
		"INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
		key, value,
	)
	return err
}

// CacheGet retrieves a cached value if it hasn't expired.
func (db *DB) CacheGet(key string) (string, bool) {
	var value string
	err := db.conn.QueryRow(
		"SELECT value FROM api_cache WHERE key = ? AND (expires_at IS NULL OR expires_at > strftime('%s','now'))",
		key,
	).Scan(&value)
	if err != nil {
		return "", false
	}
	return value, true
}

// CacheSet stores a value in the cache with TTL in seconds.
func (db *DB) CacheSet(key, value, source string, ttlSeconds int) error {
	_, err := db.conn.Exec(
		"INSERT OR REPLACE INTO api_cache (key, value, source, expires_at) VALUES (?, ?, ?, strftime('%s','now') + ?)",
		key, value, source, ttlSeconds,
	)
	return err
}
