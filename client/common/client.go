package common

import (
	"encoding/csv"
	"net"
	"os"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	BatchMaxAmount int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func getBetsReader() (*csv.Reader, *os.File, error) {
	file, err := os.Open("agency.csv")
	if err != nil {
		return nil, nil, err
	}

	reader := csv.NewReader(file)
	return reader, file, nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	reader, file, err := getBetsReader()
	if err != nil {
		log.Errorf("action: open_file | result: fail | client_id: %v | file: agency.csv | error: %v", c.config.ID, err)
		return
	}
	defer file.Close()

	c.createClientSocket()

	if err := SendSyn(c.conn, c.config.ID); err != nil {
		log.Errorf("action: SYN_msg | result: fail | error: %v", err)
	}
	log.Infof("action: send_SYN | result: success")

	var batch []Bet
	for {
		record, err := reader.Read()
		if err != nil {
			break
		}

		if len(record) < 5 {
			log.Warningf("action: parse_csv | result: fail | client_id: %v | reason: invalid_row | data: %v | data_length: %v", c.config.ID, record, len(record))
			continue
		}

		bet := Bet{
			Agency:    c.config.ID,
			FirstName: record[0],
			LastName:  record[1],
			Document:  record[2],
			Birthdate: record[3],
			Number:    record[4],
		}

		batch = append(batch, bet)

		if len(batch) == c.config.BatchMaxAmount {
			response, err := SendBatch(c.conn, batch)
			if err != nil {
				log.Errorf("action: send_batch | result: fail | client_id: %v | error: %v", c.config.ID, err)
				return
			}

			log.Infof("action: send_batch | result: success | client_id: %v | batch_size: %v | response: %v",
				c.config.ID, len(batch), response)

			// Empty the batch while maintaining its capacity
			batch = batch[:0]
		}
	}

	if len(batch) > 0 {
		response, err := SendBatch(c.conn, batch)
		if err != nil {
			log.Errorf("action: send_batch | result: fail | client_id: %v | error: %v", c.config.ID, err)
			return
		}

		log.Infof("action: send_batch | result: success | client_id: %v | batch_size: %v | response: %v",
			c.config.ID, len(batch), response)
	}

	SendEndBets(c.conn)

	log.Infof("action: send_FIN | result: success | client_id: %v", c.config.ID)
	SendFin(c.conn)

	c.conn.Close()
	c.conn = nil
}

func (c *Client) Shutdown() {
	if c.conn != nil {
		err := c.conn.Close()

		if err != nil {
			log.Errorf("action: shutdown | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)

			return
		}
	}

	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
}
