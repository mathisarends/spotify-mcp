import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv(override=True)


async def interactive_session():
    async with MCPServerStdio(
        name="Spotify Server",
        params={
            "command": "uv",
            "args": ["run", "spotify-mcp"],
        },
    ) as spotify_server:
        agent = Agent(
            name="Spotify DJ",
            instructions="""
            Du bist ein professioneller DJ Assistant.
            - Spiele Musik basierend auf Stimmung und Genre
            - Verwalte Playlists intelligent
            - Passe Lautstärke basierend auf Kontext an
            """,
            mcp_servers=[spotify_server],
        )

        print("🎵 Spotify DJ gestartet!")
        print("Schreib 'exit' zum Beenden\n")

        while True:
            user_input = input("Du: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            if not user_input:
                continue

            # Run the agent
            result = await Runner.run(agent, user_input)
            print(f"🤖 Assistant: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(interactive_session())
