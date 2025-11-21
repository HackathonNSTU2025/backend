from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

app = FastAPI(docs_url=None, redoc_url=None)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("✅ Новое подключение")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Отправить сообщение всем подключенным клиентам"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Хранилище данных для 3 станций
queues = {
    "vr": [],      # VR очки
    "robots": [],  # Робототехника  
    "quest": []    # Квесты
}

# Названия станций
station_names = {
    "vr": "Станция VR",
    "robots": "Станция Роботы", 
    "quest": "Станция Квест"
}

# Константы
AVERAGE_SERVICE_TIME = 15  # 15 минут на человека

def get_station_available_time(station_type: str) -> str:
    """Получить время когда станция освободится"""
    if not queues[station_type]:
        return datetime.now().isoformat()
    
    # Время окончания последнего в очереди
    last_person = queues[station_type][-1]
    return last_person["service_end_time"]

def calculate_service_times(station_type: str):
    """Рассчитать время начала и окончания обслуживания"""
    if not queues[station_type]:
        # Если очередь пустая - начинаем сейчас
        service_start = datetime.now()
    else:
        # Начинаем после окончания последнего
        last_person = queues[station_type][-1]
        service_start = datetime.fromisoformat(last_person["service_end_time"])
    
    service_end = service_start + timedelta(minutes=AVERAGE_SERVICE_TIME)
    return service_start, service_end

