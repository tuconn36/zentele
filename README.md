# Bot Telegram 5G MATTER

Mã nguồn nằm trong `src/`: `api/` xử lý webhook, `bot/` khởi chạy và xử lý tin nhắn, `ui/` chứa nội dung và giao diện, còn `services/` chứa các chức năng hỗ trợ. Cấu hình chung nằm trong `src/config.py`; dữ liệu icon và ảnh nằm trong `assets/`. Vercel dùng điểm vào `src/api/index.py` được khai báo trong `pyproject.toml`, còn `bot.py` ở thư mục gốc dùng để chạy bot trên máy cục bộ.

## Triển khai lên Vercel

Bot dùng webhook trên Vercel; không chạy `bot.py` hoặc polling đồng thời với webhook. Nếu GitHub Actions hoặc máy khác đang chạy bot bằng cùng token, hãy dừng nó trước khi đăng ký webhook.

1. Tạo dự án Vercel từ mã nguồn này. Có thể dùng Vercel CLI (`npx vercel` trong thư mục dự án) nếu không muốn kết nối GitHub.
2. Trong phần Environment Variables của dự án, thêm:
   - `BOT_TOKEN`: token của bot từ BotFather.
   - `TELEGRAM_WEBHOOK_SECRET`: một chuỗi bí mật tự chọn, dài 1–256 ký tự, chỉ gồm chữ cái tiếng Anh, số, `_` hoặc `-`.
   - `ADMIN_IDS` (không bắt buộc): ID Telegram của quản trị viên, cách nhau bằng dấu phẩy.
3. Triển khai lên production, ví dụ bằng `npx vercel --prod`. Sau khi đổi biến môi trường, triển khai lại để áp dụng. Ghi lại tên miền production, ví dụ `https://ten-du-an.vercel.app`.
4. Bảo đảm URL `/webhook` có thể nhận yêu cầu công khai từ Telegram; nếu bật Deployment Protection, cần cấu hình để Telegram truy cập được webhook.
5. Đăng ký webhook **sau khi triển khai**. Trên PowerShell, chạy các lệnh dưới đây, nhập token và secret tương ứng khi được hỏi, và thay URL bằng tên miền production thật:

   ```powershell
   $botToken = Read-Host 'BOT_TOKEN'
   $webhookSecret = Read-Host 'TELEGRAM_WEBHOOK_SECRET'
   $webhookUrl = 'https://ten-du-an.vercel.app/webhook'
   Invoke-RestMethod -Method Post -Uri "https://api.telegram.org/bot$botToken/setWebhook" -Body @{ url = $webhookUrl; secret_token = $webhookSecret; allowed_updates = '["message","callback_query"]' }
   ```

   Kết quả cần có `ok : True`. Không gửi token hay secret cho người khác. Sau đó thử `/start` và các nút trong Telegram. Kiểm tra lỗi tại Vercel Functions logs nếu bot không trả lời.

Trên Vercel, tin nhắn không tự xóa sau 5 phút vì bộ hẹn giờ trong bộ nhớ không được bảo đảm tiếp tục chạy; nút **Xong** vẫn xóa tin của bot. `/restart` không khởi động lại GitHub Actions. Giới hạn tần suất trong bộ nhớ chỉ áp dụng gần đúng cho từng instance.

Nếu Telegram đã khóa token hoặc tài khoản bot, chuyển nơi chạy không tự gỡ khóa; cần xử lý với Telegram hoặc dùng token hợp lệ.

## Chạy local bằng polling

Cài các thư viện trong `requirements.txt`, đặt `BOT_TOKEN` trong biến môi trường hoặc file `.env`, sau đó chạy `python bot.py`. Dừng polling trước khi dùng lại webhook Vercel.
