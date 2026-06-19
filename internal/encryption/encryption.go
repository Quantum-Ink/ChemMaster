package encryption

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"golang.org/x/crypto/pbkdf2"
)

// Manager handles AES-256 encryption/decryption for sensitive data.
type Manager struct {
	key []byte
}

// NewManager creates a new encryption manager.
// It derives a key from a machine-specific secret.
func NewManager() *Manager {
	key := deriveKey()
	return &Manager{key: key}
}

// keyFilePath returns the path to the stored key salt.
func keyFilePath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		home = "."
	}
	return filepath.Join(home, ".chemmaster", ".key_salt")
}

// deriveKey derives an AES-256 key using PBKDF2 with a persistent random salt.
// On first run, a random salt is generated and saved; on subsequent runs it is reused.
func deriveKey() []byte {
	hostname, _ := os.Hostname()
	home, _ := os.UserHomeDir()
	passphrase := fmt.Sprintf("chemmaster-%s-%s", hostname, home)

	saltPath := keyFilePath()
	salt, err := os.ReadFile(saltPath)
	if err != nil {
		// First run: generate and persist a random 16-byte salt
		salt = make([]byte, 16)
		if _, err := rand.Read(salt); err != nil {
			panic("encryption: cannot generate random salt: " + err.Error())
		}
		dir := filepath.Dir(saltPath)
		os.MkdirAll(dir, 0700)
		if err := os.WriteFile(saltPath, salt, 0600); err != nil {
			panic("encryption: cannot save key salt: " + err.Error())
		}
	}

	// PBKDF2 with 100,000 iterations and SHA-256
	return pbkdf2.Key([]byte(passphrase), salt, 100_000, 32, sha256.New)
}

// Encrypt encrypts plaintext using AES-256-GCM.
func (m *Manager) Encrypt(plaintext string) (string, error) {
	block, err := aes.NewCipher(m.key)
	if err != nil {
		return "", fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("create GCM: %w", err)
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return "", fmt.Errorf("generate nonce: %w", err)
	}

	ciphertext := gcm.Seal(nonce, nonce, []byte(plaintext), nil)
	return base64.StdEncoding.EncodeToString(ciphertext), nil
}

// Decrypt decrypts ciphertext using AES-256-GCM.
func (m *Manager) Decrypt(encoded string) (string, error) {
	ciphertext, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return "", fmt.Errorf("decode base64: %w", err)
	}

	block, err := aes.NewCipher(m.key)
	if err != nil {
		return "", fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("create GCM: %w", err)
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return "", fmt.Errorf("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return "", fmt.Errorf("decrypt: %w", err)
	}

	return string(plaintext), nil
}

