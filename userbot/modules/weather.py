# Copyright (C) 2020 TeamDerUntergang.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Bir bölgenin hava durumunu gösterir."""

import json
from requests import get
from datetime import datetime
from pytz import country_timezones as c_tz
from pytz import timezone as tz
from pytz import country_names as c_n

from userbot import CMD_HELP, WEATHER_DEFCITY
from userbot import OPEN_WEATHER_MAP_APPID as OWM_API
from userbot.events import register

# ===== CONSTANT =====
if WEATHER_DEFCITY:
    DEFCITY = WEATHER_DEFCITY
else:
    DEFCITY = None
# ====================


async def get_tz(con):
    """ Verilen ülkenin zaman dilimini alır. """
    """ @aragon12 ve @zakaryan2004'e teşekkürler. """
    for c_code in c_n:
        if con == c_n[c_code]:
            return tz(c_tz[c_code][0])
    try:
        if c_n[con]:
            return tz(c_tz[con][0])
    except KeyError:
        return


@register(outgoing=True, pattern="^.weather(?: |$)(.*)")
async def get_weather(weather):
    """ .weather komutu bir bölgenin hava durumunu OpenWeatherMap üzerinden alır. """

    if not OWM_API:
        await weather.edit(
            "`Əvvəlcə` https://openweathermap.org/ `saytından bir API key almalısan.`")
        return

    APPID = OWM_API

    if not weather.pattern_match.group(1):
        CITY = DEFCITY
        if not CITY:
            await weather.edit(
                "`WEATHER_DEFCITY dəyişkəniylənə bir şəhər həmişəlik olaraq düzəlt, ya da əmri yazarkən hansı şəhərin hava proqnozunu istədiyinidə orada yaz.`"
            )
            return
    else:
        CITY = weather.pattern_match.group(1)

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in CITY:
        newcity = CITY.split(",")
        if len(newcity[1]) == 2:
            CITY = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await weather.edit("`Səhv ölkə.`")
                return
            CITY = newcity[0].strip() + "," + countrycode.strip()

    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={APPID}'
    request = get(url)
    result = json.loads(request.text)

    if request.status_code != 200:
        await weather.edit(f"`Səhv ölkə.`")
        return

    cityname = result['name']
    curtemp = result['main']['temp']
    humidity = result['main']['humidity']
    min_temp = result['main']['temp_min']
    max_temp = result['main']['temp_max']
    desc = result['weather'][0]
    desc = desc['main']
    country = result['sys']['country']
    sunrise = result['sys']['sunrise']
    sunset = result['sys']['sunset']
    wind = result['wind']['speed']
    winddir = result['wind']['deg']

    ctimezone = tz(c_tz[country][0])
    time = datetime.now(ctimezone).strftime("%A, %I:%M %p")
    fullc_n = c_n[f"{country}"]

    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    div = (360 / len(dirs))
    funmath = int((winddir + (div / 2)) / div)
    findir = dirs[funmath % len(dirs)]
    kmph = str(wind * 3.6).split(".")
    mph = str(wind * 2.237).split(".")

    def fahrenheit(f):
        temp = str(((f - 273.15) * 9 / 5 + 32)).split(".")
        return temp[0]

    def celsius(c):
        temp = str((c - 273.15)).split(".")
        return temp[0]

    def sun(unix):
        xx = datetime.fromtimestamp(unix, tz=ctimezone).strftime("%I:%M %p")
        return xx

    await weather.edit(
        f"**İstilik:** `{celsius(curtemp)}°C | {fahrenheit(curtemp)}°F`\n"
        +
        f"**Ən az istilik:** `{celsius(min_temp)}°C | {fahrenheit(min_temp)}°F`\n"
        +
        f"**Ən yüksək istilik:** `{celsius(max_temp)}°C | {fahrenheit(max_temp)}°F`\n"
        + f"**Nəm:** `{humidity}%`\n" +
        f"**Külək sürəti:** `{kmph[0]} kmh | {mph[0]} mph, {findir}`\n" +
        f"**Gündoğuşu:** `{sun(sunrise)}`\n" +
        f"**Günbatımı:** `{sun(sunset)}`\n\n" + f"**{desc}**\n" +
        f"`{cityname}, {fullc_n}`\n" + f"`{time}`")


CMD_HELP.update({
    "weather":
    "İşlədilişi: .weather şəhər adı vəya .weather ölkə adı/ölkə kodu\
    \nBölgənin hava proqnozunu göstərir."
})
