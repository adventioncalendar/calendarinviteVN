from flask import Flask, Response
from datetime import datetime, timedelta, date
import uuid
import calendar

app = Flask(__name__)

def ics_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )

def dtstamp_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

def yyyymmdd(d: date):
    return d.strftime("%Y%m%d")

def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()
    base_date = now.date()  # dynamic start = download date (UTC)

    # 6 different events (each repeats every 6 months; together = monthly forever)
    events_data = [
    ("Bảo vệ bản thân và bạn tình của bạn bằng cách tự xét nghiệm HIV","Bạn đang quen người mới hoặc không chắc về tình trạng HIV của bạn tình? Tự xét nghiệm giúp bạn yên tâm hơn và bảo vệ những điều quan trọng. Xét nghiệm định kỳ giúp bạn chủ động kiểm soát sức khỏe và hỗ trợ phòng ngừa HIV."),
    ("Xác nhận tình trạng HIV của bạn sau khi có nguy cơ phơi nhiễm: Hãy tự xét nghiệm HIV ngay","Bạn đã quan hệ tình dục không sử dụng biện pháp bảo vệ hoặc bao cao su bị rách? Hãy tự xét nghiệm HIV càng sớm càng tốt. Nếu phơi nhiễm xảy ra trong vòng 72 giờ qua, hãy tìm đến dịch vụ PEP ngay lập tức. Hành động sớm giúp bạn được bảo vệ và có đầy đủ thông tin."),
    ("Chuẩn bị cho lần nhận thuốc PrEP định kỳ hàng quý bằng cách tự xét nghiệm HIV ngay","Bạn đang sử dụng PrEP hoặc tiếp tục các biện pháp phòng ngừa HIV? Nếu bạn đang dùng PrEP đường uống hằng ngày, hãy tự xét nghiệm HIV ít nhất mỗi 3 tháng. Xét nghiệm định kỳ giúp việc sử dụng PrEP của bạn luôn an toàn, hiệu quả và đúng kế hoạch."),
    ("Hãy tự tin khi đang sử dụng hoặc chuẩn bị sử dụng lại PrEP bằng cách tự xét nghiệm HIV ngay","Bạn đã tạm ngừng hoặc đang cân nhắc sử dụng lại PrEP? Trước khi bắt đầu lại, hãy xác nhận tình trạng HIV âm tính của bạn bằng cách tự xét nghiệm. Xét nghiệm định kỳ giúp bảo vệ bạn và duy trì hiệu quả của kế hoạch phòng ngừa."),
    ("Chủ động bảo vệ sức khỏe của bạn bằng cách tự xét nghiệm HIV ngay","Cảm thấy khỏe mạnh không phải lúc nào cũng có nghĩa là bạn không nhiễm HIV. Nhiều người không có triệu chứng trong giai đoạn đầu. Tự xét nghiệm giúp bạn có thông tin rõ ràng, sự tự tin và chủ động kiểm soát tình trạng HIV của mình."),
    ("Hãy đưa tự xét nghiệm HIV vào kế hoạch chăm sóc sức khỏe cá nhân sau khi tạm ngừng PrEP","Bạn không nhớ lần gần nhất mình xét nghiệm là khi nào? Đây là thời điểm thích hợp để tự xét nghiệm HIV. Xét nghiệm định kỳ giúp phát hiện sớm và giúp bạn tự tin hơn trên hành trình phòng ngừa HIV."),
]

    # Alerts:
    # - Day before: midnight the day before (relative to all-day start at 00:00)
    alarm_day_before = "TRIGGER;RELATED=START:-P1D"
    # - Day of: 9am local time on the day (00:00 + 9 hours)
    alarm_day_of = "TRIGGER;RELATED=START:PT9H"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, (title, description) in enumerate(events_data):
        start_date = add_months(base_date, i)
        end_date = start_date + timedelta(days=1)

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@ics-generator",
            f"DTSTAMP:{dtstamp_utc(now)}",
            f"DTSTART;VALUE=DATE:{yyyymmdd(start_date)}",
            f"DTEND;VALUE=DATE:{yyyymmdd(end_date)}",
            "RRULE:FREQ=MONTHLY;INTERVAL=6",
            f"SUMMARY:{ics_escape(title)}",
            f"DESCRIPTION:{ics_escape(description)}",

            # Alert 1: day before
            "BEGIN:VALARM",
            alarm_day_before,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            # Alert 2: day of (9am)
            "BEGIN:VALARM",
            alarm_day_of,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ics = "\r\n".join(lines) + "\r\n"

    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=invite.ics"},
    )

@app.route("/")
def health():
    return "OK. Try /invite.ics"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)




