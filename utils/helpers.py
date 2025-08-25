"""
Helper utilities for the AutoGen Education Service
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import colorama

# Initialize colorama for Windows compatibility
colorama.init()

# Rich console for pretty printing
console = Console()

def setup_logging(log_file: str = "education_service.log", level: int = logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def print_chat_message(agent_name: str, content: str, timestamp: Optional[datetime] = None):
    """Pretty print a chat message"""
    if timestamp is None:
        timestamp = datetime.now()
    
    # Color coding for different agents
    colors = {
        "Math_Expert": "blue",
        "Physics_Expert": "green",
        "Chemistry_Expert": "yellow",
        "Biology_Expert": "cyan",
        "CS_Expert": "magenta",
        "Literature_Expert": "red",
        "English_Expert": "bright_blue",
        "Info_Agent": "bright_green",
        "User": "white",
        "Manager": "bright_yellow"
    }
    
    color = colors.get(agent_name, "white")
    
    # Create panel for message
    panel = Panel(
        content,
        title=f"[{color}]{agent_name}[/{color}]",
        subtitle=f"[dim]{timestamp.strftime('%H:%M:%S')}[/dim]",
        border_style=color
    )
    
    console.print(panel)

def print_conversation_summary(summary: Dict[str, Any]):
    """Print conversation summary in a table"""
    table = Table(title="Conversation Summary")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Turns", str(summary.get("total_turns", 0)))
    table.add_row("Questions Asked", str(summary.get("questions_count", 0)))
    table.add_row("Answers Provided", str(summary.get("answers_count", 0)))
    table.add_row("Topics Discussed", ", ".join(summary.get("topics_discussed", [])))
    
    console.print(table)
    
    # Agent contributions
    if "agent_contributions" in summary:
        contrib_table = Table(title="Agent Contributions")
        contrib_table.add_column("Agent", style="cyan")
        contrib_table.add_column("Messages", style="yellow")
        contrib_table.add_column("Participation %", style="green")
        
        participation = summary.get("participation_rate", {})
        for agent, count in summary["agent_contributions"].items():
            rate = participation.get(agent, 0)
            contrib_table.add_row(agent, str(count), f"{rate}%")
        
        console.print(contrib_table)

def format_code(code: str, language: str = "python"):
    """Format code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    return syntax

def save_conversation(messages: List[Dict[str, Any]], filename: str = None):
    """Save conversation to a file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
    
    filepath = Path("conversations") / filename
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False, default=str)
    
    console.print(f"[green]Conversation saved to {filepath}[/green]")
    return filepath

def load_conversation(filename: str) -> List[Dict[str, Any]]:
    """Load conversation from a file"""
    filepath = Path("conversations") / filename
    
    if not filepath.exists():
        console.print(f"[red]File {filepath} not found[/red]")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    console.print(f"[green]Loaded {len(messages)} messages from {filepath}[/green]")
    return messages

def validate_api_keys(settings) -> bool:
    """Validate that required API keys are configured"""
    valid = True
    
    if not settings.openai_api_key and not settings.azure_openai_api_key:
        console.print("[red]❌ No API keys configured. Please set OPENAI_API_KEY or AZURE_OPENAI_API_KEY[/red]")
        valid = False
    
    if settings.openai_api_key:
        if settings.openai_api_key.startswith("your_"):
            console.print("[yellow]⚠️  OpenAI API key appears to be a placeholder[/yellow]")
            valid = False
        else:
            console.print("[green]✓ OpenAI API key configured[/green]")
    
    if settings.azure_openai_api_key:
        if settings.azure_openai_api_key.startswith("your_"):
            console.print("[yellow]⚠️  Azure OpenAI API key appears to be a placeholder[/yellow]")
            valid = False
        else:
            console.print("[green]✓ Azure OpenAI API key configured[/green]")
    
    return valid

def print_welcome_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🎓 AutoGen Education Multi-Agent Service 🎓          ║
    ║                                                           ║
    ║     Powered by Microsoft AutoGen Framework               ║
    ║     Subject Experts Available:                           ║
    ║     • Mathematics • Physics • Chemistry • Biology        ║
    ║     • Computer Science • Literature • English            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def format_quiz_question(question: Dict[str, Any]) -> str:
    """Format a quiz question for display"""
    formatted = f"**Question:** {question.get('question', 'N/A')}\n\n"
    
    if "options" in question:
        formatted += "**Options:**\n"
        for i, option in enumerate(question["options"], 1):
            formatted += f"  {i}. {option}\n"
    
    return formatted

def format_quiz_answer(question: Dict[str, Any], show_explanation: bool = True) -> str:
    """Format quiz answer with explanation"""
    formatted = ""
    
    if "correct_answer" in question:
        if isinstance(question["correct_answer"], int) and "options" in question:
            formatted += f"**Correct Answer:** {question['options'][question['correct_answer']]}\n"
        else:
            formatted += f"**Correct Answer:** {question['correct_answer']}\n"
    
    if show_explanation and "explanation" in question:
        formatted += f"\n**Explanation:** {question['explanation']}\n"
    
    return formatted

def clean_message_content(content: str) -> str:
    """Clean message content for display"""
    # Remove excessive whitespace
    lines = content.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)