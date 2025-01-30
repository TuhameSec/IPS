import argparse
import cv2
from ImageAnalysis import analyze_image
from LiveFeed import analyze_live_feed
from database import connect_to_db
from logging_config import configure_logging
logger = configure_logging()
import os

def analyze_image_command(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error("Invalid image!")
            print("Error: Invalid image!")
            return

        result = analyze_image(image)
        if result:
            name, age, nationality, ip = result
            print(f"Name: {name}\nAge: {age}\nNationality: {nationality}\nNetwork IP: {ip}")
        else:
            print("No information found.")
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print("An error occurred during analysis.")

def start_live_feed():
    try:
        print("Starting live feed analysis...")
        analyze_live_feed()
    except Exception as e:
        logger.error(f"Error during live feed analysis: {e}")
        print("An error occurred during live feed analysis.")

def main():
    parser = argparse.ArgumentParser(description="Military Image Analysis System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image")
    analyze_parser.add_argument("image_path", type=str, help="Path to the image file")

    live_feed_parser = subparsers.add_parser("live-feed", help="Start live feed analysis")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_image_command(args.image_path)
    elif args.command == "live-feed":
        start_live_feed()
    else:
        parser.print_help()

if __name__ == "__main__":
    db = None
    try:
        db = connect_to_db()
        if db:
            main()
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        print("An error occurred during execution.")
    finally:
        if db:
            try:
                db.close()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")