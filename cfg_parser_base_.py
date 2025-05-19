import re

class CFG:
    def __init__(self):
        self.variables = set()
        self.terminals = set()
        self.productions = {}
        self.start_symbol = None

    def validate_variable(self, var):
        return bool(re.match(r'^[A-Z]$', var))

    def validate_terminal(self, term):
        return bool(re.match(r'^[a-z0-9]$', term))

    def validate_production(self, head, body):
        if not self.validate_variable(head):
            return False
        for symbol in body:
            if symbol != 'epsilon' and not (self.validate_variable(symbol) or self.validate_terminal(symbol)):
                return False
        return True

    def add_variable(self, var):
        if self.validate_variable(var):
            self.variables.add(var)
            if var not in self.productions:
                self.productions[var] = []
            return True
        return False

    def add_terminal(self, term):
        if self.validate_terminal(term):
            self.terminals.add(term)
            return True
        return False

    def add_production(self, head, body):
        if self.validate_production(head, body):
            if head not in self.productions:
                self.productions[head] = []
            self.productions[head].append(body)
            return True
        return False

    def set_start_symbol(self, symbol):
        if self.validate_variable(symbol) and symbol in self.variables:
            self.start_symbol = symbol
            return True
        return False

    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                section = None
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line == 'VARIABLES':
                        section = 'variables'
                        continue
                    elif line == 'TERMINALS':
                        section = 'terminals'
                        continue
                    elif line == 'PRODUCTIONS':
                        section = 'productions'
                        continue
                    elif line == 'START':
                        section = 'start'
                        continue

                    if section == 'variables':
                        if not self.add_variable(line):
                            print(f"Invalid variable: {line}")
                            return False
                    elif section == 'terminals':
                        if not self.add_terminal(line):
                            print(f"Invalid terminal: {line}")
                            return False
                    elif section == 'productions':
                        parts = line.split('->')
                        if len(parts) != 2:
                            print(f"Invalid production format: {line}")
                            return False
                        head = parts[0].strip()
                        bodies = parts[1].strip().split('|')
                        for body in bodies:
                            body_symbols = body.strip().split() or ['epsilon']
                            if not self.add_production(head, body_symbols):
                                print(f"Invalid production: {line}")
                                return False
                    elif section == 'start':
                        if not self.set_start_symbol(line):
                            print(f"Invalid start symbol: {line}")
                            return False
            if not self.variables or not self.terminals or not self.productions or not self.start_symbol:
                print("Incomplete grammar: Missing variables, terminals, productions, or start symbol")
                return False
            return True
        except FileNotFoundError:
            print(f"File {filename} not found")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def load_from_console(self):
        print("Enter variables (one per line, uppercase letters, empty line to end):")
        while True:
            var = input().strip()
            if not var:
                break
            if not self.add_variable(var):
                print(f"Invalid variable: {var}")
                return False

        print("Enter terminals (one per line, lowercase letters or digits, empty line to end):")
        while True:
            term = input().strip()
            if not term:
                break
            if not self.add_terminal(term):
                print(f"Invalid terminal: {term}")
                return False

        print("Enter productions (format: A -> B C | epsilon, one per line, empty line to end):")
        while True:
            prod = input().strip()
            if not prod:
                break
            parts = prod.split('->')
            if len(parts) != 2:
                print(f"Invalid production format: {prod}")
                return False
            head = parts[0].strip()
            bodies = parts[1].strip().split('|')
            for body in bodies:
                body_symbols = body.strip().split() or ['epsilon']
                if not self.add_production(head, body_symbols):
                    print(f"Invalid production: {prod}")
                    return False

        print("Enter start symbol (single uppercase letter):")
        start = input().strip()
        if not self.set_start_symbol(start):
            print(f"Invalid start symbol: {start}")
            return False

        if not self.variables or not self.terminals or not self.productions or not self.start_symbol:
            print("Incomplete grammar: Missing variables, terminals, productions, or start symbol")
            return False
        return True

    def display(self):
        print("Variables:", self.variables)
        print("Terminals:", self.terminals)
        print("Productions:")
        for head, bodies in self.productions.items():
            for body in bodies:
                print(f"{head} -> {' '.join(body) if body != ['epsilon'] else 'epsilon'}")
        print("Start Symbol:", self.start_symbol)

    def parse_string(self, input_string):
        def derive(symbols, remaining_input):
            if not symbols and not remaining_input:
                return True
            if not symbols or (not remaining_input and symbols != ['epsilon']):
                return False
            first, *rest = symbols
            if first in self.terminals:
                if remaining_input and first == remaining_input[0]:
                    return derive(rest, remaining_input[1:])
                else:
                    return False
            elif first in self.variables:
                for production in self.productions.get(first, []):
                    if derive(production + rest, remaining_input):
                        return True
                return False
        return derive([self.start_symbol], list(input_string))

