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

// deriveKey derives an AES-256 key from machine-specific data.
func deriveKey() []byte {
	// Use a combination of machine-specific data
	hostname, _ := os.Hostname()
	home, _ := os.UserHomeDir()
	seed := fmt.Sprintf("chemmaster-%s-%s-secret", hostname, home)

	hash := sha256.Sum256([]byte(seed))
	return hash[:]
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

// CredentialStore stores encrypted credentials.
type CredentialStore struct {
	mgr      *Manager
	filePath string
}

// NewCredentialStore creates a new credential store.
func NewCredentialStore() *CredentialStore {
	home, _ := os.UserHomeDir()
	storePath := filepath.Join(home, ".chemmaster", "credentials.enc")
	return &CredentialStore{
		mgr:      NewManager(),
		filePath: storePath,
	}
}

// SaveCredential saves an encrypted credential.
func (cs *CredentialStore) SaveCredential(name, value string) error {
	encrypted, err := cs.mgr.Encrypt(value)
	if err != nil {
		return err
	}

	// Read existing credentials
	creds := cs.loadAll()
	creds[name] = encrypted

	// Write back
	data := ""
	for k, v := range creds {
		data += k + "=" + v + "\n"
	}

	dir := filepath.Dir(cs.filePath)
	os.MkdirAll(dir, 0700)
	return os.WriteFile(cs.filePath, []byte(data), 0600)
}

// LoadCredential loads and decrypts a credential.
func (cs *CredentialStore) LoadCredential(name string) (string, error) {
	creds := cs.loadAll()
	encrypted, ok := creds[name]
	if !ok {
		return "", fmt.Errorf("credential '%s' not found", name)
	}
	return cs.mgr.Decrypt(encrypted)
}

// DeleteCredential removes a credential.
func (cs *CredentialStore) DeleteCredential(name string) error {
	creds := cs.loadAll()
	delete(creds, name)

	data := ""
	for k, v := range creds {
		data += k + "=" + v + "\n"
	}
	return os.WriteFile(cs.filePath, []byte(data), 0600)
}

// loadAll reads all credentials from the file.
func (cs *CredentialStore) loadAll() map[string]string {
	creds := make(map[string]string)
	data, err := os.ReadFile(cs.filePath)
	if err != nil {
		return creds
	}
	for _, line := range splitLines(string(data)) {
		if idx := indexOf(line, '='); idx > 0 {
			key := line[:idx]
			val := line[idx+1:]
			creds[key] = val
		}
	}
	return creds
}

func splitLines(s string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '\n' {
			if i > start {
				lines = append(lines, s[start:i])
			}
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}

func indexOf(s string, c byte) int {
	for i := 0; i < len(s); i++ {
		if s[i] == c {
			return i
		}
	}
	return -1
}