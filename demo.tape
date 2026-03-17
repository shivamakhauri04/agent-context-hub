# VHS demo tape for agent-context-hub
# Run with: vhs demo.tape

Output assets/demo.gif

Set Shell "bash"
Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20

# Activate venv
Hide
Type "source .venv/bin/activate && clear"
Enter
Sleep 500ms
Show

# 1. List all trading docs
Type "# List all 27 trading domain documents"
Enter
Sleep 1s
Type "achub list --domain trading"
Enter
Sleep 5s

# 2. Search for wash sale rules
Type "# Search for wash sale and tax loss harvesting rules"
Enter
Sleep 1s
Type 'achub search "wash sale tax loss" --domain trading'
Enter
Sleep 5s

# 3. Compliance check with the comprehensive portfolio
Type "# Run compliance checks against a portfolio"
Enter
Sleep 1s
Type "achub check --domain trading --rules pdt,wash-sale,gfv,short-selling,zero-dte,recurring --portfolio examples/sample_comprehensive_portfolio.json"
Enter
Sleep 10s

# 4. Get a doc in LLM-optimized format
Type "# Get a document in LLM-optimized format"
Enter
Sleep 1s
Type "achub get trading/regulations/good-faith-violations/rules --format llm | head -40"
Enter
Sleep 5s

Sleep 3s
