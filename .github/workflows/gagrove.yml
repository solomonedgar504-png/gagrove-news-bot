name: Gagrove - 3 Daily Malawi News Posts

on:
  schedule:
    - cron: "0 5 * * *"
    - cron: "0 10 * * *"
    - cron: "0 15 * * *"
  workflow_dispatch:
    inputs:
      topic:
        description: "Optional topic. Blank = Malawi current breaking news."
        required: false
        default: ""

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - name: Publish Gagrove post
        env:
          META_PAGE_ID: ${{ secrets.META_PAGE_ID }}
          META_PAGE_ACCESS_TOKEN: ${{ secrets.META_PAGE_ACCESS_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GAGROVE_TOPIC: ${{ inputs.topic }}
        run: python gagrove.py
