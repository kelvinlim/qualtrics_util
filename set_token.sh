#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$SCRIPT_DIR/qualtrics_token"

case "$1" in
    va)
        ln -sf "$SCRIPT_DIR/qualtrics_token_va" "$TARGET"
        echo "Linked qualtrics_token -> qualtrics_token_va"
        ;;
    umn)
        ln -sf "$SCRIPT_DIR/qualtrics_token_umn" "$TARGET"
        echo "Linked qualtrics_token -> qualtrics_token_umn"
        ;;
    *)
        echo "Usage: $0 {va|umn}"
        echo "  va   - use the VA token"
        echo "  umn  - use the UMN token"
        ;;
esac
