package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"

	_ "modernc.org/sqlite"
)

type DB struct {
	conn *sql.DB
	path string
}

func NewDB(dbPath string) (*DB, error) {
	if dbPath == "" {
		home, _ := os.UserHomeDir()
		dbPath = filepath.Join(home, ".chemmaster", "chemmaster.db")
	}
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("create db directory: %w", err)
	}
	conn, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("open database: %w", err)
	}
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
	return db, nil
}

func (db *DB) Close() {
	if db.conn != nil {
		db.conn.Close()
	}
}

func (db *DB) createTables() error {
	// Check if elements table exists and has correct schema
	var colCount int
	err := db.conn.QueryRow(`SELECT COUNT(*) FROM pragma_table_info('elements') WHERE name='electron_config'`).Scan(&colCount)
	if err == nil && colCount == 0 {
		// Table exists but missing new columns — drop and recreate
		db.conn.Exec("DROP TABLE IF EXISTS elements")
	}

	_, err = db.conn.Exec(`
	CREATE TABLE IF NOT EXISTS elements (
		symbol TEXT PRIMARY KEY,
		name_en TEXT NOT NULL,
		name_cn TEXT NOT NULL,
		atomic_number INTEGER NOT NULL UNIQUE,
		atomic_mass REAL NOT NULL,
		electron_config TEXT DEFAULT '',
		period INTEGER DEFAULT 1,
		group_num INTEGER DEFAULT 1,
		category TEXT DEFAULT 'nonmetal',
		electronegativity REAL DEFAULT 0
	);
	CREATE TABLE IF NOT EXISTS compounds (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT, name_cn TEXT, formula TEXT NOT NULL,
		molecular_weight REAL, cas_number TEXT, smiles TEXT,
		description TEXT, source TEXT DEFAULT 'local',
		cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(formula, name)
	);
	CREATE TABLE IF NOT EXISTS reactions (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		equation TEXT NOT NULL UNIQUE,
		reactants TEXT, products TEXT, reaction_type TEXT,
		conditions TEXT, source TEXT DEFAULT 'local'
	);
	CREATE TABLE IF NOT EXISTS settings (
		key TEXT PRIMARY KEY, value TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS api_cache (
		key TEXT PRIMARY KEY, value TEXT NOT NULL, source TEXT,
		cached_at DATETIME DEFAULT CURRENT_TIMESTAMP, expires_at REAL
	);
	CREATE INDEX IF NOT EXISTS idx_compounds_formula ON compounds(formula);
	CREATE INDEX IF NOT EXISTS idx_compounds_name ON compounds(name);
	`)
	return err
}

