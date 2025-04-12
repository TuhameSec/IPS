"""Main entry point for the Military Image Analysis System."""
import argparse
import cv2
import os
import getpass
from dotenv import load_dotenv
from image_processor import analyze_image
from live_feed import analyze_live_feed
from database_manager import connect_to_db
from audit_log import log_audit
from logging_config import configure_logging
from tqdm import tqdm
from typing import List

logger = configure_logging()
load_dotenv()

def analyze_image_command(image_path: str, user_id: str, offline_mode: bool) -> None:
    """Analyze a single image for face identification.

    Args:
        image_path: Path to the image file.
        user_id: Identifier of the user.
        offline_mode: Whether to use offline database.
    """
    if not os.path.exists(image_path):
        logger.error("Image path does not exist")
        print("Error: Image path does not exist")
        return

    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error("Invalid image")
            print("Error: Invalid image")
            return

        log_audit("analyze_image", user_id, f"Analyzing {image_path}, offline={offline_mode}")
        with tqdm(total=100, desc="Analyzing image") as pbar:
            results = analyze_image(image, progress_callback=lambda x: pbar.update(x), offline_mode=offline_mode)
        if results:
            for name, age, nationality, crime, danger_level in results:
                print(f"Name: {name}\nAge: {age}\nNationality: {nationality}\nCrime: {crime}\nDanger Level: {danger_level}")
        else:
            print("No information found.")
        log_audit("analyze_image_complete", user_id, f"Results: {len(results) if results else 0} matches")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        print(f"Error: {str(e)}")
        log_audit("analyze_image_error", user_id, str(e))

def start_live_feed(cameras: List[int], user_id: str, offline_mode: bool) -> None:
    """Start live feed analysis for face identification.

    Args:
        cameras: List of camera indices.
        user_id: Identifier of the user.
        offline_mode: Whether to use offline database.
    """
    try:
        log_audit("start_live_feed", user_id, f"Cameras: {cameras}, offline={offline_mode}")
        print("Starting live feed (press 'q' to quit)...")
        analyze_live_feed(cameras, offline_mode)
        log_audit("live_feed_stopped", user_id, "Live feed terminated")
    except Exception as e:
        logger.error(f"Live feed error: {e}")
        print(f"Error: {str(e)}")
        log_audit("live_feed_error", user_id, str(e))

def main() -> None:
    """Parse command-line arguments and run the system."""
    parser = argparse.ArgumentParser(description="Military Image Analysis System")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image")
    analyze_parser.add_argument("image_path", type=str, help="Path to the image file")

    live_feed_parser = subparsers.add_parser("live-feed", help="Start live feed analysis")
    live_feed_parser.add_argument("--cameras", type=int, nargs="+", default=[0], help="Camera indices")

    args = parser.parse_args()
    user_id = getpass.getuser()
    offline_mode = args.offline

    db = None
    try:
        if not offline_mode:
            db = connect_to_db()
            if not db:
                logger.warning("Falling back to offline mode")
                offline_mode = True

        if args.command == "analyze":
            analyze_image_command(args.image_path, user_id, offline_mode)
        elif args.command == "live-feed":
            start_live_feed(args.cameras, user_id, offline_mode)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Execution error: {e}")
        print(f"Error: {str(e)}")
        log_audit("main_error", user_id, str(e))
    finally:
        if db:
            try:
                db.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database: {e}")

if __name__ == "__main__":
    main()