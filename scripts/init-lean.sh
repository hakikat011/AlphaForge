#!/bin/bash
# Initialize LEAN CLI with provided credentials
if [ -n "$QC_USER_ID" ] && [ -n "$QC_API_TOKEN" ]; then
    # Configure LEAN CLI
    lean config set user-id "$QC_USER_ID"
    lean config set api-token "$QC_API_TOKEN"
    echo "LEAN CLI configured successfully"
else
    echo "Warning: QC_USER_ID or QC_API_TOKEN not set"
    exit 1
fi 