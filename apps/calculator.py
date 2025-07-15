#!/usr/bin/env python3
"""
Calculator Application
A simple calculator that can be run through the portal
"""

import math
import sys

def main():
    print("=== Calculator ===")
    print("A simple calculator for the Application Portal")
    print("=" * 40)
    print("Available operations:")
    print("- Basic: +, -, *, /, %, **")
    print("- Functions: sin, cos, tan, sqrt, log, log10")
    print("- Constants: pi, e")
    print("- Type 'help' for more info, 'quit' to exit")
    print("=" * 40)
    
    while True:
        try:
            expression = input("\nEnter expression: ").strip()
            
            if expression.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif expression.lower() == 'help':
                show_help()
                continue
            elif expression.lower() == 'clear':
                print("\n" * 50)
                continue
            elif not expression:
                continue
            
            # Replace common mathematical expressions
            expression = expression.replace('pi', 'math.pi')
            expression = expression.replace('e', 'math.e')
            expression = expression.replace('sin', 'math.sin')
            expression = expression.replace('cos', 'math.cos')
            expression = expression.replace('tan', 'math.tan')
            expression = expression.replace('sqrt', 'math.sqrt')
            expression = expression.replace('log10', 'math.log10')
            expression = expression.replace('log', 'math.log')
            expression = expression.replace('abs', 'abs')
            expression = expression.replace('^', '**')
            
            result = eval(expression)
            print(f"Result: {result}")
            
        except ZeroDivisionError:
            print("Error: Division by zero!")
        except ValueError as e:
            print(f"Error: Invalid value - {e}")
        except SyntaxError:
            print("Error: Invalid expression syntax!")
        except NameError as e:
            print(f"Error: Unknown function or variable - {e}")
        except Exception as e:
            print(f"Error: {e}")

def show_help():
    print("\n=== Calculator Help ===")
    print("Basic Operations:")
    print("  Addition: 2 + 3")
    print("  Subtraction: 5 - 2")
    print("  Multiplication: 4 * 3")
    print("  Division: 10 / 2")
    print("  Modulo: 10 % 3")
    print("  Power: 2 ** 3 or 2 ^ 3")
    print("\nMath Functions:")
    print("  Square root: sqrt(16)")
    print("  Sine: sin(pi/2)")
    print("  Cosine: cos(0)")
    print("  Tangent: tan(pi/4)")
    print("  Natural log: log(e)")
    print("  Base-10 log: log10(100)")
    print("\nConstants:")
    print("  Pi: pi")
    print("  Euler's number: e")
    print("\nCommands:")
    print("  help - Show this help")
    print("  clear - Clear screen")
    print("  quit - Exit calculator")

if __name__ == "__main__":
    main()