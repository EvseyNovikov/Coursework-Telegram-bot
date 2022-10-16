import requests
import datetime
import pymysql
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

open_weather_token = "30d6ce2032c6c6ac39f5c4de0397f292"
tg_bot_token = "5481364034:AAGCjxW2Oj05qQJ67aqTJA8U573-Ckn-Chs"

con = pymysql.connect(host='stsvrnyr.beget.tech', user='stsvrnyr_kr',  password='t6Ge75gg', db='stsvrnyr_kr', autocommit=True)
cursor = con.cursor()


bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Здравствуйте! Напишите мне название города, а я пришлю сводку погоды!")


@dp.message_handler()
async def get_weather(message: types.Message):

    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        temp = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотрите в окно, не пойму что там за погода!"

        humidity = round(data["main"]["humidity"])
        pressure = round(data["main"]["pressure"])
        wind = round(data["wind"]["speed"])

        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"])

        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Погода в городе: {message.text}\nТемпература: {temp}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
              f"Продолжительность дня: {length_of_the_day}\n"
              f"***Хорошего дня!***"
              )

        cursor.execute("SELECT * FROM `WeatherData` WHERE `city` = %s", [city])
        record = cursor.fetchone()

        if record == None:
            cursor.execute("INSERT INTO `WeatherData` (`id`, `city`, `temperature`, `humidity`, `pressure`, `wind`, `length_of_the_day`) VALUES (NULL, %s, %s, %s, %s, %s, %s);", [city, temp, humidity, pressure, wind, length_of_the_day])
        else:
            record_id = record[0]
            
            if temp != record[2] or humidity != record[3]:
                cursor.execute("UPDATE `WeatherData` SET `city` = %s, `temperature` = %s, `humidity` = %s, `pressure` = %s, `wind` = %s, `length_of_the_day` = %s WHERE `WeatherData`.`id` = %s", [city, temp, humidity, pressure, wind, length_of_the_day, record_id])
                await message.reply(f"Данные о погоде в городе {message.text} обновлены")

    except KeyError as e:
        await message.reply("❌ Проверьте название города ❌")
    except:
         await message.reply("❌ В программе возникла ошибка ❌")



if __name__ == '__main__':
    executor.start_polling(dp)