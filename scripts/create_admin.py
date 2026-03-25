"""Bootstrap script — create the initial admin user."""

import asyncio
import sys
from core.database import get_session_factory
from core.repositories import UserRepository
from api.auth.jwt_handler import hash_password


async def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_admin.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        sys.exit(1)

    factory = get_session_factory()
    async with factory() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_username(username)
        if existing:
            print(f"User '{username}' already exists")
            sys.exit(1)

        user = await repo.create_user(
            username=username,
            hashed_password=hash_password(password),
            role="admin",
        )
        await session.commit()
        print(f"Admin user '{username}' created (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())
