package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"net"
)

// Message IDs
const (
	STORE_BET   = 1
	STORE_BATCH = 2
	FIN         = 3
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
	batchBuf := new(bytes.Buffer)

	// Amount of bets
	if err := binary.Write(batchBuf, binary.BigEndian, uint32(len(bets))); err != nil {
		return "", fmt.Errorf("error writing message ID: %v", err)
	}

	// Bets
	for _, bet := range bets {
		betData, err := encodeBet(bet)
		if err != nil {
			return "", fmt.Errorf("error encoding bet: %v", err)
		}

		// Eliminate the first byte (message id). Not ideal but works for now
		betData = betData[1:]

		// Bet
		if _, err := batchBuf.Write(betData); err != nil {
			return "", fmt.Errorf("error writing bet data: %v", err)
		}
	}

	buf := new(bytes.Buffer)

	// Message ID
	if err := binary.Write(buf, binary.BigEndian, uint8(STORE_BATCH)); err != nil {
		return "", fmt.Errorf("error writing message ID: %v", err)
	}

	// Total length of the batch
	if err := binary.Write(buf, binary.BigEndian, uint32(batchBuf.Len())); err != nil {
		return "", fmt.Errorf("error writing message ID: %v", err)
	}

	// <amount bets: uint32><bets>
	if _, err := buf.Write(batchBuf.Bytes()); err != nil {
		return "", fmt.Errorf("error appending batch to final buffer: %v", err)
	}

	err := writeExactly(conn, buf.Bytes())
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