func (db *DB) seedData() error {
	var count int
	if err := db.conn.QueryRow("SELECT COUNT(*) FROM elements").Scan(&count); err != nil {
		return err
	}
	if count == len(AllElements) {
		return nil
	}
	if count > 0 {
		db.conn.Exec("DELETE FROM elements")
	}

	tx, err := db.conn.Begin()
	if err != nil {
		return err
	}
	stmt, err := tx.Prepare(`INSERT OR IGNORE INTO elements
		(symbol, name_en, name_cn, atomic_number, atomic_mass, electron_config, period, group_num, category, electronegativity)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
	if err != nil {
		tx.Rollback()
		return err
	}
	defer stmt.Close()
	for _, e := range AllElements {
		if _, err := stmt.Exec(e.Symbol, e.NameEN, e.NameCN, e.AtomicNumber, e.AtomicMass, e.ElectronConfig, e.Period, e.Group, e.Category, e.Electronegativity); err != nil {
			tx.Rollback()
			return err
		}
	}
	if err := tx.Commit(); err != nil {
		return err
	}
	return db.seedCompounds()
}

// ===== Query methods =====

type ElementResult struct {
	Symbol            string  `json:"symbol"`
	NameEN            string  `json:"nameEn"`
	NameCN            string  `json:"nameCn"`
	AtomicNumber      int     `json:"atomicNumber"`
	AtomicMass        float64 `json:"atomicMass"`
	ElectronConfig    string  `json:"electronConfig"`
	Period            int     `json:"period"`
	Group             int     `json:"group"`
	Category          string  `json:"category"`
	Electronegativity float64 `json:"electronegativity"`
}

const elementCols = "symbol, name_en, name_cn, atomic_number, atomic_mass, electron_config, period, group_num, category, electronegativity"

func scanElement(rows *sql.Rows) (ElementResult, error) {
	var e ElementResult
	err := rows.Scan(&e.Symbol, &e.NameEN, &e.NameCN, &e.AtomicNumber, &e.AtomicMass, &e.ElectronConfig, &e.Period, &e.Group, &e.Category, &e.Electronegativity)
	return e, err
}

func (db *DB) GetAllElements() ([]ElementResult, error) {
	rows, err := db.conn.Query("SELECT " + elementCols + " FROM elements ORDER BY atomic_number")
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var results []ElementResult
	for rows.Next() {
		e, err := scanElement(rows)
		if err != nil {
			continue
		}
		results = append(results, e)
	}
	return results, nil
}

func (db *DB) GetElement(symbol string) (*ElementResult, error) {
	row := db.conn.QueryRow("SELECT "+elementCols+" FROM elements WHERE symbol = ?", symbol)
	var e ElementResult
	err := row.Scan(&e.Symbol, &e.NameEN, &e.NameCN, &e.AtomicNumber, &e.AtomicMass, &e.ElectronConfig, &e.Period, &e.Group, &e.Category, &e.Electronegativity)
	if err != nil {
		return nil, err
	}
	return &e, nil
}

func (db *DB) SearchElements(query string) ([]ElementResult, error) {
	rows, err := db.conn.Query(
		"SELECT "+elementCols+" FROM elements WHERE symbol LIKE ? OR name_en LIKE ? OR name_cn LIKE ? OR CAST(atomic_number AS TEXT) LIKE ?",
		"%"+query+"%", "%"+query+"%", "%"+query+"%", "%"+query+"%",
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var results []ElementResult
	for rows.Next() {
		e, err := scanElement(rows)
		if err != nil {
			continue
		}
		results = append(results, e)
	}
	return results, nil
}

type CompoundResult struct {
	ID              int     `json:"id"`
	Name            string  `json:"name"`
	NameCN          string  `json:"nameCn"`
	Formula         string  `json:"formula"`
	MolecularWeight float64 `json:"molecularWeight"`
	CASNumber       string  `json:"casNumber"`
	Source          string  `json:"source"`
}

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
		c.NameCN, c.CASNumber, c.Source = nameCN.String, cas.String, source.String
		results = append(results, c)
	}
	return results, nil
}

func (db *DB) seedCompounds() error {
	var count int
	if err := db.conn.QueryRow("SELECT COUNT(*) FROM compounds").Scan(&count); err != nil {
		return err
	}
	if count > 0 {
		return nil
	}
	compounds := []struct {
		Name, NameCN, Formula, CAS string
		MW                         float64
	}{
		{"Water", "水", "H2O", "7732-18-5", 18.015},
		{"Sodium chloride", "氯化钠", "NaCl", "7647-14-5", 58.443},
		{"Sulfuric acid", "硫酸", "H2SO4", "7664-93-9", 98.079},
		{"Hydrochloric acid", "盐酸", "HCl", "7647-01-0", 36.461},
		{"Sodium hydroxide", "氢氧化钠", "NaOH", "1310-73-2", 39.997},
		{"Calcium carbonate", "碳酸钙", "CaCO3", "471-34-1", 100.087},
		{"Glucose", "葡萄糖", "C6H12O6", "50-99-7", 180.156},
		{"Ethanol", "乙醇", "C2H5OH", "64-17-5", 46.069},
		{"Acetic acid", "乙酸", "CH3COOH", "64-19-7", 60.052},
		{"Carbon dioxide", "二氧化碳", "CO2", "124-38-9", 44.010},
		{"Ammonia", "氨", "NH3", "7664-41-7", 17.031},
		{"Methane", "甲烷", "CH4", "74-82-8", 16.043},
		{"Iron(III) oxide", "氧化铁", "Fe2O3", "1309-37-1", 159.687},
		{"Copper(II) sulfate", "硫酸铜", "CuSO4", "7758-98-7", 159.609},
		{"Potassium permanganate", "高锰酸钾", "KMnO4", "7722-64-7", 158.034},
		{"Calcium hydroxide", "氢氧化钙", "Ca(OH)2", "1305-62-0", 74.093},
		{"Aluminium sulfate", "硫酸铝", "Al2(SO4)3", "10043-01-3", 342.151},
		{"Sodium carbonate", "碳酸钠", "Na2CO3", "497-19-8", 105.989},
		{"Hydrogen peroxide", "过氧化氢", "H2O2", "7722-84-1", 34.015},
		{"Nitric acid", "硝酸", "HNO3", "7697-37-2", 63.013},
		{"Phosphoric acid", "磷酸", "H3PO4", "7664-38-2", 97.995},
		{"Potassium dichromate", "重铬酸钾", "K2Cr2O7", "7778-50-9", 294.185},
		{"Silver nitrate", "硝酸银", "AgNO3", "7761-88-8", 169.873},
		{"Barium sulfate", "硫酸钡", "BaSO4", "7727-43-7", 233.391},
		{"Sodium bicarbonate", "碳酸氢钠", "NaHCO3", "144-55-8", 84.007},
	}
	tx, err := db.conn.Begin()
	if err != nil {
		return err
	}
	stmt, err := tx.Prepare("INSERT OR IGNORE INTO compounds (name, name_cn, formula, molecular_weight, cas_number, source) VALUES (?, ?, ?, ?, ?, 'local')")
	if err != nil {
		tx.Rollback()
		return err
	}
	defer stmt.Close()
	for _, c := range compounds {
		if _, err := stmt.Exec(c.Name, c.NameCN, c.Formula, c.MW, c.CAS); err != nil {
			tx.Rollback()
			return err
		}
	}
	return tx.Commit()
}

func (db *DB) GetSetting(key string) (string, error) {
	var value string
	err := db.conn.QueryRow("SELECT value FROM settings WHERE key = ?", key).Scan(&value)
	if err == sql.ErrNoRows {
		return "", nil
	}
	return value, err
}

func (db *DB) SetSetting(key, value string) error {
	_, err := db.conn.Exec("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", key, value)
	return err
}

func (db *DB) CacheGet(key string) (string, bool) {
	var value string
	err := db.conn.QueryRow(
		"SELECT value FROM api_cache WHERE key = ? AND (expires_at IS NULL OR expires_at > strftime('%s','now'))", key,
	).Scan(&value)
	if err != nil {
		return "", false
	}
	return value, true
}

func (db *DB) CacheSet(key, value, source string, ttlSeconds int) error {
	_, err := db.conn.Exec(
		"INSERT OR REPLACE INTO api_cache (key, value, source, expires_at) VALUES (?, ?, ?, strftime('%s','now') + ?)",
		key, value, source, ttlSeconds,
	)
	return err
}
