# Практическая работа №1  
# Базовые принципы администрирования Linux

## Цель работы

Развернуть и настроить 3 виртуальные машины Linux в VirtualBox, организовать сетевое взаимодействие между ними через промежуточную машину-шлюз, поднять HTTP-сервер на Linux A, выполнить запросы с Linux C на Linux A и проконтролировать прохождение трафика через Linux B.

## Используемые инструменты

- VirtualBox
- Ubuntu Server 22.04
- Netplan
- Python 3
- Flask
- curl
- tcpdump

## Исходные данные

- Фамилия: **Dolinin**
- День рождения: **4**
- Месяц рождения: **9**

## Схема стенда

Были развернуты 3 виртуальные машины:

- **Linux A** — сервер
- **Linux B** — шлюз
- **Linux C** — клиент

Сетевая схема:

- Linux A ↔ Linux B : сеть `192.168.4.0/24`
- Linux B ↔ Linux C : сеть `192.168.9.0/24`

Назначенные IP-адреса:

- **Linux A**: `192.168.4.10/24`
- **Linux B**:
  - `192.168.4.1/24`
  - `192.168.9.10/24`
- **Linux C**: `192.168.9.100/24`

---

# 1. Подготовка виртуальных машин

В VirtualBox были созданы 3 виртуальные машины на базе Ubuntu Server 22.04.

## Настройка сетевых адаптеров в VirtualBox

### Linux A
- Adapter 1: `NAT`
- Adapter 2: `Internal Network` → `net-a`

### Linux B
- Adapter 1: `NAT`
- Adapter 2: `Internal Network` → `net-a`
- Adapter 3: `Internal Network` → `net-b`

### Linux C
- Adapter 1: `NAT`
- Adapter 2: `Internal Network` → `net-b`

---

# 2. Настройка Linux A

## 2.1. Hostname и пользователь

Для Linux A был задан hostname, а также добавлен пользователь:

```bash
sudo hostnamectl set-hostname dolinin_server
sudo adduser dolinin_1
```
## 2.2. Настройка сети
На машине А были обнаружены интерфейсы:
- enp0s3 — NAT
- enp0s8 — внутренняя сеть
Файл `/etc/netplan/00-installer-config.yaml` был настроен следующим образом:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses:
        - 192.168.4.10/24
      routes:
        - to: 192.168.9.0/24
          via: 192.168.4.1
```
Применение настроек:
```bash
sudo chmod 600 /etc/netplan/00-installer-config.yaml
sudo netplan apply
```
В результате интерфейс `enp0s8` получил адрес `192.168.4.10/24`, а маршрут в сеть `192.168.9.0/24` был направлен через `192.168.4.1`.
## 2.3. Развертывание HTTP-сервера
На Linux A был развернут простой HTTP-сервер на Flask, работающий на порту `5000`.
Файл `app.py`:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/get")
def get_data():
    return jsonify({"method": "GET", "status": "ok"})

@app.post("/post")
def post_data():
    return jsonify({"method": "POST", "data": request.get_json(silent=True)})

@app.put("/put")
def put_data():
    return jsonify({"method": "PUT", "data": request.get_json(silent=True)})

app.run(host="0.0.0.0", port=5000)
```
---

# 3 Настройка Linux B

## 3.1. Hostname и пользователь

Для Linux B был задан hostname и создан пользователь:

```bash
sudo hostnamectl set-hostname dolinin_gateway
sudo adduser dolinin_2
```
# 3.2. Настройка сети

На машине B были обнаружены интерфейсы:

- enp0s3 — `NAT`
- enp0s8 — `net-a`
- enp0s9 — `net-b`

Файл /etc/netplan/00-installer-config.yaml был настроен следующим образом:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses:
        - 192.168.4.1/24
    enp0s9:
      dhcp4: false
      addresses:
        - 192.168.9.10/24
