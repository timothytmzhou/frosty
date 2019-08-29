from concurrent.futures import ThreadPoolExecutor

async def wrap_sync(loop, func, *args):
    # Can set executor to None if a default has been set for loop
    return await loop.run_in_executor(ThreadPoolExecutor(), func, *args)
