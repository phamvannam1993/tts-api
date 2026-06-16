import os
import time
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_DIR = "audio_cache"
CACHE_FILE = os.path.join(AUDIO_DIR, "cache.json")


def cleanup_cache(deleted_files):
    """Remove cache entries for deleted files"""
    try:
        if not os.path.exists(CACHE_FILE):
            return

        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)

        # Remove cache entries for deleted files
        for filename in deleted_files:
            for key, cached_file in list(cache_data.items()):
                if cached_file == filename:
                    del cache_data[key]
                    logger.info(f"🗑️  Cache entry removed: {key}")

        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        logger.error(f"❌ Lỗi cleanup cache: {e}")


def cleanup_old_audio_files(max_age_hours=1):
    """
    Xóa files cũ hơn max_age_hours từ audio_cache directory
    """
    if not os.path.exists(AUDIO_DIR):
        logger.info(f"📁 {AUDIO_DIR} không tồn tại")
        return

    current_time = time.time()
    deleted_count = 0
    total_size = 0
    deleted_files = []

    try:
        for filename in os.listdir(AUDIO_DIR):
            filepath = os.path.join(AUDIO_DIR, filename)

            # Skip cache.json file
            if filename == "cache.json":
                continue

            if os.path.isfile(filepath):
                file_age_hours = (current_time - os.path.getmtime(filepath)) / 3600

                if file_age_hours > max_age_hours:
                    try:
                        file_size = os.path.getsize(filepath)
                        total_size += file_size
                        os.remove(filepath)
                        deleted_count += 1
                        deleted_files.append(filename)
                        logger.info(
                            f"🗑️  Đã xóa: {filename} "
                            f"(tuổi: {file_age_hours:.1f}h, dung lượng: {file_size/1024:.1f}KB)"
                        )
                    except Exception as e:
                        logger.error(f"❌ Lỗi xóa {filename}: {str(e)}")

        # Clean up cache entries for deleted files
        if deleted_files:
            cleanup_cache(deleted_files)

        logger.info(
            f"✅ Cleanup hoàn tất: {deleted_count} files xóa, "
            f"tổng dung lượng giải phóng: {total_size/1024/1024:.2f}MB"
        )
    except Exception as e:
        logger.error(f"❌ Lỗi cleanup: {str(e)}")


def start_cleanup_scheduler(interval_minutes=60):
    """
    Khởi động scheduler để tự động xóa audio_cache mỗi interval_minutes
    """
    scheduler = BackgroundScheduler()

    # Thêm job cleanup chạy mỗi X phút
    scheduler.add_job(
        cleanup_old_audio_files,
        "interval",
        minutes=interval_minutes,
        args=[1],  # xóa files cũ hơn 1 giờ
        id="audio_cleanup_job",
        name="Audio Cleanup Job",
    )

    try:
        scheduler.start()
        logger.info(
            f"✅ Cleanup Scheduler khởi động: chạy mỗi {interval_minutes} phút"
        )
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động scheduler: {str(e)}")

    return scheduler
