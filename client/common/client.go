package common

import (
	"net"
	"time"

	"github.com/op/go-logging"
	"github.com/spf13/viper"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(v *viper.Viper) {
	bet := Bet{
		Agency:    v.GetString("id"),
		FirstName: v.GetString("first_name"),
		LastName:  v.GetString("last_name"),
		Document:  v.GetString("document"),
		Birthdate: v.GetString("birthdate"),
		Number:    v.GetString("number"),
	}

	c.createClientSocket()

	log.Infof("action: sending_bet | result: in_progress | bet_number: %v", bet.Number)

	response, err := SendBet(c.conn, bet)
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}

	if response == "ok" {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", bet.Document, bet.Number)
	} else {
		log.Infof("action: apuesta_enviada | result: fail | response: %v", response)
	}

	c.conn.Close()
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
