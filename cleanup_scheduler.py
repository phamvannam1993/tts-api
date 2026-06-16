import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_DIR = "audio_cache"


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

    try:
        for filename in os.listdir(AUDIO_DIR):
            filepath = os.path.join(AUDIO_DIR, filename)

            if os.path.isfile(filepath):
                file_age_hours = (current_time - os.path.getmtime(filepath)) / 3600

                if file_age_hours > max_age_hours:
                    try:
                        file_size = os.path.getsize(filepath)
                        total_size += file_size
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(
                            f"🗑️  Đã xóa: {filename} "
                            f"(tuổi: {file_age_hours:.1f}h, dung lượng: {file_size/1024:.1f}KB)"
                        )
                    except Exception as e:
                        logger.error(f"❌ Lỗi xóa {filename}: {str(e)}")

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
