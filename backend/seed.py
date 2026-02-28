import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.github_sync import run_full_sync


async def main():
    print("Starting initial GitHub sync...")
    print("This will fetch repos from GitHub and populate your database.")
    print("This may take a few minutes depending on rate limits.\n")

    await run_full_sync(max_repos=500)

    print("\nSync complete! Refresh localhost:3000/explore to see data.")


if __name__ == "__main__":
    asyncio.run(main())
