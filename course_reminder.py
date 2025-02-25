import json
import requests
from datetime import datetime, time, timedelta

# PushPlus配置
PUSHPLUS_TOKEN = "e346b020ed5d46959ffb884f5ef3f3ad"  # 用户的PushPlus token

# 学期开始日期（第一周的星期一）
SEMESTER_START_DATE = datetime(2023, 9, 4)  # 2023年9月4日，根据实际情况修改

# 课程数据
def load_schedule():
    with open('schedule.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_week():
    """自动计算当前是第几周"""
    today = datetime.now()
    days_passed = (today - SEMESTER_START_DATE).days
    current_week = days_passed // 7 + 1
    return current_week

# 当前周次
CURRENT_WEEK = get_current_week()

def parse_weeks(weeks_str):
    """解析周次字符串，返回包含的周次列表"""
    if not weeks_str:
        return []
        
    result = []
    parts = weeks_str.split(', ')
    
    for part in parts:
        if '-' in part:
            # 处理范围，如 "1-4周"
            range_part = part.replace('周', '')
            start, end = map(int, range_part.split('-'))
            result.extend(range(start, end + 1))
        else:
            # 处理单个周次，如 "7周"
            week = int(part.replace('周', ''))
            result.append(week)
    
    return result

def is_course_in_current_week(course, week=None):
    """判断课程是否在指定周次"""
    if week is None:
        week = CURRENT_WEEK
        
    if 'weeks' not in course or not course['weeks']:
        return False  # 如果没有指定周次，默认不显示
    
    weeks_list = parse_weeks(course['weeks'])
    return week in weeks_list

def get_courses_by_weekday(weekday, week=None):
    """获取指定星期几的课程安排"""
    if week is None:
        week = CURRENT_WEEK
        
    schedule_data = load_schedule()
    
    if weekday in schedule_data:
        # 筛选指定周次的课程
        return [course for course in schedule_data[weekday] if is_course_in_current_week(course, week)]
    return []

def get_today_courses():
    """获取今天的课程安排"""
    # 获取今天是星期几
    weekday = datetime.now().strftime("%A").lower()
    return get_courses_by_weekday(weekday)

def get_tomorrow_courses():
    """获取明天的课程安排"""
    # 获取明天是星期几
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weekday = tomorrow.strftime("%A").lower()
    return get_courses_by_weekday(tomorrow_weekday)

def get_morning_courses(courses):
    """获取上午的课程"""
    return [course for course in courses if "上午" in course['time']]

def get_afternoon_courses(courses):
    """获取下午的课程"""
    return [course for course in courses if "下午" in course['time']]

def format_morning_reminder(courses):
    """格式化上午课程提醒"""
    if not courses:
        return "今天上午没有课程安排，可以睡个懒觉啦！😴"
    
    now = datetime.now()
    weekday_names = {
        "monday": "星期一", "tuesday": "星期二", "wednesday": "星期三",
        "thursday": "星期四", "friday": "星期五", "saturday": "星期六", "sunday": "星期日"
    }
    weekday = weekday_names[now.strftime("%A").lower()]
    
    message = f"早上好杨天宇同学！今天是第{CURRENT_WEEK}周{weekday}，再过20分钟就要迟到啦！赶紧出门吧！🏃‍♂️\n\n"
    message += "【今日上午课程】\n"
    
    for course in courses:
        message += f"📚 {course['time']} - {course['course']}\n"
        message += f"👨‍🏫 {course['teacher']} @ {course['location']}\n"
        message += "📝 需要带的书：\n"
        for book in course['books']:
            message += f"  ✅ {book}\n"
        message += "\n"
    
    message += "别忘了带上笔记本和水杯！祝你学习愉快！✨"
    return message

def format_afternoon_reminder(courses):
    """格式化下午课程提醒"""
    if not courses:
        return "今天下午没有课程安排，可以好好休息一下啦！🛋️"
    
    message = f"中午好杨天宇同学！下午的课程马上就要开始了，再过20分钟就要迟到啦！🕒\n\n"
    message += "【今日下午课程】\n"
    
    for course in courses:
        message += f"📚 {course['time']} - {course['course']}\n"
        message += f"👨‍🏫 {course['teacher']} @ {course['location']}\n"
        message += "📝 需要带的书：\n"
        for book in course['books']:
            message += f"  ✅ {book}\n"
        message += "\n"
    
    message += "记得带上充电宝和水杯！下午的课程也要加油哦！💪"
    return message

def format_daily_summary(today_courses, tomorrow_courses):
    """格式化每日课程总结"""
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    
    weekday_names = {
        "monday": "星期一", "tuesday": "星期二", "wednesday": "星期三",
        "thursday": "星期四", "friday": "星期五", "saturday": "星期六", "sunday": "星期日"
    }
    
    today_weekday = weekday_names[now.strftime("%A").lower()]
    tomorrow_weekday = weekday_names[tomorrow.strftime("%A").lower()]
    
    message = f"晚上好杨天宇同学！现在是晚上9点，这是今天（第{CURRENT_WEEK}周{today_weekday}）的课程总结：\n\n"
    
    if not today_courses:
        message += "今天没有课程安排，希望你度过了愉快的一天！🎮\n\n"
    else:
        for course in today_courses:
            message += f"📚 {course['time']} - {course['course']}\n"
            message += f"👨‍🏫 {course['teacher']} @ {course['location']}\n"
            if 'note' in course and course['note']:
                message += f"📌 {course['note']}\n"
            message += "\n"
    
    # 添加明天的课程预习提醒
    message += f"【明天（{tomorrow_weekday}）课程预习提醒】\n"
    
    if not tomorrow_courses:
        message += f"明天没有课程安排，可以好好放松一下！🎉\n"
    else:
        message += "建议今晚预习以下课程：\n\n"
        for course in tomorrow_courses:
            message += f"📖 {course['time']} - {course['course']}\n"
            message += f"👨‍🏫 {course['teacher']} @ {course['location']}\n"
            message += "📝 预习准备：\n"
            for book in course['books']:
                message += f"  ✅ {book}\n"
            message += "\n"
    
    message += "记得整理今天的笔记，准备好明天需要的材料！晚安！🌙✨"
    return message

def format_week_message(week_courses):
    """格式化整周的课程信息"""
    message = f"📅 第{CURRENT_WEEK}周完整课表 📅\n\n"
    
    day_names = {
        "monday": "星期一", "tuesday": "星期二", "wednesday": "星期三",
        "thursday": "星期四", "friday": "星期五", "saturday": "星期六", "sunday": "星期日"
    }
    
    for day, day_name in day_names.items():
        courses = week_courses[day]
        if not courses:
            message += f"【{day_name}】休息日，没有课程安排~\n\n"
            continue
        
        message += f"【{day_name}】课程安排：\n"
        for course in courses:
            if not course['course']:  # 跳过空课程
                continue
                
            message += f"📚 {course['time']} - {course['course']}\n"
            message += f"👨‍🏫 {course['teacher']} @ {course['location']}\n"
            message += "📝 需要带的书：\n"
            for book in course['books']:
                message += f"  ✅ {book}\n"
            message += "\n"
    
    message += "祝你学习愉快！记得提前准备好每天需要的材料哦！📚✨"
    return message

def send_pushplus_notification(title, content):
    """使用PushPlus发送通知到手机"""
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "txt"  # 使用文本模板
        }
        print(f"正在发送通知到PushPlus，token: {PUSHPLUS_TOKEN[:4]}...{PUSHPLUS_TOKEN[-4:]}")
        response = requests.post(url, json=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print("消息推送成功！")
            else:
                print(f"消息推送失败！错误信息: {result.get('msg')}")
        else:
            print(f"消息推送失败！状态码：{response.status_code}")
    except Exception as e:
        print(f"消息推送出错：{str(e)}")
        import traceback
        print(f"详细错误信息：\n{traceback.format_exc()}")

def morning_reminder():
    """发送上午课程提醒"""
    courses = get_today_courses()
    morning_courses = get_morning_courses(courses)
    message = format_morning_reminder(morning_courses)
    print(f"上午课程提醒：\n{message}")
    
    # 发送推送通知
    send_pushplus_notification("⏰ 上午课程提醒", message)

def afternoon_reminder():
    """发送下午课程提醒"""
    courses = get_today_courses()
    afternoon_courses = get_afternoon_courses(courses)
    message = format_afternoon_reminder(afternoon_courses)
    print(f"下午课程提醒：\n{message}")
    
    # 发送推送通知
    send_pushplus_notification("⏰ 下午课程提醒", message)

def daily_summary():
    """发送每日课程总结"""
    today_courses = get_today_courses()
    tomorrow_courses = get_tomorrow_courses()
    message = format_daily_summary(today_courses, tomorrow_courses)
    print(f"每日课程总结：\n{message}")
    
    # 发送推送通知
    send_pushplus_notification("📝 今日课程总结与明日预习", message)

def weekly_reminder():
    """发送整周课程提醒"""
    schedule_data = load_schedule()
    week_courses = {}
    
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        if day in schedule_data:
            # 筛选当前周次的课程
            week_courses[day] = [course for course in schedule_data[day] if is_course_in_current_week(course)]
        else:
            week_courses[day] = []
    
    message = format_week_message(week_courses)
    print(f"第{CURRENT_WEEK}周课程信息：\n{message}")
    
    # 发送推送通知
    send_pushplus_notification(f"📅 第{CURRENT_WEEK}周完整课表", message)

def determine_reminder_type():
    """根据当前时间决定发送哪种类型的提醒"""
    current_time = datetime.now().time()
    
    if time(7, 30) <= current_time <= time(8, 30):
        # 早上7:30-8:30发送上午课程提醒
        morning_reminder()
    elif time(13, 0) <= current_time <= time(14, 0):
        # 下午1:00-2:00发送下午课程提醒
        afternoon_reminder()
    elif time(21, 0) <= current_time <= time(22, 0):
        # 晚上9:00-10:00发送每日课程总结
        daily_summary()
    else:
        # 其他时间发送整周课程提醒
        weekly_reminder()

if __name__ == "__main__":
    # 根据当前时间决定发送哪种类型的提醒
    determine_reminder_type() 
