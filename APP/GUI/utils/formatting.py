
# async def formatting_status(
#     status: str
#     ) -> str:
#     """
#     New:Active:Ready:Ban:Waits
#     """
#     if status == "New":      text = f"🆕<b>Новый</b>🆕"
#     elif status == "Young_Active": text = f"🆕<b>Первый Запуск</b>🆕"
#     elif status == "Ready":  text = f"🅿️<b>Отработал</b>🅿️"
#     elif status == "Old_Active": text = f"🔄<b>В работе</b>🔄"
#     elif status == "Ban":    text = f"⛔️<b>БАН</b>⛔️"
#     elif status == "Waits":  text = f"⏳<b>Ждёт старта</b>⏳"
#     elif status == "Support":text = f"🦾<b>Для поддержки</b>🤖"
#     elif status == "Delete": text = f"❌<b>Удалён</b>❌"
    
#     max_length = 25
#     formatted_text = text.center(max_length)[:max_length]
#     return formatted_text

# async def formatting_status_personal(
#     status: str
#     ) -> str:
#     if status == "owner":
#         text = f"🏆<b>OWNER</b>🏆"
#     elif status == "ADMIN":
#         text = f"🎩<b>ADMIN</b>🎩"
#     elif status == "User":
#         text = f"👤<b>User</b>👤"
#     elif status == "Delete":
#         text = f"❌<b>Удалён</b>❌"
#     max_length = 25
#     formatted_text = text.center(max_length)[:max_length]
#     return formatted_text

async def formatting_num_acc(
    num_acc: int
    ) -> str:
    dict_num_acc = {
        "0": " 0️⃣",
        "1": " 1️⃣",
        "2": " 2️⃣",
        "3": " 3️⃣",
        "4": " 4️⃣",
        "5": " 5️⃣",
        "6": " 6️⃣",
        "7": " 7️⃣",
        "8": " 8️⃣",
        "9": " 9️⃣",
    }
    result = ""
    for num in str(num_acc):
        result += dict_num_acc[num]
    return result

                                                                              