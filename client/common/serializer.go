package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
)

// Encodes a bet in binary with the following format:
// <msg id: ui8><total_len: i32><len1: i32><field 1>...
func encodeBet(bet Bet) ([]byte, error) {
	buf := new(bytes.Buffer)

	if err := binary.Write(buf, binary.BigEndian, uint8(STORE_BET)); err != nil {
		return nil, fmt.Errorf("error writing total length: %v", err)
	}

	fields := []string{bet.Agency, bet.FirstName, bet.LastName, bet.Document, bet.Birthdate, bet.Number}

	totalLength := uint32(0)
	for _, field := range fields {
		totalLength += uint32(4 + len(field))
	}

	if err := binary.Write(buf, binary.BigEndian, totalLength); err != nil {
		return nil, fmt.Errorf("error writing total length: %v", err)
	}

	for _, field := range fields {
		if err := binary.Write(buf, binary.BigEndian, int32(len(field))); err != nil {
			return nil, fmt.Errorf("error writing length: %v", err)
		}

		if _, err := buf.WriteString(field); err != nil {
			return nil, fmt.Errorf("error writing content: %v", err)
		}
	}

	return buf.Bytes(), nil
}

func encodeBatch(bets []Bet) ([]byte, error) {
	batchBuf := new(bytes.Buffer)

	// Amount of bets
	if err := binary.Write(batchBuf, binary.BigEndian, uint32(len(bets))); err != nil {
		return nil, fmt.Errorf("error writing message ID: %v", err)
	}

	// Bets
	for _, bet := range bets {
		betData, err := encodeBet(bet)
		if err != nil {
			return nil, fmt.Errorf("error encoding bet: %v", err)
		}

		// Eliminate the first byte (message id). Not ideal but works for now
		betData = betData[1:]

		// Bet
		if _, err := batchBuf.Write(betData); err != nil {
			return nil, fmt.Errorf("error writing bet data: %v", err)
		}
	}

	buf := new(bytes.Buffer)

	// Message ID
	if err := binary.Write(buf, binary.BigEndian, uint8(STORE_BATCH)); err != nil {
		return nil, fmt.Errorf("error writing message ID: %v", err)
	}

	// Total length of the batch
	if err := binary.Write(buf, binary.BigEndian, uint32(batchBuf.Len())); err != nil {
		return nil, fmt.Errorf("error writing message ID: %v", err)
	}

	// <amount bets: uint32><bets>
	if _, err := buf.Write(batchBuf.Bytes()); err != nil {
		return nil, fmt.Errorf("error appending batch to final buffer: %v", err)
	}

	return buf.Bytes(), nil
}

func getFinMsg() ([]byte, error) {
	buf := new(bytes.Buffer)

	if err := binary.Write(buf, binary.BigEndian, uint8(FIN)); err != nil {
		return nil, fmt.Errorf("error creating FIN message: %v", err)
	}

	return buf.Bytes(), nil
}
