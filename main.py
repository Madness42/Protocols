import os
import re
import json
from urllib.request import urlopen


PRIVATE_IPS = [
    "192.168.",
    "10.",
    "127.",
    "172."
]
IP_NOTATION = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


def traceroute(target):
    command = f"tracert {target}"

    print(f"Выполняется команда: {command}")
    with os.popen(command) as process:
        output = process.read()

    ips = IP_NOTATION.findall(output)
    return ips


def is_private_ip(ip):
    for prefix in PRIVATE_IPS:
        if not ip.startswith(prefix):
            continue
        if prefix == "172.":
            return 15 <= int(ip.split('.')[1]) <= 31
        return True
    return False


def data(ip):
    if is_private_ip(ip):
        return ip, "Private", "Local", "Local Network"

    try:
        with urlopen(f"https://rdap.db.ripe.net/ip/{ip}") as response:
            site = response.read().decode('utf-8')
            info = json.loads(site)

        as_number = info.get("autnum", "Unknown")
        country = info.get("country", "Unknown")
        provider = info.get("name", "Unknown")

        if as_number == "Unknown" and "entities" in info:
            as_number = info["entities"][0].get("handle", "Unknown")

        return ip, as_number, country, provider

    except Exception as ex:
        print(f"Ошибка: {ex}")
        return ip, "Error", "Unknown", "Unknown"


def result_function(ips):
    print("| №      | IP Адрес            | AS            | Страна    | Провайдер            |")
    print("|________|_____________________|_______________|___________|______________________|")

    for index, ip in enumerate(ips):
        ip, as_number, country, provider = data(ip)

        line = (
            f"| {index:<6} | {ip:<19} | {as_number:<13} | "
            f"{country:<9} | {provider:<20} |"
        )
        print(line)


def main():
    target = input("Введите IP-адрес или доменное имя: ").strip()
    print("Трассировка (займет некоторое время)")
    results = traceroute(target)
    print(f"Трассировка завершена.")
    result_function(results)


if __name__ == '__main__':
    main()
