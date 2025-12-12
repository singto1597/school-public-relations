let todayData = null;

async function fetchData() {
    try {
        // 1. ไปดึง JSON จาก Python
        const response = await fetch('/api/today');
        todayData = await response.json();
        renderUI(); // ดึงเสร็จ ให้วาดหน้าเว็บ
        startTimer(); // เริ่มจับเวลานับถอยหลัง
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('assembly-point').innerText = "System Offline";
    }
}

function renderUI() {
    if (!todayData) return;

    // แสดงวันที่
    document.getElementById('date-display').innerText = todayData.date;

    // แสดงจุดเข้าแถว
    const assemblyElem = document.getElementById('assembly-point');
    assemblyElem.innerText = todayData.assembly_point;
    
    // เปลี่ยนสีกล่องตามจุดเข้าแถว
    const statusBox = document.getElementById('status-box');
    if (todayData.assembly_point.includes('เสาธง')) {
        statusBox.style.backgroundColor = '#d1fae5'; // เขียวอ่อน
        statusBox.style.color = '#065f46';
    } else if (todayData.assembly_point.includes('หน้าห้อง')) {
        statusBox.style.backgroundColor = '#fef3c7'; // เหลืองอ่อน
        statusBox.style.color = '#92400e';
    }

    const modeNames = {
        'normal_50': 'ตาราง 2 (50 นาที)',
        'short_40': 'ตาราง 4 (40 นาที)',
        'even_50': 'ตาราง 3 (กิจกรรมเช้า)',
        'exam': 'ตารางสอบ'
    };

    const modeText = modeNames[todayData.schedule_mode] || todayData.schedule_mode;
    document.getElementById('schedule-mode-display').innerText = modeText;

    // แสดงประกาศ (ถ้ามี)
    if (todayData.special_message) {
        document.getElementById('announcement-box').style.display = 'block';
        document.getElementById('special-message').innerText = todayData.special_message;
    } else {
        document.getElementById('announcement-box').style.display = 'none';
    }

    const newsFeed = document.getElementById('news-feed');
    if (newsFeed && todayData.announcements) {
        newsFeed.innerHTML = '<h3>📰 ข่าวประชาสัมพันธ์</h3>'; // หัวข้อ
        todayData.announcements.forEach(news => {
            const newsItem = document.createElement('div');
            newsItem.className = 'card';
            newsItem.style.borderLeft = '4px solid #3b82f6'; // ขีดสีฟ้า
            newsItem.style.textAlign = 'left';
            newsItem.innerHTML = `
                <div style="font-weight:bold; font-size:1.1rem;">${news.title}</div>
                <div style="color:#4b5563; margin-top:5px;">${news.content}</div>
                <div style="color:#9ca3af; font-size:0.8rem; margin-top:8px;">🕒 ${news.date}</div>
            `;
            newsFeed.appendChild(newsItem);
        });
    }
    // วาดตารางเวลาด้านล่าง
    const list = document.getElementById('timeline-list');
    list.innerHTML = ''; // เคลียร์ของเก่า
    todayData.timetable.forEach(slot => {
        const li = document.createElement('li');
        li.innerHTML = `<span>${slot.period}</span> <span>${slot.start} - ${slot.end}</span>`;
        list.appendChild(li);
    });
}

function startTimer() {
    // ฟังก์ชันนับถอยหลัง ทำงานทุก 1 วินาที
    setInterval(() => {
        if (!todayData) return;
        
        const now = new Date();
        const currentTimeStr = now.toTimeString().slice(0, 5); // ได้ค่า "08:30"
        
        // หาว่าตอนนี้อยู่คาบไหน?
        let currentSlot = null;
        let nextSlot = null;

        // วนลูปหาคาบปัจจุบัน
        for (let i = 0; i < todayData.timetable.length; i++) {
            const slot = todayData.timetable[i];
            
            // เปรียบเทียบเวลา (String compare)
            if (currentTimeStr >= slot.start && currentTimeStr < slot.end) {
                currentSlot = slot;
                nextSlot = todayData.timetable[i+1];
                break;
            }
        }

        // อัปเดตหน้าจอ
        if (currentSlot) {
            document.getElementById('current-period-name').innerText = currentSlot.period;
            
            // แสดงเวลาเลิกคาบ
            document.getElementById('countdown-timer').innerText = `ถึงเวลา ${currentSlot.end}`;
            document.getElementById('countdown-timer').style.fontSize = "1.5rem";
            
            if (nextSlot) {
                document.getElementById('next-period-label').innerText = `ต่อไป: ${nextSlot.period}`;
            } else {
                document.getElementById('next-period-label').innerText = "จบวันแล้วเย้! 🎉";
            }
        } else {
            document.getElementById('current-period-name').innerText = "นอกเวลาเรียน";
            document.getElementById('countdown-timer').innerText = "--:--";
        }

    }, 1000);
}

// เริ่มทำงานทันที
fetchData();