```
Применение настроек
```bash
sudo chmod 600 /etc/netplan/00-installer-config.yaml
sudo netplan apply
```
В результате Linux B получил два адреса:

- `192.168.4.1/24` в сети между Linux A и Linux B;
- `192.168.9.10/24` в сети между Linux B и Linux C.
## 3.3. Включение маршрутизации
Для пересылки пакетов между интерфейсами на Linux B был включён IP forwarding.
```bash
sudo nano /etc/sysctl.conf
```
Раскомментирована строка
```bash
net.ipv4.ip_forward=1
sudo sysctl -p
```
## 3.4. Запуск tcpdump
Для контроля прохождения HTTP-трафика через Linux B был запущен tcpdump с фильтрацией по порту `5000`.\
Во время выполнения запросов с Linux C на Linux A в выводе tcpdump фиксировались TCP-пакеты, проходящие через шлюз.
```bash
sudo tcpdump -i any port 5000
```
---
# 4. Настройка Linux C
## 4.1. Hostname и пользователь
Для Linux C был задан hostname и создан пользователь:
```bash
sudo hostnamectl set-hostname dolinin_client
sudo adduser dolinin_3
```
## 4.2. Настройка сети
На машине C были обнаружены интерфейсы:
- enp0s3 — NAT
- enp0s8 — внутренняя сеть net-b\
Файл `/etc/netplan/00-installer-config.yaml` был настроен следующим образом:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses:
        - 192.168.9.100/24
      routes:
        - to: 192.168.4.0/24
          via: 192.168.9.10
```
Применение настроек
```bash
sudo chmod 600 /etc/netplan/00-installer-config.yaml
sudo netplan apply
```
В результате интерфейс enp0s8 получил адрес `192.168.9.100/24`, а маршрут в сеть `192.168.4.0/24` был направлен через `192.168.9.10`
## 4.3. Проверка сетевой связности
С Linux C была выполнена проверка доступности шлюза и сервера:
```bash
ping 192.168.9.10
ping 192.168.4.10
```
Пакеты успешно доходили до Linux B и Linux A, что подтверждало корректность маршрутизации.
## 4.4. Отправка HTTP-запросов
С Linux C были отправлены три HTTP-запроса к серверу на Linux A с помощью curl.\
В ответ сервер возвращал JSON-ответы, подтверждающие успешную обработку запросов.

```bash
curl http://192.168.4.10:5000/get
```
```bash
curl -X POST http://192.168.4.10:5000/post 
  -H "Content-Type: application/json" 
  -d '{"name":"Dolinin","lab":"1"}'
```
```bash
curl -X PUT http://192.168.4.10:5000/put 
  -H "Content-Type: application/json" 
  -d '{"status":"updated"}'
```
___
# 5. Обеспечение сохранения настроек после перезагрузки
## 5.1. Сохранение сетевой конфигурации
Сетевые настройки были сохранены в файлах Netplan, поэтому после перезагрузки системы IP-адреса и маршруты применялись автоматически
## 5.3. Сохранение правил iptables
Для сохранения правил iptables после перезагрузки был установлен пакет:
```bash
sudo apt update
sudo apt install iptables-persistent -y
```
После этого текущие правила были сохранены автоматически и восстанавливались при запуске системы.
___
# 6. Результаты выполнения работы

В ходе выполнения практической работы были:

- Развернуты три виртуальные машины на Ubuntu Server 22.04;
- Настроены hostname и пользователи на каждой машине;
- Сконфигурирована сетевая схема с двумя подсетями;
- Настроена маршрутизация через промежуточную машину Linux B;
- Реализован HTTP-сервер на Flask на Linux A;
- Выполнены GET, POST и PUT-запросы с Linux C на Linux A;
- Выполнен контроль трафика на Linux B с помощью tcpdump;
- Обеспечено сохранение сетевых настроек и маршрутизации после перезагрузки.
___
# 7. Заключение

В результате выполнения работы были изучены базовые принципы администрирования Linux, включая настройку сети, статическую маршрутизацию, запуск сетевых сервисов, а также сохранения настроек после перезагрузки системы.
