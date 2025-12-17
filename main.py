import os
import csv
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from logic import LanguageProcessor

console = Console()

HARDCODED_LANGUAGES = [
    "The set of all strings over {0, 1} that start with 0 and end with 1",
    "The set of strings with an equal number of a's and b's",
    "Strings representing palindromes over {a, b}",
    "Strings containing the substring '101'",
    "The set of strings matching the email format"
]

HARDCODED_TEST_STRINGS = [
    "001", "111", "010", "101", "00001", "aab", "aba", "abc"
]

processor = LanguageProcessor()

def check_api_key():
    if not os.environ.get("GOOGLE_API_KEY"):
        console.print("[bold red]WARNING: GOOGLE_API_KEY environment variable not set![/bold red]")
        console.print("Please set it using: export GOOGLE_API_KEY='your_key'")
        console.print("Or enter it now:")
        key = Prompt.ask("API Key", password=True)
        if key:
            os.environ["GOOGLE_API_KEY"] = key
            # Re-init processor to pick up the key
            global processor
            processor = LanguageProcessor()
        else:
            console.print("[red]Cannot proceed without API Key.[/red]")
            sys.exit(1)

def print_menu():
    console.print("\n[bold cyan]--- Theory of Computation AI Tool ---[/bold cyan]")
    console.print("1. [green]Define Language (Manual)[/green]")
    console.print("2. [green]Select Hardcoded Language[/green]")
    console.print("3. [yellow]Test Single String[/yellow]")
    console.print("4. [yellow]Batch Test (CSV File)[/yellow]")
    console.print("5. [yellow]Batch Test (Hardcoded Samples)[/yellow]")
    console.print("6. [red]Exit[/red]")

def define_language(description):
    with console.status("[bold green]Analyzing Language...[/bold green]"):
        result = processor.set_language(description)
    
    if "error" in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")
        return

    console.print(Panel(f"[bold]Description:[/bold] {description}", title="Language Defined"))
    
    if result.get("is_regular"):
        console.print(f"[bold green]Type:[/bold green] Regular Language")
        console.print(f"[bold blue]Regex:[/bold blue] {result.get('regex')}")
    else:
        console.print(f"[bold yellow]Type:[/bold yellow] Non-Regular Language")
    
    console.print(f"[italic]{result.get('explanation')}[/italic]")

def test_string(string):
    if not processor.current_description:
        console.print("[red]Please define a language first![/red]")
        return

    with console.status(f"Checking '{string}'..."):
        result = processor.process_string(string)

    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    accepted = result.get("accepted")
    reason = result.get("reason")
    
    color = "green" if accepted else "red"
    status = "ACCEPTED" if accepted else "REJECTED"
    
    console.print(f"String: '{string}' -> [{color}]{status}[/{color}]")
    console.print(f"Reason: {reason}")

def batch_test(strings):
    if not processor.current_description:
        console.print("[red]Please define a language first![/red]")
        return

    table = Table(title="Batch Test Results")
    table.add_column("String", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Reason", style="italic")

    with console.status("[bold green]Running Batch Test...[/bold green]"):
        for s in strings:
            s = s.strip()
            if not s: continue
            
            result = processor.process_string(s)
            accepted = result.get("accepted")
            reason = result.get("reason", "")
            
            status_str = "[green]ACCEPTED[/green]" if accepted else "[red]REJECTED[/red]"
            table.add_row(s, status_str, reason)

    console.print(table)

def main():
    check_api_key()
    
    while True:
        print_menu()
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            desc = Prompt.ask("Enter language description")
            define_language(desc)
        
        elif choice == "2":
            console.print("Available Languages:")
            for idx, lang in enumerate(HARDCODED_LANGUAGES, 1):
                console.print(f"{idx}. {lang}")
            
            lang_idx = Prompt.ask("Choose number", choices=[str(i) for i in range(1, len(HARDCODED_LANGUAGES)+1)])
            define_language(HARDCODED_LANGUAGES[int(lang_idx)-1])

        elif choice == "3":
            s = Prompt.ask("Enter string to test")
            test_string(s)

        elif choice == "4":
            filepath = Prompt.ask("Enter CSV filepath", default="test_inputs.csv")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    reader = csv.reader(f)
                    strings = [row[0] for row in reader if row] # Assume single column
                batch_test(strings)
            else:
                console.print("[red]File not found.[/red]")

        elif choice == "5":
             batch_test(HARDCODED_TEST_STRINGS)

        elif choice == "6":
            console.print("[bold]Goodbye![/bold]")
            break

if __name__ == "__main__":
    main()