HTML_DOCS = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 T-Bank Queue System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .panel { border: 2px solid #333; padding: 20px; margin: 10px; border-radius: 10px; background: white; }
        .admin { border-color: #e74c3c; }
        .user { border-color: #3498db; }
        .stations { border-color: #9b59b6; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; border: none; border-radius: 5px; font-weight: bold; }
        .btn-join { background: #3498db; color: white; }
        .btn-serve { background: #e74c3c; color: white; }
        .btn-station { background: #9b59b6; color: white; margin: 2px; }
        .btn-json { background: #f39c12; color: white; }
        input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        #notifications { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background: #f9f9f9; }
        .notification { margin: 5px 0; padding: 8px; border-left: 4px solid #3498db; background: white; border-radius: 4px; }
        .success { border-left-color: #27ae60; background: #d5f4e6; }
        .warning { border-left-color: #f39c12; background: #fdebd0; }
        .info { border-left-color: #3498db; background: #d6eaf8; }
        .error { border-left-color: #e74c3c; background: #fadbd8; }
        .json-result { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🚀 T-Bank Queue System - 3 Станции</h1>
    
    <div class="panel stations">
        <h2>🎯 ВЫБОР СТАНЦИИ (пользователь)</h2>
        <div>
            <button class="btn-station" onclick="joinStation('vr')">🥽 Станция VR</button>
            <button class="btn-station" onclick="joinStation('robots')">🤖 Станция Роботы</button>
            <button class="btn-station" onclick="joinStation('quest')">🎪 Станция Квест</button>
        </div>
        <input type="text" id="userName" placeholder="Имя" value="Иван">
        <input type="text" id="userLastName" placeholder="Фамилия" value="Петров">
    </div>
    
    <div class="panel admin">
        <h2>👨‍💼 АДМИНИСТРАТОР / УПРАВЛЕНИЕ</h2>
        <div>
            <button class="btn-serve" onclick="serveNext('vr')">🔄 VR - Обслужить следующего</button>
            <button class="btn-serve" onclick="serveNext('robots')">🔄 Роботы - Обслужить следующего</button>
            <button class="btn-serve" onclick="serveNext('quest')">🔄 Квест - Обслужить следующего</button>
        </div>
        <div style="margin-top: 15px;">
            <button class="btn-json" onclick="getQueueJSON('vr')">📋 VR - JSON очереди</button>
            <button class="btn-json" onclick="getQueueJSON('robots')">📋 Роботы - JSON очереди</button>
            <button class="btn-json" onclick="getQueueJSON('quest')">📋 Квест - JSON очереди</button>
            <button class="btn-json" onclick="getAllQueuesJSON()">📋 Все очереди (JSON)</button>
        </div>
    </div>
    
    <div class="panel">
        <h2>🔔 УВЕДОМЛЕНИЯ (WebSocket в реальном времени)</h2>
        <div>
            <strong>Статус WebSocket:</strong> <span id="wsStatus">🔄 Подключаемся...</span>
        </div>
        <div id="notifications">
            <div class="notification info">⏳ Ожидайте уведомлений...</div>
        </div>
    </div>

    <div id="jsonResult" style="display: none; margin-top: 20px;">
        <h3>📄 JSON Ответ:</h3>
        <pre class="json-result" id="jsonContent"></pre>
    </div>

    <script>
        let ws = null;
        
        function addNotification(message, type = 'info') {
            const notifications = document.getElementById('notifications');
            const div = document.createElement('div');
            div.className = 'notification ' + type;
            div.innerHTML = '<strong>🕒 ' + new Date().toLocaleTimeString() + ':</strong> ' + message;
            notifications.appendChild(div);
            notifications.scrollTop = notifications.scrollHeight;
        }
        
        function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = function() {
                    document.getElementById('wsStatus').innerHTML = '✅ <strong>Подключен</strong>';
                    addNotification('WebSocket подключен - получаете уведомления в реальном времени', 'success');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function() {
                    document.getElementById('wsStatus').innerHTML = '🔴 <strong>Отключен</strong>';
                    addNotification('WebSocket отключен', 'error');
                    // Переподключение через 3 секунды
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function() {
                    document.getElementById('wsStatus').innerHTML = '🔴 <strong>Ошибка</strong>';
                };
                
            } catch (error) {
                addNotification('Ошибка подключения: ' + error, 'error');
            }
        }
        
        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'user_joined':
                    addNotification(data.message, 'info');
                    break;
                case 'user_served':
                    addNotification(data.message, 'success');
                    break;
                case 'next_in_line':
                    addNotification(data.message, 'warning');
                    break;
                case 'welcome':
                    addNotification(data.message, 'info');
                    break;
            }
        }
        
        function showJSONResult(data) {
            const jsonResult = document.getElementById('jsonResult');
            const jsonContent = document.getElementById('jsonContent');
            
            jsonContent.textContent = JSON.stringify(data, null, 2);
            jsonResult.style.display = 'block';
            jsonResult.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function joinStation(stationType) {
            const firstName = document.getElementById('userName').value.trim();
            const lastName = document.getElementById('userLastName').value.trim();
            
            if (!firstName || !lastName) {
                addNotification('❌ Введите имя и фамилию', 'error');
                return;
            }
            
            try {
                addNotification(`⏳ Добавляем ${firstName} ${lastName} на станцию ${stationType}...`, 'info');
                
                const response = await fetch('/queue/' + stationType + '/join?first_name=' + encodeURIComponent(firstName) + '&last_name=' + encodeURIComponent(lastName), {
                    method: 'POST'
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                addNotification(`✅ ${data.message}`, 'success');
                
            } catch (error) {
                addNotification('❌ Ошибка: ' + error.message, 'error');
            }
        }
        
        async function serveNext(stationType) {
            try {
                addNotification(`⏳ Обслуживаем следующего на станции ${stationType}...`, 'info');
                
                const response = await fetch('/queue/' + stationType + '/serve-next', {
                    method: 'POST'
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    addNotification(`✅ ${data.message}`, 'success');
                } else {
                    addNotification(`ℹ️ ${data.error}`, 'info');
                }
                
            } catch (error) {
                addNotification('❌ Ошибка: ' + error.message, 'error');
            }
        }
        
        async function getQueueJSON(stationType) {
            try {
                const response = await fetch('/queue/' + stationType);
                const data = await response.json();
                showJSONResult(data);
                addNotification(`📋 Получена JSON очередь станции ${stationType}`, 'info');
            } catch (error) {
                addNotification('❌ Ошибка при получении JSON: ' + error.message, 'error');
            }
        }
        
        async function getAllQueuesJSON() {
            try {
                const response = await fetch('/admin/queues');
                const data = await response.json();
                showJSONResult(data);
                addNotification('📋 Получены все очереди в JSON', 'info');
            } catch (error) {
                addNotification('❌ Ошибка при получении всех очередей: ' + error.message, 'error');
            }
        }
        
        // Авто-подключение при загрузке
        window.onload = function() {
            addNotification('🚀 Система запускается...', 'info');
            connectWebSocket();
        };
    </script>
</body>
</html>
'''

@app.get("/")
async def root():
    return {"message": "T-Bank Queue System API", "version": "1.0.0"}

@app.get("/docs")
async def documentation():
    return HTMLResponse(HTML_DOCS)

# JSON endpoints для администраторов
@app.get("/admin/queues")
async def get_all_queues():
    """Получить все очереди в JSON (для администраторов)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "stations": {
            "vr": {
                "name": "Станция VR",
                "queue": queues["vr"],
                "total_waiting": len(queues["vr"]),
                "next_available_time": get_station_available_time("vr")
            },
            "robots": {
                "name": "Станция Роботы", 
                "queue": queues["robots"],
                "total_waiting": len(queues["robots"]),
                "next_available_time": get_station_available_time("robots")
            },
            "quest": {
                "name": "Станция Квест",
                "queue": queues["quest"],
                "total_waiting": len(queues["quest"]),
                "next_available_time": get_station_available_time("quest")
            }
        }
    }

@app.get("/queue/{station_type}")
async def get_queue(station_type: str):
    """Получить очередь конкретной станции в JSON"""
    if station_type not in queues:
        raise HTTPException(404, "Станция не найдена")
    
    return {
        "station_type": station_type,
        "station_name": station_names[station_type],
        "queue": queues[station_type],
        "total": len(queues[station_type]),
        "next_available_time": get_station_available_time(station_type),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/queue/{station_type}/join")
async def join_queue(station_type: str, first_name: str, last_name: str):
    """Встать в очередь на конкретную станцию"""
    if station_type not in queues:
        raise HTTPException(404, "Станция не найдена")
    
    user_id = str(uuid.uuid4())
    
    # Рассчитываем время обслуживания
    service_start, service_end = calculate_service_times(station_type)
    queue_position = len(queues[station_type]) + 1
    
    user_data = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "station_type": station_type,
        "queue_position": queue_position,
        "service_start_time": service_start.isoformat(),
        "service_end_time": service_end.isoformat(),
        "joined_at": datetime.now().isoformat()
    }
    
    queues[station_type].append(user_data)
    
    # Уведомление о добавлении
    end_time_str = service_end.strftime('%H:%M')
    await manager.broadcast({
        "type": "user_joined",
        "message": f"🎫 {first_name} {last_name} встал в очередь на станции {station_names[station_type]}. Позиция: {queue_position}. Окончание: {end_time_str}",
        "user_data": user_data,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "user_id": user_id,
        "station_type": station_type,
        "station_name": station_names[station_type],
        "queue_position": queue_position,
        "service_end_time": service_end.isoformat(),
        "message": f"Вы в очереди на станции {station_names[station_type]}! Номер: {queue_position}. Окончание: {end_time_str}"
    }

@app.post("/queue/{station_type}/serve-next")
async def serve_next(station_type: str):
    """Обслужить следующего на станции"""
    if station_type not in queues:
        raise HTTPException(404, "Станция не найдена")
    
    if not queues[station_type]:
        return {"error": "Очередь пуста"}
    
    served_user = queues[station_type].pop(0)
    
    # Обновляем времена для оставшихся в очереди
    current_time = datetime.now()
    for user in queues[station_type]:
        user["service_start_time"] = current_time.isoformat()
        user["service_end_time"] = (current_time + timedelta(minutes=AVERAGE_SERVICE_TIME)).isoformat()
        current_time = datetime.fromisoformat(user["service_end_time"])
    
    # Уведомление об обслуживании
    await manager.broadcast({
        "type": "user_served", 
        "message": f"✅ {served_user['first_name']} {served_user['last_name']} обслужен на станции {station_names[station_type]}!",
        "served_user": served_user,
        "timestamp": datetime.now().isoformat()
    })
    
    # Уведомляем следующего
    if queues[station_type]:
        next_user = queues[station_type][0]
        next_end_time = datetime.fromisoformat(next_user["service_end_time"]).strftime('%H:%M')
        await manager.broadcast({
            "type": "next_in_line",
            "message": f"🎯 {next_user['first_name']} {next_user['last_name']} - вы следующий на станции {station_names[station_type]}! Окончание: {next_end_time}",
            "next_user": next_user,
            "timestamp": datetime.now().isoformat()
        })
    
    remaining_count = len(queues[station_type])
    return {
        "success": True,
        "served_user": served_user,
        "remaining_count": remaining_count,
        "message": f"Обслужен {served_user['first_name']} на станции {station_names[station_type]}. Осталось: {remaining_count} чел."
    }

# WebSocket endpoint для всех
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "welcome", 
            "message": "🔌 Подключены к системе очередей T-Bank",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            
    except Exception as e:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)