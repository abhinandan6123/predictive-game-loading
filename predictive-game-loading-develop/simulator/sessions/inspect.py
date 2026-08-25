from simulator.sessions.generator import generate_sessions


def main() -> None:
    sessions = generate_sessions(
        count=10,
        seed=42,
    )

    for session in sessions:
        games = [event.game_id for event in session.events]

        print(f"{session.session_id}: {' -> '.join(games)}")


if __name__ == "__main__":
    main()
