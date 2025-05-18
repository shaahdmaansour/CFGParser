import re

class CFG:
    def __init__(self):
        self.variables = set()
        self.terminals = set()
        self.productions = {}
        self.start_symbol = None

    def validate_variable(self, var):
        """Check if a variable is a single uppercase letter."""
        return bool(re.match(r'^[A-Z]$', var))

    def validate_terminal(self, term):
        """Check if a terminal is a single lowercase letter or digit."""
        return bool(re.match(r'^[a-z0-9]$', term))

    def validate_production(self, head, body):
        """Validate a production rule."""
        if not self.validate_variable(head):
            return False
        for symbol in body:
            if symbol != 'epsilon' and not (self.validate_variable(symbol) or self.validate_terminal(symbol)):
                return False
        return True

    def add_variable(self, var):
        """Add a variable if valid."""
        if self.validate_variable(var):
            self.variables.add(var)
            if var not in self.productions:
                self.productions[var] = []
            return True
        return False

    def add_terminal(self, term):
        """Add a terminal if valid."""
        if self.validate_terminal(term):
            self.terminals.add(term)
            return True
        return False

    def add_production(self, head, body):
        """Add a production rule if valid."""
        if self.validate_production(head, body):
            if head not in self.productions:
                self.productions[head] = []
            self.productions[head].append(body)
            return True
        return False

    def set_start_symbol(self, symbol):
        """Set the start symbol if valid and exists in variables."""
        if self.validate_variable(symbol) and symbol in self.variables:
            self.start_symbol = symbol
            return True
        return False

    def load_from_file(self, filename):
        """Load CFG from a text file."""
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
        """Load CFG from console input."""
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
        """Display the loaded CFG."""
        print("Variables:", self.variables)
        print("Terminals:", self.terminals)
        print("Productions:")
        for head, bodies in self.productions.items():
            for body in bodies:
                print(f"{head} -> {' '.join(body) if body != ['epsilon'] else 'epsilon'}")
        print("Start Symbol:", self.start_symbol)

def main():
    cfg = CFG()
    print("Choose input method: 1) File 2) Console")
    choice = input().strip()
    success = False
    if choice == '1':
        print("""
Expected file format (e.g., grammar.txt):
VARIABLES
[One uppercase letter per line, e.g.]
S
A
B
TERMINALS
[One lowercase letter or digit per line, e.g.]
a
b
PRODUCTIONS
[One rule per line, format: X -> Y Z | epsilon, e.g.]
S -> A B
A -> a A | epsilon
B -> b B | epsilon
START
[Single uppercase letter, e.g.]
S
- Use spaces between symbols in productions.
- No extra spaces or blank lines within sections.
- Save as UTF-8 text file.
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
        print("Grammar loaded successfully!")
        cfg.display()
    else:
        print("Failed to load grammar")

if __name__ == "__main__":
    main()