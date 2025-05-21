import pygame
import sys
import os
from cfgParser import CFG

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)
GREEN = (144, 238, 144)
RED = (255, 99, 71)

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CFG Parser GUI")

# Fonts
font_large = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 20)
font_small = pygame.font.SysFont('Arial', 16)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = font_medium.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()
            return True
        return False

class TextBox:
    def __init__(self, x, y, width, height, placeholder="", text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface):
        # Draw background
        color = LIGHT_BLUE if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        # Render text
        if self.text:
            text_surface = font_medium.render(self.text, True, BLACK)
        else:
            text_surface = font_medium.render(self.placeholder, True, GRAY)
            
        # Blit text
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_pos = text_rect.right + 2
            if cursor_pos > self.rect.right - 10:
                cursor_pos = self.rect.right - 10
            pygame.draw.line(surface, BLACK, 
                            (cursor_pos, self.rect.top + 5),
                            (cursor_pos, self.rect.bottom - 5), 2)
            
        # Blink cursor
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.cursor_visible = True
                self.cursor_timer = 0
            return self.active
                
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
            self.cursor_visible = True
            self.cursor_timer = 0
            return True
        return False

class CFGParserGUI:
    def __init__(self):
        self.cfg = CFG()
        self.grammar_loaded = False
        self.current_screen = "main"  # main, file_input, console_input, result
        self.message = ""
        self.message_color = BLACK
        self.filename_input = TextBox(300, 250, 300, 40, "Enter filename...")
        self.test_string_input = TextBox(300, 300, 300, 40, "Enter string to derive...")
        self.console_input = []
        self.console_mode = "variables"  # variables, terminals, productions, start
        self.console_variables = []
        self.console_terminals = []
        self.console_productions = []
        self.console_start = ""
        self.temp_input = TextBox(300, 350, 300, 40, "Enter value...")
        self.derivation_steps = []
        self.result_text = []
        self.current_input_line = 0
        
        # Create buttons
        self.buttons = {
            "main": [
                Button(300, 200, 200, 50, "Load from File", LIGHT_BLUE, DARK_BLUE, self.switch_to_file),
                Button(300, 270, 200, 50, "Load from Console", LIGHT_BLUE, DARK_BLUE, self.switch_to_console),
                Button(300, 340, 200, 50, "Exit", RED, (255, 150, 150), self.exit_app)
            ],
            "file_input": [
                Button(200, 320, 150, 40, "Load Grammar", GREEN, (100, 200, 100), self.load_from_file),
                Button(400, 320, 150, 40, "Back", GRAY, (150, 150, 150), self.back_to_main)
            ],
            "console_input": [
                Button(400, 400, 150, 40, "Submit", GREEN, (100, 200, 100), self.submit_console_input),
                Button(200, 400, 150, 40, "Back", GRAY, (150, 150, 150), self.back_to_main)
            ],
            "string_input": [
                Button(200, 350, 150, 40, "Leftmost", GREEN, (100, 200, 100), lambda: self.derive_string("left")),
                Button(400, 350, 150, 40, "Rightmost", GREEN, (100, 200, 100), lambda: self.derive_string("right")),
                Button(300, 400, 200, 40, "Generate Parse Tree", LIGHT_BLUE, DARK_BLUE, self.generate_parse_tree),
                Button(300, 450, 200, 40, "Back", GRAY, (150, 150, 150), self.back_to_main)
            ],
            "result": [
                Button(300, 500, 200, 40, "Back", GRAY, (150, 150, 150), self.back_to_main),
                Button(300, 450, 200, 40, "Generate Images", LIGHT_BLUE, DARK_BLUE, self.generate_images)
            ]
        }
    
    def switch_to_file(self):
        self.current_screen = "file_input"
        self.filename_input.text = ""
        self.message = ""
    
    def switch_to_console(self):
        self.current_screen = "console_input"
        self.console_mode = "variables"
        self.console_variables = []
        self.console_terminals = []
        self.console_productions = []
        self.console_start = ""
        self.temp_input.text = ""
        self.message = "Enter variables (uppercase letters, one at a time)"
        self.message_color = BLACK
    
    def back_to_main(self):
        self.current_screen = "main"
        self.message = ""
    
    def exit_app(self):
        pygame.quit()
        sys.exit()
    
    def load_from_file(self):
        filename = self.filename_input.text.strip()
        if filename:
            # Try to load the grammar from the file
            if self.cfg.loadFromFile(filename):
                self.grammar_loaded = True
                self.message = "Grammar loaded successfully!"
                self.message_color = GREEN
                self.current_screen = "string_input"
                self.test_string_input.text = ""
            else:
                self.message = "Failed to load grammar."
                self.message_color = RED
        else:
            self.message = "Please enter a filename."
            self.message_color = RED
    
    def submit_console_input(self):
        value = self.temp_input.text.strip()
        
        if self.console_mode == "variables":
            if not value:
                self.console_mode = "terminals"
                self.message = "Enter terminals (lowercase letters or digits, one at a time)"
                self.temp_input.text = ""
            elif value not in self.console_variables:
                if self.cfg.validateVariable(value):
                    self.console_variables.append(value)
                    self.message = f"Added variable: {value}. Enter more or leave empty to continue."
                    self.temp_input.text = ""
                else:
                    self.message = "Invalid variable. Must be a single uppercase letter."
                    self.message_color = RED
            else:
                self.message = "Variable already added. Enter another or leave empty to continue."
                self.message_color = RED
                
        elif self.console_mode == "terminals":
            if not value:
                self.console_mode = "productions"
                self.message = "Enter productions (format: A -> B C | epsilon)"
                self.temp_input.text = ""
            elif value not in self.console_terminals:
                if self.cfg.validateTerminal(value):
                    self.console_terminals.append(value)
                    self.message = f"Added terminal: {value}. Enter more or leave empty to continue."
                    self.temp_input.text = ""
                else:
                    self.message = "Invalid terminal. Must be a single lowercase letter or digit."
                    self.message_color = RED
            else:
                self.message = "Terminal already added. Enter another or leave empty to continue."
                self.message_color = RED
                
        elif self.console_mode == "productions":
            if not value:
                self.console_mode = "start"
                self.message = "Enter start symbol (single uppercase letter)"
                self.temp_input.text = ""
            else:
                parts = value.split('->')
                if len(parts) != 2:
                    self.message = "Invalid production format. Must be A -> B C | epsilon"
                    self.message_color = RED
                else:
                    head = parts[0].strip()
                    if head not in self.console_variables:
                        self.message = f"Head symbol {head} is not in variables."
                        self.message_color = RED
                    else:
                        self.console_productions.append(value)
                        self.message = f"Added production: {value}. Enter more or leave empty to continue."
                        self.message_color = BLACK
                        self.temp_input.text = ""
                
        elif self.console_mode == "start":
            if not value:
                self.message = "Please enter a start symbol."
                self.message_color = RED
            elif value not in self.console_variables:
                self.message = f"Start symbol {value} is not in variables."
                self.message_color = RED
            else:
                self.console_start = value
                
                # Load the grammar
                self.cfg = CFG()
                for var in self.console_variables:
                    self.cfg.addVariable(var)
                for term in self.console_terminals:
                    self.cfg.addTerminal(term)
                for prod in self.console_productions:
                    parts = prod.split('->')
                    head = parts[0].strip()
                    bodies = parts[1].strip().split('|')
                    for body in bodies:
                        bodySymbols = body.strip().split() or ['epsilon']
                        self.cfg.addProduction(head, bodySymbols)
                self.cfg.setStartSymbol(self.console_start)
                
                self.grammar_loaded = True
                self.message = "Grammar loaded successfully!"
                self.message_color = GREEN
                self.current_screen = "string_input"
                self.test_string_input.text = ""
    
    def derive_string(self, strategy):
        test_str = self.test_string_input.text.strip()
        if test_str or test_str == "":  # Allow empty string
            steps = self.cfg.getDerivationSteps(test_str, strategy=strategy, silent=True)
            if steps:
                self.derivation_steps = steps
                self.result_text = [f"{strategy.capitalize()}most derivation of '{test_str}':"]
                for step in steps:
                    self.result_text.append(f"=> {step}")
                self.current_screen = "result"
            else:
                self.message = f"String '{test_str}' is not in the language of this grammar."
                self.message_color = RED
        else:
            self.message = "Please enter a string to derive."
            self.message_color = RED
    
    def generate_parse_tree(self):
        test_str = self.test_string_input.text.strip()
        if test_str or test_str == "":  # Allow empty string
            self.cfg.generateParseTree(test_str)
            self.message = "Parse tree generated and saved as 'parseTree.pdf'."
            self.message_color = GREEN
        else:
            self.message = "Please enter a string to derive."
            self.message_color = RED
    
    def generate_images(self):
        test_str = self.test_string_input.text.strip()
        if test_str or test_str == "":  # Allow empty string
            # Get derivation type from the first result line
            if "Leftmost" in self.result_text[0]:
                strategy = "left"
            else:
                strategy = "right"
                
            self.cfg.generateDerivationImage(test_str, strategy=strategy)
            self.cfg.generateParseTree(test_str)
            self.message = f"Images generated and saved as '{strategy}Derivation.pdf' and 'parseTree.pdf'."
            self.message_color = GREEN
        else:
            self.message = "No string to derive."
            self.message_color = RED
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw title
        title = font_large.render("CFG Parser", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw message
        if self.message:
            msg = font_medium.render(self.message, True, self.message_color)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 120))
        
        # Draw elements based on current screen
        if self.current_screen == "main":
            for button in self.buttons["main"]:
                button.draw(screen)
                
        elif self.current_screen == "file_input":
            prompt = font_medium.render("Enter the filename of your grammar:", True, BLACK)
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 200))
            
            self.filename_input.draw(screen)
            
            for button in self.buttons["file_input"]:
                button.draw(screen)
                
        elif self.current_screen == "console_input":
            # Display current section
            section_text = ""
            if self.console_mode == "variables":
                section_text = "Variables"
            elif self.console_mode == "terminals":
                section_text = "Terminals"
            elif self.console_mode == "productions":
                section_text = "Productions"
            elif self.console_mode == "start":
                section_text = "Start Symbol"
                
            section_render = font_medium.render(f"Enter {section_text}:", True, BLACK)
            screen.blit(section_render, (WIDTH // 2 - section_render.get_width() // 2, 200))
            
            # Draw input box
            self.temp_input.draw(screen)
            
            # Display current values
            y_pos = 150
            if self.console_variables:
                var_text = "Variables: " + ", ".join(self.console_variables)
                var_render = font_small.render(var_text, True, BLACK)
                screen.blit(var_render, (50, y_pos))
                y_pos += 20
                
            if self.console_terminals:
                term_text = "Terminals: " + ", ".join(self.console_terminals)
                term_render = font_small.render(term_text, True, BLACK)
                screen.blit(term_render, (50, y_pos))
                y_pos += 20
                
            if self.console_productions:
                prod_text = "Productions:"
                prod_render = font_small.render(prod_text, True, BLACK)
                screen.blit(prod_render, (50, y_pos))
                for i, prod in enumerate(self.console_productions):
                    if i < 5:  # Limit displayed productions
                        prod_render = font_small.render("  " + prod, True, BLACK)
                        screen.blit(prod_render, (50, y_pos + 20 + i * 20))
                    elif i == 5:
                        more_render = font_small.render(f"  ... {len(self.console_productions) - 5} more", True, BLACK)
                        screen.blit(more_render, (50, y_pos + 20 + 5 * 20))
                        break
                        
            if self.console_start:
                start_text = "Start Symbol: " + self.console_start
                start_render = font_small.render(start_text, True, BLACK)
                screen.blit(start_render, (50, y_pos + 150))
            
            for button in self.buttons["console_input"]:
                button.draw(screen)
                
        elif self.current_screen == "string_input":
            prompt = font_medium.render("Enter a string to derive:", True, BLACK)
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))
            
            self.test_string_input.draw(screen)
            
            for button in self.buttons["string_input"]:
                button.draw(screen)
                
        elif self.current_screen == "result":
            # Display derivation steps
            for i, line in enumerate(self.result_text):
                if i < 12:  # Limit displayed lines
                    line_render = font_medium.render(line, True, BLACK)
                    screen.blit(line_render, (50, 150 + i * 30))
                elif i == 12:
                    more_render = font_medium.render(f"... {len(self.result_text) - 12} more steps", True, BLACK)
                    screen.blit(more_render, (50, 150 + 12 * 30))
                    break
            
            for button in self.buttons["result"]:
                button.draw(screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle button events
                current_buttons = self.buttons.get(self.current_screen, [])
                for button in current_buttons:
                    button.check_hover(mouse_pos)
                    button.handle_event(event)
                
                # Handle text input events
                if self.current_screen == "file_input":
                    self.filename_input.handle_event(event)
                    
                elif self.current_screen == "console_input":
                    self.temp_input.handle_event(event)
                
                elif self.current_screen == "string_input":
                    self.test_string_input.handle_event(event)
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the application
if __name__ == "__main__":
    app = CFGParserGUI()
    app.run() 