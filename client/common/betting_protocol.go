package common

import (
	"encoding/binary"
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

	err = writeExactly(conn, betData)
	if err != nil {
		return "", fmt.Errorf("error sending bet: %v", err)
	}

	// Read server response
	sizeBytes, err := readExactly(conn, 4)
	if err != nil {
		return "", fmt.Errorf("error reading message size: %v", err)
	}
	msgSize := int(binary.BigEndian.Uint32(sizeBytes))

	msg, err := readExactly(conn, msgSize)
	if err != nil {
		return "", fmt.Errorf("error reading message: %v", err)
	}

	return string(msg), nil
}
