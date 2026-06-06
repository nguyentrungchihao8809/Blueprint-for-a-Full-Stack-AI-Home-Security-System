from pytubefix import YouTube

url = "https://youtu.be/rPDcLx7aebE"
yt = YouTube(url)

print(f"🎬 Đang tải video: {yt.title}")
# Lấy định dạng có cả âm thanh và hình ảnh, độ phân giải cao nhất
stream = yt.streams.get_highest_resolution()
stream.download(output_path="D:/Projects/YOLO-Nhung", filename="trom_cho.mp4")

print("✅ Tải xong! File đã nằm trong thư mục dự án của Hào.")