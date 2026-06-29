"""
OpenRadar — Developer tips loaded-screen style.

Curated tactical hints for builders, sourced from community wisdom.
Each tip = (category, body, optional attribution).
Categories carry their own accent color in the CSS layer.
"""

from typing import List, Tuple

Tip = Tuple[str, str, str]  # (category, body, attribution)


TIPS: List[Tip] = [
    # LINUX / SHELL
    ("LINUX", "Press Ctrl+R and start typing. Reverse-search your entire shell history.", "Bash manual"),
    ("LINUX", "Use 'ls -lah' not 'ls -l'. The 'h' makes sizes human-readable.", "coreutils"),
    ("LINUX", "Pipe 'du -sh' to find what's eating your disk. Pipe nothing to nothing.", "always works"),
    ("LINUX", "Process substitution '<(cmd)' lets diff compare two live outputs. The future is now.", "advanced bash"),
    ("LINUX", "tmux prefix + [ enters copy mode. Pair with prefix + ] to paste. Sessions outlive SSH.", "tmux cheatsheet"),

    # RSI / ERGONOMICS
    ("RSI", "Every 20 min: look at something 20 feet away for 20 s. The 20-20-20 rule.", "ophthalmology"),
    ("RSI", "Lower your keyboard. Most desks are too high. Shoulders relaxed, elbows at 90°.", "physio"),
    ("RSI", "A vertical mouse pays for itself in two weeks. Wrist pronation is a debt.", "ergonomic cheatsheet"),
    ("RSI", "Stand up every 30 min. Not for productivity theatre. For blood.", "orthopedics"),
    ("RSI", "Split keyboards reduce ulnar deviation. Your 50-year-old self sends thanks.", "kinesis ethos"),

    # INFRA / DEVOPS
    ("INFRA", "Health checks must run from the same network as your users. Outside pings are theatre.", "SRE manual"),
    ("INFRA", "Backups that aren't restored are wishes. Drill quarterly.", "SRE"),
    ("INFRA", "Logs are not metrics. Aggregate percentiles. Don't grep for 'error'.", "observability 101"),
    ("INFRA", "'rm -rf' has ended careers. Always -i for the unfamiliar paths.", "post-mortem"),
    ("INFRA", "Feature flags beat feature rollouts. Easier forward, easier back.", "launchdarkly blog"),

    # BEGINNER
    ("BEGINNER", "Read the error twice. The answer is in the last line.", "junior devs"),
    ("BEGINNER", "Google your exact error in quotes. Someone shipped through this before you.", "stackoverflow"),
    ("BEGINNER", "Print debugging is fine. The debugger is fine. Use whatever unblocks you.", "rich harris"),
    ("BEGINNER", "'wip: it works' is a valid commit message. Squash before review.", "git"),
    ("BEGINNER", "Sleep before merging. Tired-you writes bugs rested-you hunts for hours.", "circadian"),

    # EXPERT
    ("EXPERT", "Worse is better. Ship the 80% solution. Perfect is the enemy of shipped.", "pike"),
    ("EXPERT", "Profile before optimising. The hotspot is never where you guessed.", "KDnuggets"),
    ("EXPERT", "Smallest PRs get reviewed fastest. Big PRs rot in the queue.", "google eng"),
    ("EXPERT", "Tests are a forcing function. If it's hard to test, the design is wrong.", "tidy first?"),
    ("EXPERT", "Read code you wrote 5 years ago. The shame and pride both mean you grew.", "confucius, paraphrased"),

    # AI
    ("AI", "AI is a co-pilot, not auto-pilot. You own the architecture; it owns the typing.", "claude"),
    ("AI", "Specificity beats verbosity. 'Reduce EU mobile checkout latency' beats 'make it fast'.", "prompting"),
    ("AI", "LLMs forget every session. Maintain a 'project state' doc and paste it in.", "memory"),
    ("AI", "Don't trust tests you haven't read. The model can be confidently wrong.", "trust"),
    ("AI", "Save successful prompts. You'll reuse 40% of them within a month.", "prompt bible"),

    # JOBS / CAREER
    ("CAREER", "Your network is your net worth. Reply to that DM, even when busy.", "zer0"),
    ("CAREER", "Ask for a 30-min pairing session, not a coffee chat. You learn 10× more.", "interview"),
    ("CAREER", "Write the post you wish existed. Future-you applying will thank past-you.", "builder"),
    ("CAREER", "Track wins weekly. 'Reduced X by 30%' beats 'worked on X'.", "cv"),
    ("CAREER", "Quit gracefully. Career paths intersect more than you'd think.", "networks"),

    # WORKFLOW
    ("WORKFLOW", "Single source of truth beats clever syncing. Compute once.", "naming"),
    ("WORKFLOW", "Delete more than you add. Every line is a future tax.", "rust gospel"),
    ("WORKFLOW", "If you did it 3 times, write a script. The 4th time owes you nothing.", "automate the boring"),
    ("WORKFLOW", "Documentation is a love letter to future-you. Write it tired.", "lean press"),
    ("WORKFLOW", "Commit. Push. Walk away. Tomorrow-you will re-orient in 30 seconds.", "git, gitpush, sleep"),
]


def get_tips() -> List[Tip]:
    """Return the static tips list. Cached at import."""
    return TIPS
