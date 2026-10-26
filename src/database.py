from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///./movie.db', echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
