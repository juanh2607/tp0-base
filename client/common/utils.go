package common

import "net"

func readExactly(conn net.Conn, n int) ([]byte, error) {
	buf := make([]byte, n)
	totalRead := 0

	for totalRead < n {
		num, err := conn.Read(buf[totalRead:])
		if err != nil {
			return nil, err
		}

		totalRead += num
	}

	return buf, nil
}

func writeExactly(conn net.Conn, data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			return err
		}

		totalSent += n
	}

	return nil
}
