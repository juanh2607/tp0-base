package common

import (
	"encoding/binary"
	"fmt"
	"net"
)

// Message IDs
const (
	STORE_BET   = 1
	STORE_BATCH = 2
	FIN         = 3
	END_BETS    = 4
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

func SendBatch(conn net.Conn, bets []Bet) (string, error) {
	data, err := encodeBatch(bets)
	if err != nil {
		return "", fmt.Errorf("error serializing bets: %v", err)
	}

	err = writeExactly(conn, data)
	if err != nil {
		return "", fmt.Errorf("error sending batch: %v", err)
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

// Send FIN message to end communication with the server
func SendFin(conn net.Conn) error {
	msg, err := getFinMsg()
	if err != nil {
		return fmt.Errorf("error creating FIN message: %v", err)
	}

	if err := writeExactly(conn, msg); err != nil {
		return fmt.Errorf("error sending FIN message: %v", err)
	}

	return nil
}

// Send END_BETS to server and wait for result
func SendEndBets(conn net.Conn) error {
	msg, err := getEndBetsMsg()
	if err != nil {
		return fmt.Errorf("error creating END_BETS message: %v", err)
	}

	if err := writeExactly(conn, msg); err != nil {
		return fmt.Errorf("error sending END_BETS message: %v", err)
	}

	log.Info("action: send_END_BETS | result: success")
	log.Info("action: consulta_ganadores | result: in_progress")

	// Read server response
	sizeBytes, err := readExactly(conn, 4)
	if err != nil {
		return fmt.Errorf("error reading message size: %v", err)
	}
	msgSize := int(binary.BigEndian.Uint32(sizeBytes))

	msg, err = readExactly(conn, msgSize)
	if err != nil {
		return fmt.Errorf("error reading message: %v", err)
	}

	return nil
}
