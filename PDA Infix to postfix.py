import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple
from graphviz import Digraph
import subprocess

class PDA:
    def __init__(self):
        self.states = set()
        self.stack_alphabet = set()
        self.transition_function = {}
        self.start_state = None
        self.start_stack_symbol = None
        self.final_states = set()
        self.stack: List[str] = []  # Initialize with an empty stack

    def set_pda_tuples(self, states, stack_alphabet, transition_function, start_state, start_stack_symbol, final_states):
        self.states = set(states)
        self.stack_alphabet = set(stack_alphabet)
        self.transition_function = transition_function
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.final_states = set(final_states)

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            raise IndexError("pop from an empty stack")

    def peek(self):
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0
    
    def visualize_pda(self):
        dot = Digraph(comment='PDA')

        # Add states
        for state in self.states:
            dot.node(state, shape='circle', color='blue' if state in self.final_states else 'black')

        # Add transitions
        for transition, target in self.transition_function.items():
            start_state, char, stack_symbol = transition
            end_state, *stack_symbols = target

            label = f'{char}, {stack_symbol} -> {",".join(stack_symbols)}'

            dot.edge(start_state, end_state, label=label)

        # Save the image to a file (e.g., pda_graph.png)
        dot.render('pda_graph', format='png', cleanup=True)

def infix_to_postfix(infix_expression: str, pda: PDA) -> Tuple[str, List[str]]:
    output = []
    steps = []

    pda.push(pda.start_stack_symbol)  # Initialize the stack with the start stack symbol
    current_state = pda.start_state

    for char in infix_expression:
        if char.isalnum():
            output.append(char)
            steps.append(f"Push({char})")
        elif char == '(':
            pda.push(char)
            steps.append(f"Push({char})")
        elif char in {'+', '-', '*', '/', '^'}:
            pda.push(char)
            steps.append(f"Push({char})")
        elif char == ')':
            while not pda.is_empty() and pda.peek() != '(':
                output.append(pda.pop())
                steps.append("Pop()")
            pda.pop()  # Pop the '('
            steps.append("Pop()")
        else:
            steps.append("Invalid input encountered. Going to dead state.")
            pda.set_pda_tuples(states=['q_dead'], stack_alphabet=set(), transition_function={}, 
                               start_state='q_dead', start_stack_symbol='', final_states={'q_dead'})

    while not pda.is_empty():
        popped_item = pda.pop()
        if popped_item != pda.start_stack_symbol:
            output.append(popped_item)
            steps.append("Pop()")

    return ''.join(output), steps

def generate_pda_from_equation():
    # Define the PDA tuples for infix to postfix conversion
    states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q_dead'}
    stack_alphabet = {'no', '(', ')', '+', '-', '*', '/', '^'}
    transition_function = {
        ('q0', 'no', 'Z0'): ('q1', 'Z0'),
        ('q0', '(', 'Z0'): ('q3', 'Z0'),
        ('q0', '+', 'Z0'): ('q_dead', ''),
        ('q0', '-', 'Z0'): ('q_dead', ''),
        ('q0', '*', 'Z0'): ('q_dead', ''),
        ('q0', '/', 'Z0'): ('q_dead', ''),
        ('q0', '^', 'Z0'): ('q_dead', ''),
        ('q1', 'no', 'Z0'): ('q1', 'Z0'),
        ('q1', ')', 'no'): ('q1', 'λ'),
        ('q1', '+', 'no'): ('q2', 'Z0'),
        ('q1', '-', 'no'): ('q2', 'Z0'),
        ('q1', '*', 'no'): ('q2', 'Z0'),
        ('q1', '/', 'no'): ('q2', 'Z0'),
        ('q1', '^', 'no'): ('q2', 'Z0'),
        ('q1', '(', 'no'): ('q_dead', ''),
        ('q1', '', 'Z0'): ('q4', ''),
        ('q2', 'no', '+'): ('q1', 'λ'),
        ('q2', 'no', '-'): ('q1', 'λ'),
        ('q2', 'no', '*'): ('q1', 'λ'),
        ('q2', 'no', '/'): ('q1', 'λ'),
        ('q2', 'no', '^'): ('q1', 'λ'),
        ('q2', '(', '+'): ('q1', 'Z0'),
        ('q2', '(', '-'): ('q1', 'Z0'),
        ('q2', '(', '*'): ('q1', 'Z0'),
        ('q2', '(', '/'): ('q1', 'Z0'),
        ('q2', '(', '^'): ('q1', 'Z0'),
        ('q2', '+', 'Z0'): ('q_dead', 'λ'),
        ('q2', '-', 'Z0'): ('q_dead', 'λ'),
        ('q2', '*', 'Z0'): ('q_dead', 'λ'),
        ('q2', '/', 'Z0'): ('q_dead', 'λ'),
        ('q2', '^', 'Z0'): ('q_dead', 'λ'),
          # Accept state
        ('q3', 'no', 'Z0'): ('q1', 'Z0'),
        ('q3', '(', 'Z0'): ('q3', 'Z0'),
        ('q3', '+', 'Z0'): ('q_dead', ''),
        ('q3', '-', 'Z0'): ('q_dead', ''),
        ('q3', ')', 'Z0'): ('q_dead', ''),
        ('q3', '*', 'Z0'): ('q_dead', ''),
        ('q3', '/', 'Z0'): ('q_dead', ''),
        ('q3', '^', 'Z0'): ('q_dead', ''),
        ('q4', '', 'Z0'): ('q4', 'λ'),  # Stay in the accept state
        ('q_dead', '', 'Z0'): ('q_dead', 'λ'),  # Stay in the dead state
    }
    start_state = 'q0'
    start_stack_symbol = 'Z0'
    final_states = {'q4'}

    pda = PDA()
    pda.set_pda_tuples(states, stack_alphabet, transition_function, start_state, start_stack_symbol, final_states)

    return pda

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDA Visualizer")

        self.label_equation = tk.Label(root, text="Enter Equation/Expression:")
        self.label_equation.pack()

        self.entry_equation = tk.Entry(root)
        self.entry_equation.pack()

        self.convert_button = tk.Button(root, text="Convert", command=self.convert_equation)
        self.convert_button.pack()

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

    def convert_equation(self):
        equation = self.entry_equation.get()

        # Generate PDA based on the equation
        pda = generate_pda_from_equation()

        # Visualize the PDA
        pda.visualize_pda()

        # Convert infix expression to postfix using the created PDA
        postfix_expression, steps = infix_to_postfix(equation, pda)

        result_text = f"Equation/Expression: {equation}\nPostfix Expression: {postfix_expression}\n\nSteps:\n"
    
        for step in steps:
            result_text += step + "\n"

        self.result_label.config(text=result_text)
        messagebox.showinfo("Result", result_text)
        # Open the image file
        image_file = 'pda_graph.png'
        subprocess.Popen(['start', image_file], shell=True)  # Windows

if __name__ == "__main__":
    main_root = tk.Tk()
    main_root.geometry("400x300")  # Set the initial size of the window
    app = App(main_root)
    main_root.mainloop()
