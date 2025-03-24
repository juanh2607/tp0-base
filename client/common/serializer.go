package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
)

// Encodes a bet in binary with the following format:
// <total_len: i32><len1: i32><field 1>...
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
