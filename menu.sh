#!/bin/bash

# =========================
# COLORS
# =========================
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

# =========================
# BANNER
# =========================
banner() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "  ██████  ██    ██  █████  ██      ███    ███ ██ ███    ██ ██████  "
    echo "  ██   ██ ██    ██ ██   ██ ██      ████  ████ ██ ████   ██ ██   ██ "
    echo "  ██   ██ ██    ██ ███████ ██      ██ ████ ██ ██ ██ ██  ██ ██   ██ "
    echo "  ██   ██ ██    ██ ██   ██ ██      ██  ██  ██ ██ ██  ██ ██ ██   ██ "
    echo "  ██████   ██████  ██   ██ ███████ ██      ██ ██ ██   ████ ██████  "
    echo -e "${RESET}"
    echo -e "${YELLOW}${BOLD}            DualMindDiff AI - by 3MPER0RR${RESET}"
    echo -e "${CYAN}     Compare reasoning across AI models | Function Calling${RESET}"
    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo ""
}

# =========================
# MENU PRINCIPALE
# =========================
main_menu() {
    banner
    echo -e "  ${BOLD}[1]${RESET}  ${GREEN}DualMindDiff AI${RESET}     — Compare two models on a document"
    echo -e "  ${BOLD}[2]${RESET}  ${GREEN}Function Calling${RESET}     — AI agent with tools (CVE search, file read...)"
    echo -e "  ${BOLD}[3]${RESET}  ${YELLOW}Exit${RESET}"
    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo -ne "\n  ${BOLD}Select option:${RESET} "
    read choice

    case $choice in
        1) menu_dualmind ;;
        2) menu_fc ;;
        3) echo -e "\n${CYAN}Bye.${RESET}\n" ; exit 0 ;;
        *) echo -e "\n${RED}Invalid option${RESET}" ; sleep 1 ; main_menu ;;
    esac
}

# =========================
# MENU DUALMINDIFF
# =========================
menu_dualmind() {
    banner
    echo -e "  ${BOLD}${GREEN}DualMindDiff AI${RESET}\n"
    echo -e "  ${CYAN}Safe Engine${RESET}  → first model (analyzes with filter)"
    echo -e "  ${CYAN}Raw Engine${RESET}   → second model (raw analysis)"
    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"

    echo -ne "\n  ${BOLD}Prompt${RESET} (default: analyze the document): "
    read prompt
    if [ -z "$prompt" ]; then
        prompt="Analyze the content in the document."
    fi

    echo -ne "  ${BOLD}File path${RESET} (default: data/sample.txt): "
    read filepath
    if [ -z "$filepath" ]; then
        filepath="data/sample.txt"
    fi

    echo ""
    echo -e "  ${BOLD}Safe Engine provider:${RESET}"
    echo -e "  [1] ollama-cloud"
    echo -e "  [2] google"
    echo -e "  [3] groq"
    echo -e "  [4] dummy (test)"
    echo -ne "\n  Select: "
    read safe_choice

    case $safe_choice in
        1) safe_mode="ollama-cloud" ; safe_model="gemma4:31b-cloud" ;;
        2) safe_mode="google"       ; safe_model="gemini-2.5-flash" ;;
        3) safe_mode="groq"         ; safe_model="llama-3.3-70b-versatile" ;;
        4) safe_mode="dummy"        ; safe_model="" ;;
        *) safe_mode="dummy"        ; safe_model="" ;;
    esac

    echo ""
    echo -e "  ${BOLD}Raw Engine provider:${RESET}"
    echo -e "  [1] google"
    echo -e "  [2] ollama-cloud"
    echo -e "  [3] groq"
    echo -e "  [4] dummy (test)"
    echo -ne "\n  Select: "
    read raw_choice

    case $raw_choice in
        1) raw_mode="google"       ; raw_model="gemini-2.5-flash" ;;
        2) raw_mode="ollama-cloud" ; raw_model="gemma4:31b-cloud" ;;
        3) raw_mode="groq"         ; raw_model="llama-3.3-70b-versatile" ;;
        4) raw_mode="dummy"        ; raw_model="" ;;
        *) raw_mode="dummy"        ; raw_model="" ;;
    esac

    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo -e "  ${CYAN}Safe${RESET}  : $safe_mode / $safe_model"
    echo -e "  ${CYAN}Raw${RESET}   : $raw_mode / $raw_model"
    echo -e "  ${CYAN}File${RESET}  : $filepath"
    echo -e "  ${CYAN}Prompt${RESET}: $prompt"
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo -ne "\n  ${BOLD}Launch? [y/n]:${RESET} "
    read confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo ""
        python3 main.py \
            --prompt "$prompt" \
            --file "$filepath" \
            --safe-mode "$safe_mode" \
            --safe-model "$safe_model" \
            --raw-mode "$raw_mode" \
            --raw-model "$raw_model"
    fi

    echo ""
    echo -ne "  ${BOLD}Back to menu? [y/n]:${RESET} "
    read back
    if [ "$back" = "y" ] || [ "$back" = "Y" ]; then
        main_menu
    fi
}

# =========================
# MENU FUNCTION CALLING
# =========================
menu_fc() {
    banner
    echo -e "  ${BOLD}${GREEN}Function Calling Module${RESET}\n"
    echo -e "  ${CYAN}Tools available:${RESET}"
    echo -e "  • read_file    — reads a file from disk"
    echo -e "  • save_report  — saves output to file"
    echo -e "  • list_files   — lists files in a directory"
    echo -e "  • search_cve   — searches NVD for CVE details"
    echo -e "  • run_command  — runs safe shell commands"
    echo -e "  • fetch_url    — fetches content from a URL"
    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"

    echo ""
    echo -e "  ${BOLD}Provider:${RESET}"
    echo -e "  [1] Google Gemini"
    echo -e "  [2] Groq"
    echo -e "  [3] OpenRouter"
    echo -ne "\n  Select: "
    read prov_choice

    case $prov_choice in
        1) provider="google" ;;
        2) provider="groq" ;;
        3) provider="openrouter" ;;
        *) provider="google" ;;
    esac

    echo -ne "\n  ${BOLD}Prompt${RESET}: "
    read fc_prompt
    if [ -z "$fc_prompt" ]; then
        fc_prompt="Read data/sample.txt and analyze it from a security perspective"
    fi

    echo -ne "  ${BOLD}Disable logging? [y/n]${RESET} (default: n): "
    read nolog
    nolog_flag=""
    if [ "$nolog" = "y" ] || [ "$nolog" = "Y" ]; then
        nolog_flag="--no-log"
    fi

    echo ""
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo -e "  ${CYAN}Provider${RESET}: $provider"
    echo -e "  ${CYAN}Prompt${RESET}  : $fc_prompt"
    echo -e "${YELLOW}─────────────────────────────────────────────────────────${RESET}"
    echo -ne "\n  ${BOLD}Launch? [y/n]:${RESET} "
    read confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo ""
        python3 fc_module.py \
            --provider "$provider" \
            --prompt "$fc_prompt" \
            $nolog_flag
    fi

    echo ""
    echo -ne "  ${BOLD}Back to menu? [y/n]:${RESET} "
    read back
    if [ "$back" = "y" ] || [ "$back" = "Y" ]; then
        main_menu
    fi
}

# =========================
# ENTRY
# =========================
main_menu
