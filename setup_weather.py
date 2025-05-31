#!/usr/bin/env python3
"""
Weather API Setup Script
Helps users set up the weatherstack API key for the voice assistant.
"""

import os
import shutil
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold cyan]Weather API Setup[/bold cyan]\n"
        "This script will help you configure the weatherstack API for weather functionality.",
        border_style="cyan"
    ))
    
    # Check if .env.example exists
    if not os.path.exists('.env.example'):
        console.print("[red]Error: .env.example file not found![/red]")
        return
    
    # Check if .env already exists
    if os.path.exists('.env'):
        console.print("[yellow]Warning: .env file already exists![/yellow]")
        overwrite = console.input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            console.print("[green]Setup cancelled.[/green]")
            return
    
    # Copy .env.example to .env
    try:
        shutil.copy2('.env.example', '.env')
        console.print("[green]✓ Created .env file from template[/green]")
    except Exception as e:
        console.print(f"[red]Error creating .env file: {e}[/red]")
        return
    
    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Get your free API key from: [link]https://weatherstack.com/signup[/link]")
    console.print("2. Edit the .env file and replace 'your_weatherstack_api_key_here' with your actual API key")
    console.print("3. Install dependencies: [code]pip install -r requirements.txt[/code]")
    console.print("4. Test the weather functionality by asking: 'What's the weather like?'")
    
    console.print(f"\n[dim]The .env file has been created at: {os.path.abspath('.env')}[/dim]")
    console.print("[dim].env files are automatically excluded from git to keep your API key secure.[/dim]")

if __name__ == "__main__":
    main() 