def get_derivation_steps(self, input_string, strategy='left'):
        """
        Generate and print the leftmost or rightmost derivation steps with cycle detection.
        Returns a list of steps or None if the string is not derivable.
        """
        steps = []
        visited_states = set()  # Keep track of (current_symbols, input_index)

        def derive(symbols, remaining_input, derivation_path):
            current_state = (" ".join(symbols), len(input_string) - len(remaining_input))
            if current_state in visited_states:
                return False  # Avoid infinite loops

            visited_states.add(current_state)

            if not symbols and not remaining_input:
                steps.append(' '.join(derivation_path))
                return True
            if not symbols or (not remaining_input and symbols != ['epsilon']):
                return False

            if strategy == 'left':
                for i, sym in enumerate(symbols):
                    if sym in self.variables:
                        for prod in self.productions[sym]:
                            new_symbols = symbols[:i] + (prod if prod != ['epsilon'] else []) + symbols[i+1:]
                            derivation_path.append(' '.join(new_symbols))
                            if derive(new_symbols, remaining_input, derivation_path):
                                return True
                            derivation_path.pop()
                        return False  # If a variable is found, try all its productions before backtracking
                if "".join(symbols) == input_string:
                    steps.append(" ".join(symbols))
                    return True
                return False

            elif strategy == 'right':
                for i in reversed(range(len(symbols))):
                    sym = symbols[i]
                    if sym in self.variables:
                        for prod in self.productions[sym]:
                            new_symbols = symbols[:i] + (prod if prod != ['epsilon'] else []) + symbols[i+1:]
                            derivation_path.append(' '.join(new_symbols))
                            if derive(new_symbols, remaining_input, derivation_path):
                                return True
                            derivation_path.pop()
                        return False # If a variable is found, try all its productions before backtracking
                if "".join(symbols) == input_string:
                    steps.append(" ".join(symbols))
                    return True
                return False

            return False

        initial = [self.start_symbol]
        steps.append(' '.join(initial))
        if derive(initial, list(input_string), steps):
            print(f"\n{strategy.capitalize()}most derivation of '{input_string}':")
            for step in steps:
                print("=>", step)
            return steps
        else:
            print(f"\nNo {strategy}most derivation found for '{input_string}'.")
            return None

def main():
    cfg = CFG()
    print("Choose input method: 1) File 2) Console")
    choice = input().strip()
    success = False
    if choice == '1':
        print("""
Expected file format (e.g., grammar.txt):
VARIABLES
S
A
B
TERMINALS
a
b
PRODUCTIONS
S -> A B
A -> a A | epsilon
B -> b B | epsilon
START
S
""")
        print("Enter filename (e.g., grammar.txt):")
        filename = input().strip()
        success = cfg.load_from_file(filename)
    elif choice == '2':
        success = cfg.load_from_console()
    else:
        print("Invalid choice")
        return

    if success:
        print("\nGrammar loaded successfully!")
        cfg.display()
        print("\nProductions:", cfg.productions)

        # Test derivation
        print("\nEnter a string to derive:")
        test_str = input().strip()
        print("\nChoose derivation type: 1) Leftmost 2) Rightmost")
        strat_choice = input().strip()
        strategy = "left" if strat_choice == "1" else "right"
        cfg.get_derivation_steps(test_str, strategy=strategy)

    else:
        print("Failed to load grammar.")

if __name__ == "__main__":
    main()
