from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import uvicorn
from pydantic import BaseModel

from bs4 import BeautifulSoup

app = FastAPI()
html_storage = {}

# Mẫu HTML với CSS styling
TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đơn xin nghỉ phép</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            color: #2c5282;
            margin-bottom: 25px;
        }
        
        .form-group {
            display: flex;
            margin-bottom: 18px;
            align-items: center;
        }
        
        .form-label {
            width: 200px;
            font-weight: 600;
            padding-right: 15px;
        }
        
        .form-control {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: {{ "white" if editable else "#f9f9f9" }};
            {{ "cursor: not-allowed;" if not editable }}
        }
        
        input[type="text"], input[type="date"], input[type="checkbox"], textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        input[readonly], textarea[readonly] {
            background-color: #f9f9f9;
            cursor: not-allowed;
        }
        
        input[type="checkbox"] {
            width: auto;
        }
        
        .attachment-area {
            border: 2px dashed #ddd;
            padding: 20px;
            text-align: center;
            margin-top: 5px;
            border-radius: 4px;
            color: #666;
        }
        
        .action-buttons {
            display: flex;
            justify-content: center;
            margin-top: 25px;
            gap: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        
        .btn-primary {
            background-color: #2c5282;
            color: white;
        }
        
        .btn-secondary {
            background-color: #e2e8f0;
            color: #333;
        }
        
        .btn:hover {
            opacity: 0.9;
        }
        
        .leave-info {
            background-color: #ebf8ff;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #4299e1;
        }
        
        .error-message {
            color: #e53e3e;
            margin-top: 5px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Đơn xin nghỉ phép</h1>
        
        <div class="leave-info">
            <div class="form-group">
                <div class="form-label">Loại nghỉ</div>
                <div class="form-control">Nghỉ phép năm</div>
            </div>
            <div class="form-group">
                <div class="form-label">Số ngày còn lại</div>
                <div class="form-control">4 ngày</div>
            </div>
        </div>
        
        <form method="post" action="/submit">
            <div class="form-group">
                <label class="form-label">Cả ngày</label>
                <input type="checkbox" checked readonly>
            </div>
            
            <div class="form-group">
                <label class="form-label">Lịch làm việc</label>
                <div class="form-control">08:00 - 17:30</div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Ngày bắt đầu</label>
                <input type="date" name="Ngày bắt đầu" class="form-control" value="{{ start_date }}" {{ "readonly" if not editable }}>
            </div>
            
            <div class="form-group">
                <label class="form-label">Ngày kết thúc</label>
                <input type="date" name="Ngày kết thúc" class="form-control" value="{{ end_date }}" {{ "readonly" if not editable }}>
            </div>
            
            <div class="form-group">
                <label class="form-label">Đang yêu cầu</label>
                <div class="form-control">{{ requested_days }} ngày</div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Trở lại làm việc vào</label>
                <div class="form-control">{{ return_date }}</div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Lặp lại</label>
                <input type="checkbox">
            </div>
            
            <div class="form-group">
                <label class="form-label">Nhận xét</label>
                <textarea name="nhan_xet" class="form-control" rows="2"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Người tiếp nhận công việc (Nếu có)</label>
                <input type="text" name="nguoi_tiep_nhan" class="form-control">
            </div>
            
            <div class="form-group">
                <label class="form-label">Địa chỉ</label>
                <input type="text" name="address" class="form-control">
            </div>
            
            <div class="form-group">
                <label class="form-label">Lý do nghỉ</label>
                <textarea name="Lý do" class="form-control" rows="3" {{ "readonly" if not editable }}>{{ reason }}</textarea>
            </div>
        </form>
    </div>
</body>
</html>
"""

class LeaveRequestForm(BaseModel):
    start_date: str
    end_date: str
    reason: str



def convert_form_to_telegram_message(form_html):
    soup = BeautifulSoup(form_html, 'html.parser')
    message = "Thông tin đơn xin nghỉ:\n\n"
    
    message += "Thông tin hệ thống:\n"
    message += "*Loại nghỉ:* Nghỉ phép năm\n"
    message += "*Số ngày còn lại:* 4 ngày\n"
    message += "\nThông tin đăng ký:\n"
    for group in soup.select('.form-group'):
        label = group.find('label')
        
        # Tìm phần tử chứa dữ liệu, không chỉ input/textarea mà cả div/span/p
        value_tag = group.find(['input', 'textarea', 'select', 'div', 'span', 'p'])

        if label and value_tag:
            field_name = label.get_text(strip=True)

            # Xử lý giá trị:
            if value_tag.name in ['input', 'select']:
                value = value_tag.get('value', '').strip()
            elif value_tag.name == 'textarea':
                value = value_tag.text.strip()
            else:
                # div, span, p...
                value = value_tag.get_text(strip=True)

            if value:
                message += f"*{field_name}:* {value}\n"
        

    return message


@app.post("/generate")
async def generate(leave_request_form: LeaveRequestForm):
    print(leave_request_form)
    """Tạo form đơn xin nghỉ phép dựa trên dữ liệu nhập vào"""
    # Chuyển đổi chuỗi ngày thành đối tượng datetime
    start_date_obj = datetime.strptime(leave_request_form.start_date, '%d/%m/%Y')
    end_date_obj = datetime.strptime(leave_request_form.end_date, '%d/%m/%Y')
    
    # Tính số ngày yêu cầu (bao gồm cả ngày bắt đầu và kết thúc)
    delta = end_date_obj - start_date_obj
    requested_days = delta.days + 1
    
    # Tính ngày quay lại làm việc (ngày tiếp theo sau ngày kết thúc)
    return_date_obj = end_date_obj + timedelta(days=1)
    # Định dạng ngày trở lại làm việc theo tiếng Việt
    return_date = return_date_obj.strftime('%d thg %m %Y, 8:00 SA')
    
    # Định dạng ngày để hiển thị
    start_date_formatted = start_date_obj.strftime("Ngày %d tháng %m năm %Y")
    end_date_formatted = end_date_obj.strftime("Ngày %d tháng %m năm %Y")
    
    # Render mẫu với dữ liệu đã cung cấp
    from jinja2 import Template
    template = Template(TEMPLATE)
    html_content = template.render(
        start_date=start_date_formatted,
        end_date=end_date_formatted,
        reason=leave_request_form.reason,
        requested_days=requested_days,
        return_date=return_date,
        editable=False
    )
    message = convert_form_to_telegram_message(html_content)
    return message

@app.post('/submit')
async def submit():
    return "Đã gửi đơn xin nghỉ lên hệ thống SAPP"


if __name__ == "__main__":
    uvicorn.run("sapp_service:app", host="0.0.0.0", port=8001, reload=True)