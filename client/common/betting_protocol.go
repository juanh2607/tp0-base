package common

import (
	"bytes"
	"fmt"
	"net"
)

// Message IDs
const (
	STORE_BET = 1
)

type Bet struct {
	Agency    string
	FirstName string
	LastName  string
	Document  string
	Birthdate string
	Number    string
}

func SendBet(conn net.Conn, bet Bet) (string, error) {
	betData, err := encodeBet(bet)
	if err != nil {
		return "", fmt.Errorf("error serializing bet: %v", err)
	}

	_, err = conn.Write(betData)
	if err != nil {
		return "", fmt.Errorf("error sending bet: %v", err)
	}

	// Read server response
	reader := new(bytes.Buffer)
	_, err = reader.ReadFrom(conn)
	if err != nil {
		return "", fmt.Errorf("error receiving answer: %v", err)
	}

	return reader.String(), nil
}
