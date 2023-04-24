import logging

import ot
import util
import utli_karol


class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
        filename: Optional; path to the file, from which to read data.
            Default is empty string, and data is read from console.
    """

    def __init__(self, oblivious_transfer=True, filename=""):

        self.socket = util.EvaluatorSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)
        # data is equal to list of inputs, obtained through private_func
        # (either from console or from file)
        # private value will be max of input, when data will be cleaned up during communication
        self.private_value = "0"
        if filename == "":
            self.data, _ = utli_karol.private_func("Bob")
        else:
            self.data, _ = utli_karol.private_func("Bob", file_read=True, filename=filename)



    def listen(self):
        """Start listening for Alice messages."""
        logging.info("Start listening")
        try:
            for entry in self.socket.poll_socket():
                self.socket.send(True)
                # this part was adjusted to the requirements of task: verification
                # length of the entry dict is 5 for calculation and 2 for verification
                # "else" is a safeguard, should never occur.
                if len(entry) == 5:
                    # calculate private value (local max) based on saved data and max len obtained through communication
                    _, self.private_value = utli_karol.private_func(data=self.data, bit_size=entry["bitlength"])
                    if entry["printout"] != "none":
                        self.send_evaluation(entry)
                    self.send_response(entry)
                elif len(entry) == 2:
                    self.verify(entry)
                else:
                    logging.info("Stop listening")
                    exit(1)
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
        N = len(a_wires) + len(b_wires)

        print(f"Received {circuit['id']}")

        # Generate all possible inputs for both Alice and Bob
        for bits in [format(n, 'b').zfill(N) for n in range(2 ** N)]:
            bits_b = [int(b) for b in bits[N - len(b_wires):]]  # Bob's inputs

            # Create dict mapping each wire of Bob to Bob's input
            b_inputs_clear = {
                b_wires[i]: bits_b[i]
                for i in range(len(b_wires))
            }

            # Evaluate and send result to Alice
            self.ot.send_result(circuit, garbled_tables, pbits_out,
                                b_inputs_clear)

    def send_response(self, entry):
        """Cased on a circuit and input from Alice calculate the result.
            Function is based on original send_evaluation function.
            Instead of generating output for every possible input, it relies on the received input only

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        # initiation of the function, exactly the same as in original,
        # optimized for required variables only
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        b_wires = circuit.get("bob", [])  # list of Bob's wires

        print(f"Received {circuit['id']}")

        # Generate input to circuit based on the value obtained on init
        bits_b = [int(b) for b in self.private_value]  # Bob's inputs

        # Create dict mapping each wire of Bob to Bob's input, no changes here
        b_inputs_clear = {
            b_wires[i]: bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice,
        # also obtain the result for yourself and print
        result = self.ot.send_result(circuit, garbled_tables, pbits_out,
                                     b_inputs_clear)
        int_result = utli_karol.circuit_output_to_int(result)
        print(f"Result of function is {int_result}")

    def verify(self, entry):
        """
        Function verifies if the yao works correctly.
        This also compromises the secrecy of data between parties
        Since to obtain verification we send the plaintext values and check if the circuit worked
        The result is printed in readable form and is transferred back to Alice

        Args:
            entry: dictionary received from Alice containing two values:
                    alice_max and general_max (names self-explanatory)

        """
        logging.info("Verifying")
        self.socket.receive()  # for establishing communication between parties
        alice_max = entry["alice_max"]
        general_max = entry["general_max"]
        verification_max = max(alice_max, int(self.private_value, 2))
        res = verification_max == general_max
        if res:
            print("Verified correctly")
        else:
            print(f"Error! Through transfer obtained: {general_max}, correct value: {verification_max}")
        self.socket.send(res)
