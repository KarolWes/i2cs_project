import logging

from src import util, ot, utli_karol


class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """

    def __init__(self, oblivious_transfer=True):
        self.private_value = utli_karol.private_func("Bob")
        self.socket = util.EvaluatorSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    def listen(self):
        """Start listening for Alice messages."""
        logging.info("Start listening")
        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                self.send_evaluation(entry)
        except KeyboardInterrupt:
            logging.info("Stop listening")

    def send_evaluation(self, entry):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        a_wires = circuit.get("alice", [])  # list of Alice's wires
        b_wires = circuit.get("bob", [])  # list of Bob's wires

        print(f"Received {circuit['id']}")

        # Generate input to circuit based on the value obtained on init
        bits_b = [int(b) for b in self.private_value]  # Bob's inputs

        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice
        result = self.ot.send_result(circuit, garbled_tables, pbits_out,
                                     b_inputs_clear)
        int_result = int("".join(str(result[k]) for k in result.keys()), 2)
        print(f"Result of function is {int_result}")

    def verify(self, entry):
        # TODO check how to install this into code
        logging.info("Verifying")
        alice_max = entry["private_max"]
        general_max = entry["obtained_max"]
        res = max(alice_max, int(self.private_value, 2)) == general_max
        self.socket.send(res)
