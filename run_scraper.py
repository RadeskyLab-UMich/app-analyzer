import asyncio
from youtube_scraper import YoutubeScraper

async def main():
    scraper = YoutubeScraper()

    video_ids = ['dQw4w9WgXcQ', 'ZZ5LpwO-An4', 'J---aiyznGQ']
    video_df = await scraper.video_metadata(video_ids)

    print(video_df)

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())