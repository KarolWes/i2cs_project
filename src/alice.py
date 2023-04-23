import logging
import garbler
import ot
import util
import utli_karol


class Alice(garbler.YaoGarbler):
    """Alice is the creator of the Yao circuit.

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice will finally print the truth table of the circuit
    for all combination of Alice-Bob inputs.

    Alice does not know Bob's inputs but for the purpose
    of printing the truth table only, Alice assumes that Bob's inputs follow
    a specific order.

    Attributes:
        circuits: the JSON file containing circuits
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default)
        print_mode: Optional; if set to anything but "none", would result in evaluation and printing out the circuit table
        filename: Optional; path to the file, from which to read data.
            Default is empty string, and data is read from console
    """

    def __init__(self, circuits, oblivious_transfer=True, print_mode="none", filename=""):
        super().__init__(circuits)
        self.socket = util.GarblerSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)
        # Three more fields:
        # pm defines, if the printing of the garbled tables (and their evaluation) should be performed
        # general_max stores the value obtained from the OT to further use
        # private_value is equal to max of input, obtained through private_func
        # (either from console or from file)
        self.pm = print_mode
        self.general_max = -1
        if filename == "":
            self.private_value = utli_karol.private_func("Alice")
        else:
            self.private_value = utli_karol.private_func("Alice", file_read=True, filename=filename)

    def start(self):
        """Start Yao protocol."""

        for circuit in self.circuits:
            to_send = {
                "circuit": circuit["circuit"],
                "garbled_tables": circuit["garbled_tables"],
                "pbits_out": circuit["pbits_out"],
            }
            logging.debug(f"Sending {circuit['circuit']['id']}")
            self.socket.send_wait(to_send)
            # evaluation
            if self.pm != "none":
                self.print(circuit)

            # main part of communication
            print("-------------")
            self.calculate_response(circuit)
            self.verify()

    def print(self, entry):
        """Print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }
        N = len(a_wires) + len(b_wires)

        print(f"======== {circuit['id']} ========")

        # Generate all inputs for both Alice and Bob
        for bits in [format(n, 'b').zfill(N) for n in range(2 ** N)]:
            bits_a = [int(b) for b in bits[:len(a_wires)]]  # Alice's inputs

            # Map Alice's wires to (key, encr_bit)
            for i in range(len(a_wires)):
                a_inputs[a_wires[i]] = (keys[a_wires[i]][bits_a[i]],
                                        pbits[a_wires[i]] ^ bits_a[i])

            # Send Alice's encrypted inputs and keys to Bob
            result = self.ot.get_result(a_inputs, b_keys)

            # Format output
            str_bits_a = ' '.join(bits[:len(a_wires)])
            str_bits_b = ' '.join(bits[len(a_wires):])
            str_result = ' '.join([str(result[w]) for w in outputs])

            print(f"  Alice{a_wires} = {str_bits_a} "
                  f"Bob{b_wires} = {str_bits_b}  "
                  f"Outputs{outputs} = {str_result}")

        print()

    def calculate_response(self, entry):
        """Proceeds with OT on real data.
        Function based on the original print function.
        Instead of repeating transfer for all possible inputs it takes only the important one
        (i.e. the one corresponding to value calculated in private_func)

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        # initiation of the function, exactly the same as in original,
        # optimized for required variables only
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }

        # Circuit input generated based on private value obtained while initialisation
        bits_a = [int(b) for b in self.private_value]  # Alice's inputs

        # Map Alice's wires to (key, encr_bit), no changes here
        for i in range(len(a_wires)):
            a_inputs[a_wires[i]] = (keys[a_wires[i]][bits_a[i]],
                                    pbits[a_wires[i]] ^ bits_a[i])

        # Send Alice's encrypted inputs and keys to Bob
        result = self.ot.get_result(a_inputs, b_keys)

        # Format output, save for further use, and print
        int_result = utli_karol.circuit_output_to_int(result)
        self.general_max = int_result
        print(f"Output: {int_result}")

    def _get_encr_bits(self, pbit, key0, key1):
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))

    def verify(self):
        """
        prepares data for verification and sends them to Bob
        Prints a verification result
        """
        to_send = {
            "alice_max": int(self.private_value, 2),
            "general_max": self.general_max
        }
        logging.debug(f"Sending data for verification")
        self.socket.send_wait(to_send)
        # this line is needed to properly establish communication between parties
        self.socket.send("connection established")
        result = self.socket.receive()
        print(f"Result of verification: {result}")
